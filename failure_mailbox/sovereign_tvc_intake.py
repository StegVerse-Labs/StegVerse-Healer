#!/usr/bin/env python3
"""Credential-neutral Healer client for the sovereign TVC mailbox runtime."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import github_notification_parser as parser  # noqa: E402
import incident_engine  # noqa: E402

DEFAULT_ENDPOINT = "http://127.0.0.1:8766/v1/mailbox-failure-observation"
SCHEMA = "stegverse.tvc.mailbox_failure_observation_request/v1"
CAPABILITY_ID = "tvc.mailbox-failure-observation.v1"
POLICY_ID = "tv.mailbox-failure-observation.v1"
CALLER = "StegVerse-Labs/StegVerse-Healer"
CONSUMER_TASK = "HEALER-GITHUB-FAILURE-MAILBOX-001"
EXPECTED_BATCH_FIELDS = {
    "id", "thread_id", "internet_message_id", "email_ts", "subject", "snippet",
    "signal_class", "severity", "account", "threshold_percent",
}
FORBIDDEN_RESPONSE_KEYS = {
    "access_token", "client_secret", "password", "private_key", "authorization",
    "STEGVERSE_MAIL_TENANT_ID", "STEGVERSE_MAIL_CLIENT_ID",
    "STEGVERSE_MAIL_CLIENT_SECRET", "STEGVERSE_MONITOR_MAILBOX",
}


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _state_dir() -> Path:
    explicit = os.getenv("HEALER_FAILURE_MAILBOX_STATE_DIR", "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()
    base = Path(os.getenv("XDG_STATE_HOME", str(Path.home() / ".local/state"))).expanduser()
    return (base / "stegverse/healer/failure-mailbox").resolve()


def validate_endpoint(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("TVC mailbox endpoint must be loopback HTTP")
    if parsed.path != "/v1/mailbox-failure-observation":
        raise ValueError("unexpected TVC mailbox endpoint path")
    return endpoint


def build_request(now: dt.datetime, *, window_minutes: int, lag_minutes: int, maximum_messages: int) -> dict[str, Any]:
    if window_minutes < 1 or window_minutes > 1440:
        raise ValueError("window_minutes_out_of_bounds")
    if lag_minutes < 0 or lag_minutes > 60:
        raise ValueError("lag_minutes_out_of_bounds")
    if maximum_messages < 1 or maximum_messages > 1000:
        raise ValueError("maximum_messages_out_of_bounds")
    end = now.astimezone(dt.timezone.utc) - dt.timedelta(minutes=lag_minutes)
    start = end - dt.timedelta(minutes=window_minutes)
    return {
        "schema": SCHEMA,
        "capability_id": CAPABILITY_ID,
        "policy_id": POLICY_ID,
        "caller_repository": CALLER,
        "consumer_task": CONSUMER_TASK,
        "window_start": _iso(start),
        "window_end": _iso(end),
        "maximum_messages": maximum_messages,
    }


def _find_forbidden_key(value: Any, path: str = "response") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in FORBIDDEN_RESPONSE_KEYS:
                return f"{path}.{key}"
            nested = _find_forbidden_key(child, f"{path}.{key}")
            if nested:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _find_forbidden_key(child, f"{path}[{index}]")
            if nested:
                return nested
    return None


def validate_response(response: dict[str, Any]) -> None:
    forbidden = _find_forbidden_key(response)
    if forbidden:
        raise ValueError(f"protected_material_returned:{forbidden}")
    if response.get("decision") != "ALLOW_OPERATION_RESULT":
        raise ValueError("TVC mailbox operation not allowed")
    manifest = response.get("manifest")
    if not isinstance(manifest, dict):
        raise ValueError("manifest_missing")
    required_false = (
        "mailbox_mutated", "credential_value_exposed", "credential_value_persisted",
        "consumer_credential_exported", "provider_message_ids_exported", "partial_materialization",
        "authority_effect",
    )
    for field in required_false:
        if manifest.get(field) is not False:
            raise ValueError(f"unsafe_manifest:{field}")
    if manifest.get("credential_authority") != "TV/TVC":
        raise ValueError("credential_authority_mismatch")
    batch = response.get("batch")
    if not isinstance(batch, list):
        raise ValueError("batch_missing")
    if int(manifest.get("materialized_count", -1)) != len(batch):
        raise ValueError("materialized_count_mismatch")
    for row in batch:
        if not isinstance(row, dict):
            raise ValueError("batch_row_not_object")
        if not set(row).issubset(EXPECTED_BATCH_FIELDS):
            raise ValueError("batch_row_field_expansion")
    use_receipt = response.get("use_receipt")
    if not isinstance(use_receipt, dict):
        raise ValueError("use_receipt_missing")
    for field in ("secret_material_returned", "secret_material_logged", "secret_material_retained", "mailbox_mutated", "consumer_credential_exported", "authority_effect"):
        if use_receipt.get(field) is not False:
            raise ValueError(f"unsafe_use_receipt:{field}")


def request_tvc(endpoint: str, payload: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    endpoint = validate_endpoint(endpoint)
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={"content-type": "application/json", "accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("TVC response must be an object")
    return value


def consume_response(response: dict[str, Any], state_dir: Path) -> dict[str, Any]:
    validate_response(response)
    state_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = state_dir / "github-operational-failure-ledger.json"
    summary_path = state_dir / "github-operational-failure-summary.json"
    manifest_path = state_dir / "last-tvc-mailbox-manifest.json"
    grant_path = state_dir / "last-tvc-mailbox-grant.json"
    ledger = incident_engine.load_ledger(ledger_path)
    results = []
    for row in response["batch"]:
        observation = parser.parse_github_failure_message(row)
        results.append(incident_engine.ingest_observation(ledger, observation))
    incident_engine.build_neighbor_candidates(ledger)
    incident_engine.save_json(ledger_path, ledger)
    summary = incident_engine.summary(ledger)
    incident_engine.save_json(summary_path, summary)
    incident_engine.save_json(manifest_path, response["manifest"])
    incident_engine.save_json(grant_path, response["grant_receipt"])
    return {
        "state": "COMPLETE",
        "materialized_count": response["manifest"]["materialized_count"],
        "signal_counts": response["manifest"].get("signal_counts", {}),
        "incident_results": results,
        "open_incidents": summary["open_incidents"],
        "credential_authority": "TV/TVC",
        "credential_value_received": False,
        "mailbox_mutated": False,
        "authority_effect": False,
        "state_dir": str(state_dir),
    }


def main() -> int:
    parser_cli = argparse.ArgumentParser(description="Consume the local TVC sanitized GitHub operational-failure mailbox boundary.")
    parser_cli.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser_cli.add_argument("--window-minutes", type=int, default=20)
    parser_cli.add_argument("--lag-minutes", type=int, default=2)
    parser_cli.add_argument("--maximum-messages", type=int, default=1000)
    parser_cli.add_argument("--state-dir", type=Path, default=_state_dir())
    args = parser_cli.parse_args()
    payload = build_request(
        dt.datetime.now(dt.timezone.utc),
        window_minutes=args.window_minutes,
        lag_minutes=args.lag_minutes,
        maximum_messages=args.maximum_messages,
    )
    try:
        response = request_tvc(args.endpoint, payload)
        result = consume_response(response, args.state_dir.expanduser().resolve())
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({
            "state": "BLOCKED",
            "reason": str(exc),
            "credential_authority": "TV/TVC",
            "credential_value_received": False,
            "mailbox_mutated": False,
            "authority_effect": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
