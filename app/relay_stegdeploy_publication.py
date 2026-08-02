#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com"
SOURCE_REPO = "StegVerse-org/LLM-adapter"
SOURCE_PATH = "receipts/stegdeploy-image-publication.json"
SOURCE_WORKFLOW = "stegdeploy-image.yml"
TARGET_REPO = "StegVerse-org/core-node-runtime-demo"
EVENT_TYPE = "stegdeploy-image-published"
STATE_PATH = Path("data/summary/stegdeploy_publication_dispatch.json")


def request_json(url: str, token: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "StegVerse-Healer",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API request failed ({exc.code}): {detail}") from exc


def load_source_receipt(token: str) -> dict[str, Any]:
    encoded = request_json(f"{API}/repos/{SOURCE_REPO}/contents/{SOURCE_PATH}?ref=main", token)
    content = encoded.get("content")
    if encoded.get("encoding") != "base64" or not isinstance(content, str):
        raise RuntimeError("source publication receipt was not returned as base64 content")
    return json.loads(base64.b64decode(content).decode("utf-8"))


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if receipt.get("schema") != "stegdeploy.image-publication.v2": blockers.append("source receipt is not v2")
    if receipt.get("state") != "PUBLISHED": blockers.append("source receipt is not PUBLISHED")
    digest = receipt.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"): blockers.append("source digest is not sha256-addressed")
    if receipt.get("consumer_pull_verified") is not True: blockers.append("source consumer pull is not verified")
    if receipt.get("repository") != SOURCE_REPO: blockers.append("source repository identity mismatch")
    if not isinstance(receipt.get("receipt_sha256"), str): blockers.append("source receipt hash missing")
    return blockers


def load_previous_state() -> dict[str, Any]:
    if not STATE_PATH.exists(): return {}
    try:
        value = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def dispatch_publication_workflow(token: str) -> None:
    request_json(f"{API}/repos/{SOURCE_REPO}/actions/workflows/{SOURCE_WORKFLOW}/dispatches", token, method="POST", payload={"ref": "main"})


def write_state(*, state: str, blockers: list[str], receipt: dict[str, Any] | None, dispatched: bool, remediation_dispatched: bool = False) -> None:
    previous = load_previous_state()
    source_commit = receipt.get("source_commit") if receipt else None
    body = {
        "schema": "stegverse.healer.stegdeploy_publication_dispatch.v2",
        "state": state,
        "source_repository": SOURCE_REPO,
        "source_path": SOURCE_PATH,
        "source_workflow": SOURCE_WORKFLOW,
        "target_repository": TARGET_REPO,
        "event_type": EVENT_TYPE,
        "observed_source_commit": source_commit,
        "observed_digest": receipt.get("digest") if receipt else None,
        "observed_receipt_sha256": receipt.get("receipt_sha256") if receipt else None,
        "last_dispatched_receipt_sha256": receipt.get("receipt_sha256") if dispatched and receipt else previous.get("last_dispatched_receipt_sha256"),
        "last_remediation_source_commit": source_commit if remediation_dispatched else previous.get("last_remediation_source_commit"),
        "blockers": blockers,
        "manual_user_action_required": False,
        "provider_execution_authorized": False,
        "custody_authorized": False,
        "deployment_authorized": False,
        "publication_authorized": False,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    token = os.environ.get("HEALER_GH_TOKEN", "").strip()
    if not token:
        write_state(state="BLOCKED", blockers=["HEALER_GH_TOKEN unavailable"], receipt=None, dispatched=False)
        return 2
    receipt = load_source_receipt(token)
    blockers = validate_receipt(receipt)
    if blockers:
        previous = load_previous_state()
        source_commit = receipt.get("source_commit")
        stale_contract = receipt.get("schema") != "stegdeploy.image-publication.v2"
        already_requested = bool(source_commit) and previous.get("last_remediation_source_commit") == source_commit
        if stale_contract and not already_requested:
            try:
                dispatch_publication_workflow(token)
            except Exception as exc:
                blockers = [*blockers, f"publication remediation dispatch failed: {exc}"]
                write_state(state="BLOCKED", blockers=blockers, receipt=receipt, dispatched=False)
                return 1
            write_state(state="REMEDIATION_DISPATCHED", blockers=blockers, receipt=receipt, dispatched=False, remediation_dispatched=True)
            return 0
        write_state(state="BLOCKED_REMEDIATION_PENDING" if stale_contract and already_requested else "BLOCKED", blockers=blockers, receipt=receipt, dispatched=False)
        return 0
    receipt_hash = receipt["receipt_sha256"]
    if load_previous_state().get("last_dispatched_receipt_sha256") == receipt_hash:
        write_state(state="NOOP_ALREADY_DISPATCHED", blockers=[], receipt=receipt, dispatched=False)
        return 0
    payload = {"event_type": EVENT_TYPE, "client_payload": {
        "repository": SOURCE_REPO,
        "schema": receipt["schema"],
        "state": receipt["state"],
        "digest": receipt["digest"],
        "consumer_pull_verified": receipt["consumer_pull_verified"],
        "receipt_sha256": receipt_hash,
        "source_commit": receipt.get("source_commit"),
    }}
    request_json(f"{API}/repos/{TARGET_REPO}/dispatches", token, method="POST", payload=payload)
    write_state(state="DISPATCHED", blockers=[], receipt=receipt, dispatched=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
