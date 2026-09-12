#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from app.ece_periodic_evaluation import execute_periodic_ece


def _persist_cycle(receipt_path: Path, result: dict) -> None:
    receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bind_site_materialization(result: dict, roots: dict[str, Path], runtime_root: Path) -> dict:
    """Optionally copy the exact Site-safe projection into an already-bound served Site root.

    Absence of a served-root binding is not an ECE failure: diagnostic/evaluation/custody
    may complete while public materialization remains unobserved. Once a served root is
    explicitly bound, however, materialization fails closed on any receipt/hash/authority
    error rather than silently presenting stale state.
    """
    if result.get("state") != "COMPLETE":
        return result

    output_root = runtime_root.expanduser().resolve() / "receipts" / "ecosystem-continuity"
    cycle_receipt = output_root / "cycle.latest.json"
    if not cycle_receipt.is_file():
        return {"state":"BLOCKED","outcome":"ECE_CYCLE_RECEIPT_MISSING_BEFORE_SITE_MATERIALIZATION","authority_effect":"NONE"}

    served_raw = os.getenv("STEGVERSE_SITE_SERVED_ROOT", "").strip()
    if not served_raw:
        result["site_materialization_state"] = "NOT_BOUND"
        result["site_live_publication_observed"] = False
        _persist_cycle(cycle_receipt, result)
        return result

    site_root = roots.get("StegVerse-Labs/Site")
    if site_root is None:
        return {"state":"BLOCKED","outcome":"ECE_SITE_LOCAL_SOURCE_MISSING_FOR_MATERIALIZER","authority_effect":"NONE"}
    materializer = site_root / "scripts" / "materialize_ecosystem_continuity_current.py"
    if not materializer.is_file():
        return {"state":"BLOCKED","outcome":"ECE_SITE_MATERIALIZER_SOURCE_MISSING","authority_effect":"NONE"}

    projection_ref = result.get("site_projection_ref")
    projection_sha = result.get("site_projection_sha256")
    if not isinstance(projection_ref, str) or not projection_ref or not isinstance(projection_sha, str) or len(projection_sha) != 64:
        return {"state":"BLOCKED","outcome":"ECE_SITE_PROJECTION_BINDING_INVALID","authority_effect":"NONE"}

    materialization_receipt = output_root / "site-materialization.latest.json"
    command = [
        sys.executable, str(materializer),
        "--cycle-receipt", str(cycle_receipt),
        "--projection", projection_ref,
        "--served-site-root", str(Path(served_raw).expanduser().resolve()),
        "--source-site-root", str(site_root),
        "--receipt-output", str(materialization_receipt),
    ]
    proc = subprocess.run(command, cwd=site_root, text=True, capture_output=True, check=False, timeout=120)
    result.setdefault("execution", []).append({
        "command": command,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    })
    if proc.returncode != 0 or not materialization_receipt.is_file():
        result.update({
            "state": "BLOCKED",
            "outcome": "ECE_SITE_MATERIALIZATION_FAILED",
            "site_materialization_state": "BLOCKED",
            "site_live_publication_observed": False,
        })
        _persist_cycle(cycle_receipt, result)
        return result

    try:
        receipt = json.loads(materialization_receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        result.update({"state":"BLOCKED","outcome":"ECE_SITE_MATERIALIZATION_RECEIPT_INVALID","site_materialization_state":"BLOCKED"})
        _persist_cycle(cycle_receipt, result)
        return result

    valid = (
        receipt.get("schema") == "stegverse.site-ecosystem-continuity-materialization-receipt.v1"
        and receipt.get("state") == "COMPLETE"
        and receipt.get("authority_effect") == "NONE_COPY_ONLY"
        and receipt.get("projection_sha256") == projection_sha
        and receipt.get("exact_bytes_preserved") is True
        and receipt.get("continuity_recalculated") is False
        and receipt.get("live_publication_observed") is False
        and receipt.get("recovery_verified") is False
    )
    if not valid:
        result.update({"state":"BLOCKED","outcome":"ECE_SITE_MATERIALIZATION_RECEIPT_DRIFT","site_materialization_state":"BLOCKED"})
        _persist_cycle(cycle_receipt, result)
        return result

    result.update({
        "site_materialization_state": "MATERIALIZED_PENDING_PUBLIC_OBSERVATION",
        "site_materialization_receipt_ref": str(materialization_receipt),
        "site_current_projection_ref": receipt.get("target_ref"),
        "site_current_projection_sha256": receipt.get("projection_sha256"),
        "site_live_publication_observed": False,
    })
    _persist_cycle(cycle_receipt, result)
    return result


def main() -> int:
    raw_roots = os.getenv("STEGVERSE_REPO_ROOTS_JSON", "").strip()
    raw_runtime = os.getenv("STEGVERSE_HEARTBEAT_ROOT", "").strip()
    if not raw_roots or not raw_runtime:
        print(json.dumps({"state":"BLOCKED","outcome":"ECE_RUNTIME_BINDING_MISSING","authority_effect":"NONE"}, sort_keys=True))
        return 3
    parsed = json.loads(raw_roots)
    if not isinstance(parsed, dict):
        raise SystemExit("STEGVERSE_REPO_ROOTS_JSON must be an object")
    roots = {str(repo): Path(str(path)).expanduser().resolve() for repo, path in parsed.items()}
    runtime_root = Path(raw_runtime).expanduser().resolve()
    result = execute_periodic_ece(roots, runtime_root)
    result = bind_site_materialization(result, roots, runtime_root)
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("state") == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
