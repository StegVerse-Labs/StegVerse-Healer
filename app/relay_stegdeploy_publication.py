#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_REPO = "StegVerse-org/LLM-adapter"
TARGET_REPO = "StegVerse-org/core-node-runtime-demo"
SOURCE_PATH = "receipts/stegdeploy-image-publication.json"
VALID_SOURCE_SCHEMA = "stegdeploy.image-publication.v2"
FORBIDDEN_CREDENTIALS = ("HEALER_GH_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "HEALER_PAT", "GH_STEGVERSE_AI_TOKEN")


def load_roots() -> dict[str, Path]:
    raw = os.getenv("STEGVERSE_REPO_ROOTS_JSON", "").strip()
    if not raw:
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON is required")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON must be an object")
    roots: dict[str, Path] = {}
    for repo, value in parsed.items():
        if isinstance(repo, str) and isinstance(value, str):
            path = Path(value).expanduser().resolve()
            if path.is_dir():
                roots[repo] = path
    return roots


def load_receipt(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("source receipt must be an object")
    return value


def validate_source(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if receipt.get("repository") != SOURCE_REPO:
        blockers.append("source_repository_identity_mismatch")
    if receipt.get("schema") != VALID_SOURCE_SCHEMA:
        blockers.append("source_receipt_not_v2")
    if receipt.get("state") != "PUBLISHED":
        blockers.append("source_receipt_not_published")
    digest = receipt.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        blockers.append("source_digest_not_sha256")
    if receipt.get("consumer_pull_verified") is not True:
        blockers.append("historical_consumer_pull_not_verified")
    if not isinstance(receipt.get("receipt_sha256"), str):
        blockers.append("source_receipt_hash_missing")
    return blockers


def write_state(path: Path | None, body: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    forbidden = [name for name in FORBIDDEN_CREDENTIALS if os.getenv(name)]
    if forbidden:
        print("Forbidden GitHub credential environment: " + ",".join(sorted(forbidden)), file=sys.stderr)
        return 2

    state_raw = os.getenv("HEALER_RELAY_STATE", "").strip()
    state_path = Path(state_raw).resolve() if state_raw else None
    try:
        roots = load_roots()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2

    source_root = roots.get(SOURCE_REPO)
    target_root = roots.get(TARGET_REPO)
    blockers: list[str] = []
    if source_root is None:
        blockers.append("source_repository_not_materialized")
    if target_root is None:
        blockers.append("target_repository_not_materialized")

    source: dict[str, Any] | None = None
    source_path = source_root / SOURCE_PATH if source_root else None
    if source_path and source_path.is_file():
        try:
            source = load_receipt(source_path)
            blockers.extend(validate_source(source))
        except Exception as exc:
            blockers.append(f"source_receipt_invalid:{exc}")
    elif source_root is not None:
        blockers.append("source_publication_receipt_not_materialized")

    previous_hash = os.getenv("HEALER_LAST_PUBLICATION_RECEIPT_SHA256", "").strip()
    source_hash = str(source.get("receipt_sha256")) if source else ""
    if not blockers and source_hash and previous_hash == source_hash:
        body = {
            "schema": "stegverse.healer.stegdeploy_publication_relay.v3",
            "state": "NOOP_ALREADY_VERIFIED",
            "source_repository": SOURCE_REPO,
            "target_repository": TARGET_REPO,
            "source_receipt_sha256": source_hash,
            "credential_authority": "TV/TVC",
            "github_token_required": False,
            "github_api_used": False,
            "github_dispatch_used": False,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "blockers": [],
        }
        write_state(state_path, body)
        print(json.dumps(body, sort_keys=True))
        return 0

    intake: dict[str, Any] | None = None
    if not blockers and source_path is not None and target_root is not None:
        script = target_root / "tools" / "stegdeploy_runtime_intake_local.py"
        if not script.is_file():
            blockers.append("target_local_intake_not_materialized")
        else:
            output_path = Path(os.getenv("STEGDEPLOY_RUNTIME_INTAKE_RECEIPT", "/tmp/stegdeploy-runtime-intake.latest.json")).resolve()
            env = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                "LANG": os.environ.get("LANG", "C.UTF-8"),
                "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
                "STEGDEPLOY_PUBLICATION_RECEIPT": str(source_path),
                "STEGDEPLOY_RUNTIME_INTAKE_RECEIPT": str(output_path),
            }
            proc = subprocess.run(
                [sys.executable, str(script)],
                cwd=target_root,
                env=env,
                text=True,
                capture_output=True,
                timeout=180,
                check=False,
            )
            try:
                intake = json.loads(proc.stdout.strip().splitlines()[-1])
            except Exception:
                intake = {"state": "FAILED", "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:]}
            if proc.returncode != 0 or intake.get("state") != "COMPATIBLE":
                blockers.extend(str(value) for value in intake.get("blockers", []) if value)
                if not blockers:
                    blockers.append("target_local_intake_not_compatible")

    state = "COMPLETE" if not blockers and intake and intake.get("state") == "COMPATIBLE" else "BLOCKED"
    body = {
        "schema": "stegverse.healer.stegdeploy_publication_relay.v3",
        "state": state,
        "source_repository": SOURCE_REPO,
        "source_path": SOURCE_PATH,
        "target_repository": TARGET_REPO,
        "source_receipt_sha256": source_hash or None,
        "source_digest": source.get("digest") if source else None,
        "target_intake": intake,
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "github_api_used": False,
        "github_dispatch_used": False,
        "remote_registry_pull_requested_by_relay": False,
        "blockers": sorted(set(blockers)),
        "next_executable_action": None if state == "COMPLETE" else "MATERIALIZE_REQUIRED_LOCAL_SOURCE_TARGET_AND_EXACT_IMAGE_THEN_RETRY",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_state(state_path, body)
    print(json.dumps(body, sort_keys=True))
    return 0 if state == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
