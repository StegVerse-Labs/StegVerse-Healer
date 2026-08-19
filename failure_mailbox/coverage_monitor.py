#!/usr/bin/env python3
"""Evaluate failure-intake coverage against an independently counted source stream.

The monitor is deliberately transport-neutral. It compares source-observation counts
with accepted-ingestion counts for the same bounded window and emits a typed state.
It does not mutate mail or grant runtime/repair/release authority.
"""

from __future__ import annotations

from typing import Any

VALID_STATES = {
    "COMPLETE_COVERAGE",
    "PARTIAL_COVERAGE",
    "COVERAGE_GAP",
    "NO_SOURCE_ACTIVITY",
    "INVALID_COVERAGE_EVIDENCE",
}


def evaluate_coverage(
    *,
    source_count: int,
    ingested_count: int,
    window_start: str,
    window_end: str,
    source_ref: str = "",
    ingestion_ref: str = "",
) -> dict[str, Any]:
    if source_count < 0 or ingested_count < 0:
        raise ValueError("coverage counts must be non-negative")
    if not str(window_start).strip() or not str(window_end).strip():
        raise ValueError("bounded window_start and window_end are required")

    if source_count == 0 and ingested_count == 0:
        state = "NO_SOURCE_ACTIVITY"
        ratio = 1.0
    elif ingested_count > source_count:
        state = "INVALID_COVERAGE_EVIDENCE"
        ratio = None
    elif source_count > 0 and ingested_count == 0:
        state = "COVERAGE_GAP"
        ratio = 0.0
    elif ingested_count < source_count:
        state = "PARTIAL_COVERAGE"
        ratio = ingested_count / source_count
    else:
        state = "COMPLETE_COVERAGE"
        ratio = 1.0

    return {
        "schema": "stegverse.healer.failure-mailbox-coverage/v0.1",
        "state": state,
        "window": {"start": window_start, "end": window_end},
        "source_count": source_count,
        "ingested_count": ingested_count,
        "coverage_ratio": ratio,
        "missing_count": max(source_count - ingested_count, 0),
        "source_ref": source_ref,
        "ingestion_ref": ingestion_ref,
        "healthy": state in {"COMPLETE_COVERAGE", "NO_SOURCE_ACTIVITY"},
        "action_required": state in {"PARTIAL_COVERAGE", "COVERAGE_GAP", "INVALID_COVERAGE_EVIDENCE"},
        "mailbox_mutation_authority": False,
        "authority_effect": False,
        "heartbeat_effect": False,
    }
