#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from failure_mailbox.incident_engine import (
    build_neighbor_candidates,
    default_ledger,
    ingest_observation,
    summary,
    transition_incident,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "failure_mailbox" / "benchmark_fixtures.json"


def run() -> dict:
    fixture = json.loads(FIXTURES.read_text(encoding="utf-8"))
    ledger = default_ledger()
    start = time.perf_counter()

    normalized_by_message = {}
    results = []
    for observation in fixture["observations"]:
        result = ingest_observation(ledger, observation)
        normalized_by_message[observation["message_id"]] = observation
        results.append(result)

    duplicate_results = []
    for message_id in fixture.get("duplicate_replays", []):
        duplicate_results.append(ingest_observation(ledger, normalized_by_message[message_id]))

    repeated = [i for i in ledger["incidents"].values() if int(i["occurrence_count"]) > 1]
    if not repeated:
        raise AssertionError("benchmark corpus failed to create a repeated incident")

    sandbox_incident = repeated[0]["incident_id"]
    transition_incident(
        ledger,
        sandbox_incident,
        "IMPOSSIBLE_TO_REPAIR",
        evidence_ref="benchmark://worker/impossible-to-repair",
    )

    unresolved = next(i for i in ledger["incidents"].values() if i["incident_id"] != sandbox_incident)
    resolution_guard_pass = False
    try:
        transition_incident(ledger, unresolved["incident_id"], "RESOLVED")
    except ValueError:
        resolution_guard_pass = True

    transition_incident(
        ledger,
        unresolved["incident_id"],
        "RESOLVED",
        evidence_ref="benchmark://resolution/evidence",
    )

    build_neighbor_candidates(ledger, window_seconds=900)
    report = summary(ledger)
    elapsed = time.perf_counter() - start

    neighbor_count = sum(len(i.get("neighbor_candidates", [])) for i in ledger["incidents"].values())
    observation_count = report["observation_count"]
    incident_count = report["incident_count"]
    compression_ratio = observation_count / incident_count if incident_count else 0.0
    state_bytes = len(json.dumps(ledger, sort_keys=True).encode("utf-8"))
    archive_count = len(report["archive_eligible_message_ids"])

    expected = fixture["expected"]
    checks = {
        "observation_count": observation_count == expected["observation_count"],
        "incident_count": incident_count == expected["incident_count"],
        "duplicate_replay_noop": all(r["result"] == "duplicate_noop" for r in duplicate_results),
        "repeated_incident_count": len(repeated) == expected["repeated_incident_count"],
        "sandbox_routing": ledger["incidents"][sandbox_incident]["state"] == "SANDBOX_REQUIRED",
        "resolution_guard": resolution_guard_pass,
        "archive_after_evidence": archive_count > 0,
        "neighbor_candidates": neighbor_count >= expected["minimum_neighbor_candidate_count"],
    }

    return {
        "schema": "stegverse.healer.failure-mailbox-benchmark/v0.1",
        "fixture_schema": fixture["schema"],
        "result": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "metrics": {
            "input_notifications": len(fixture["observations"]),
            "unique_message_observations": observation_count,
            "distinct_incidents": incident_count,
            "notification_to_incident_ratio": compression_ratio,
            "duplicate_replays_tested": len(duplicate_results),
            "repeated_incidents": len(repeated),
            "neighbor_candidates": neighbor_count,
            "archive_eligible_messages": archive_count,
            "ledger_bytes": state_bytes,
            "elapsed_seconds": elapsed,
            "observations_per_second": observation_count / elapsed if elapsed > 0 else None,
        },
        "packaging_gate": {
            "deterministic_core_pass": all(checks.values()),
            "historical_corpus_benchmark_required": True,
            "live_incremental_benchmark_required": True,
            "package_release_allowed": False,
        },
    }


def main() -> int:
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
