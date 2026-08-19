#!/usr/bin/env python3
"""Historical GitHub-notification backfill for the Healer failure ledger.

Input is JSONL containing already-read mailbox message objects. This module has no
mailbox credentials and never mutates source mail. Unsupported messages are
quarantined in the report rather than approximated into an incident. Transport-level
notification outcomes are counted separately from semantic incident classes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from failure_mailbox.episode_analysis import build_failure_episodes, episode_summary
from failure_mailbox.github_notification_parser import parse_github_failure_message
from failure_mailbox.incident_engine import (
    build_neighbor_candidates,
    ingest_observation,
    load_ledger,
    save_json,
    summary,
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any], str]]:
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            digest = _sha256_bytes(raw.rstrip(b"\r\n"))
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                yield line_number, {"__parse_error__": str(exc)}, digest
                continue
            if not isinstance(value, dict):
                yield line_number, {"__parse_error__": "JSONL row must be an object"}, digest
                continue
            yield line_number, value, digest


def run_backfill(
    *,
    input_path: Path,
    ledger_path: Path,
    neighbor_window_seconds: int = 900,
) -> dict[str, Any]:
    ledger = load_ledger(ledger_path)
    source_bytes = input_path.read_bytes()
    counters = {
        "input_rows": 0,
        "parsed_notifications": 0,
        "incident_created": 0,
        "incident_updated": 0,
        "duplicate_noop": 0,
        "quarantined": 0,
    }
    notification_results: Counter[str] = Counter()
    quarantine: list[dict[str, Any]] = []

    for line_number, raw, row_sha256 in iter_jsonl(input_path):
        counters["input_rows"] += 1
        if "__parse_error__" in raw:
            counters["quarantined"] += 1
            quarantine.append({
                "line_number": line_number,
                "row_sha256": row_sha256,
                "reason": raw["__parse_error__"],
            })
            continue
        try:
            observation = parse_github_failure_message(raw)
            counters["parsed_notifications"] += 1
            notification_result = str(observation.get("notification_result_class") or "UNCLASSIFIED_NOTIFICATION")
            notification_results[notification_result] += 1
            result = ingest_observation(ledger, observation)
            outcome = str(result.get("result"))
            if outcome in counters:
                counters[outcome] += 1
            else:
                raise RuntimeError(f"unexpected incident ingest result: {outcome}")
        except (ValueError, RuntimeError, KeyError, TypeError) as exc:
            counters["quarantined"] += 1
            quarantine.append({
                "line_number": line_number,
                "row_sha256": row_sha256,
                "message_id": str(raw.get("id") or raw.get("message_id") or ""),
                "subject": str(raw.get("subject") or "")[:500],
                "reason": str(exc),
            })

    build_neighbor_candidates(ledger, neighbor_window_seconds)
    save_json(ledger_path, ledger)
    incident_report = summary(ledger)
    episodes = build_failure_episodes(ledger)
    episode_report = episode_summary(episodes)

    unique_messages = int(incident_report.get("observation_count", 0))
    incident_count = int(incident_report.get("incident_count", 0))
    notification_to_incident = (unique_messages / incident_count) if incident_count else 0.0
    parsed = counters["parsed_notifications"]
    quarantine_rate = (counters["quarantined"] / counters["input_rows"]) if counters["input_rows"] else 0.0

    return {
        "schema": "stegverse.healer.failure-mailbox-historical-backfill/v0.2",
        "source": {
            "path": str(input_path),
            "sha256": _sha256_bytes(source_bytes),
            "mailbox_mutated": False,
        },
        "counters": counters,
        "notification_result_frequency": dict(sorted(notification_results.items())),
        "quality": {
            "parse_success_rate": (parsed / counters["input_rows"]) if counters["input_rows"] else 0.0,
            "quarantine_rate": quarantine_rate,
            "notification_to_incident_ratio": notification_to_incident,
            "transport_outcome_separated_from_semantic_family": True,
            "causality_claimed": False,
        },
        "incident_summary": incident_report,
        "episode_summary": episode_report,
        "largest_episodes": episodes[:25],
        "quarantine": quarantine,
        "authority_effect": False,
        "heartbeat_effect": False,
        "mailbox_mutation_authority": False,
        "package_release_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--neighbor-window-seconds", type=int, default=900)
    args = parser.parse_args()
    report = run_backfill(
        input_path=args.input,
        ledger_path=args.ledger,
        neighbor_window_seconds=args.neighbor_window_seconds,
    )
    save_json(args.report, report)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
