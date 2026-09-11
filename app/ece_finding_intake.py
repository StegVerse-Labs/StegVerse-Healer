#!/usr/bin/env python3
"""Read-only intake for canonical Ecosystem Continuity Evaluator findings.

This module prepares actionable findings for existing Healer dispatch semantics. It
never changes the underlying ECE observation, marks recovery, or grants execution
authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EVALUATION_SCHEMA = "stegverse.ecosystem-continuity-evaluation.v1"
INTAKE_SCHEMA = "stegverse.healer-ece-finding-intake.v1"
ALLOWED_REMEDIATION = {
    "NONE", "AUTO_REMEDIABLE", "DISPATCHABLE", "AUTHORITY_BOUNDARY", "HUMAN_BOUNDARY"
}


def _canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def ingest(evaluation: dict) -> dict:
    if evaluation.get("schema") != EVALUATION_SCHEMA:
        raise ValueError("INVALID_ECE_SCHEMA")
    if evaluation.get("authority_effect") != "NONE_DIAGNOSTIC_ONLY":
        raise ValueError("ECE_AUTHORITY_EFFECT_REJECTED")
    evaluation_id = evaluation.get("evaluation_id")
    if not evaluation_id:
        raise ValueError("MISSING_EVALUATION_ID")

    items = []
    for finding in evaluation.get("findings", []):
        if finding.get("observation_state") == "PASS":
            continue
        remediation_class = finding.get("remediation_class")
        if remediation_class not in ALLOWED_REMEDIATION:
            raise ValueError("INVALID_REMEDIATION_CLASS")
        snapshot = {
            "finding_id": finding.get("finding_id"),
            "evaluation_id": evaluation_id,
            "component_id": finding.get("component_id"),
            "predicate_id": finding.get("predicate_id"),
            "observation_state": finding.get("observation_state"),
            "severity": finding.get("severity"),
            "continuity_critical": finding.get("continuity_critical"),
            "evidence": list(finding.get("evidence", [])),
            "evidence_age_seconds": finding.get("evidence_age_seconds"),
            "authority_owner": finding.get("authority_owner"),
            "remediation_class": remediation_class,
        }
        items.append({
            "finding_snapshot": snapshot,
            "finding_snapshot_sha256": hashlib.sha256(_canonical_bytes(snapshot)).hexdigest(),
            "healer_state": "DETECTED",
            "recovery_verified": False,
            "dispatch_authority_effect": "NONE_INTAKE_ONLY",
        })

    return {
        "schema": INTAKE_SCHEMA,
        "source_evaluation_id": evaluation_id,
        "source_continuity_state": evaluation.get("continuity_state"),
        "items": items,
        "authority_effect": "NONE_INTAKE_ONLY",
        "recovery_rule": "LATER_INDEPENDENT_ECE_PASS_REQUIRED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    evaluation = json.loads(Path(args.input).read_text())
    result = ingest(evaluation)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
