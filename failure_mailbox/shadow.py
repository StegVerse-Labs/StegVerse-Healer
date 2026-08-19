#!/usr/bin/env python3
"""Incremental failure-mailbox shadow processor.

The shadow processor consumes already-materialized JSONL batches. It has no mailbox
credentials, performs no mailbox mutation, and grants no repair/runtime/release
or heartbeat authority. Source-stream coverage is measured separately from parse
quality: a quarantined row still reached the intake surface, while a missing row
is a transport coverage problem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from failure_mailbox.backfill import run_backfill
from failure_mailbox.coverage_monitor import evaluate_coverage
from failure_mailbox.incident_engine import save_json

STATE_SCHEMA = "stegverse.healer.failure-mailbox-shadow-state/v0.1"
REPORT_SCHEMA = "stegverse.healer.failure-mailbox-shadow-batch/v0.1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema": STATE_SCHEMA, "batches": {}, "last_batch_id": ""}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("schema") != STATE_SCHEMA:
        raise ValueError("unsupported shadow state schema")
    if not isinstance(state.get("batches"), dict):
        raise ValueError("shadow state batches must be an object")
    return state


def run_shadow_batch(
    *,
    input_path: Path,
    ledger_path: Path,
    state_path: Path,
    batch_id: str,
    source_count: int,
    window_start: str,
    window_end: str,
    source_ref: str = "",
) -> dict[str, Any]:
    batch_id = str(batch_id).strip()
    if not batch_id:
        raise ValueError("batch_id is required")
    if source_count < 0:
        raise ValueError("source_count must be non-negative")

    batch_sha256 = _sha256(input_path)
    state = _load_state(state_path)
    prior = state["batches"].get(batch_id)
    if prior:
        if prior.get("input_sha256") != batch_sha256:
            raise ValueError("batch_id replay has conflicting input hash")
        return {
            "schema": REPORT_SCHEMA,
            "batch_id": batch_id,
            "result": "DUPLICATE_BATCH_NOOP",
            "input_sha256": batch_sha256,
            "prior_report": prior,
            "mailbox_mutated": False,
            "authority_effect": False,
            "heartbeat_effect": False,
            "package_release_effect": False,
        }

    backfill = run_backfill(input_path=input_path, ledger_path=ledger_path)
    input_rows = int(backfill["counters"]["input_rows"])
    parsed = int(backfill["counters"]["parsed_notifications"])
    quarantined = int(backfill["counters"]["quarantined"])

    coverage = evaluate_coverage(
        source_count=source_count,
        ingested_count=input_rows,
        window_start=window_start,
        window_end=window_end,
        source_ref=source_ref,
        ingestion_ref=f"shadow://{batch_id}",
    )

    report = {
        "schema": REPORT_SCHEMA,
        "batch_id": batch_id,
        "result": "PASS" if coverage["healthy"] else "COVERAGE_ACTION_REQUIRED",
        "input_sha256": batch_sha256,
        "window": {"start": window_start, "end": window_end},
        "coverage": coverage,
        "quality": {
            "input_rows": input_rows,
            "parsed_notifications": parsed,
            "quarantined": quarantined,
            "parse_success_rate": (parsed / input_rows) if input_rows else 1.0,
            "quarantine_rate": (quarantined / input_rows) if input_rows else 0.0,
        },
        "incident_summary": backfill["incident_summary"],
        "episode_summary": backfill["episode_summary"],
        "mailbox_mutated": False,
        "authority_effect": False,
        "heartbeat_effect": False,
        "package_release_effect": False,
    }

    state["batches"][batch_id] = {
        "input_sha256": batch_sha256,
        "window": report["window"],
        "source_count": source_count,
        "input_rows": input_rows,
        "parsed_notifications": parsed,
        "quarantined": quarantined,
        "coverage_state": coverage["state"],
        "result": report["result"],
    }
    state["last_batch_id"] = batch_id
    save_json(state_path, state)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--source-count", type=int, required=True)
    parser.add_argument("--window-start", required=True)
    parser.add_argument("--window-end", required=True)
    parser.add_argument("--source-ref", default="")
    args = parser.parse_args()

    report = run_shadow_batch(
        input_path=args.input,
        ledger_path=args.ledger,
        state_path=args.state,
        batch_id=args.batch_id,
        source_count=args.source_count,
        window_start=args.window_start,
        window_end=args.window_end,
        source_ref=args.source_ref,
    )
    save_json(args.report, report)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["result"] in {"PASS", "DUPLICATE_BATCH_NOOP"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
