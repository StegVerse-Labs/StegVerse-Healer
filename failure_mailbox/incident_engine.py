#!/usr/bin/env python3
"""Deterministic GitHub-failure incident ledger for StegVerse-Healer.

Input is a normalized JSON observation supplied by an authorized mailbox adapter.
This module contains no mailbox or GitHub credentials and performs no mailbox
mutation. Email/workflow notifications are observations, not authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL_STATES = {"RESOLVED", "UNRESOLVED"}
VALID_STATES = {
    "OPEN",
    "TRIAGED",
    "REPAIRING",
    "RETESTING",
    "UNABLE_TO_REPAIR",
    "IMPOSSIBLE_TO_REPAIR",
    "SANDBOX_REQUIRED",
    "RESOLVED",
    "UNRESOLVED",
}
SANDBOX_INPUT_STATES = {"UNABLE_TO_REPAIR", "IMPOSSIBLE_TO_REPAIR"}

FAILURE_CLASS_RULES = (
    ("MODULE_NOT_FOUND", ("modulenotfounderror", "no module named")),
    ("ROUTE_UNREACHABLE", ("route_unreachable", "blocked_route_unreachable", "route unreachable")),
    ("FAIL_CLOSED", ("fail_closed", "fail-closed", "review_required_unexpected_fail_closed")),
    ("NO_JOBS_RUN", ("no jobs were run", "no jobs ran")),
    ("IMPORT_ERROR", ("importerror", "cannot import name")),
    ("DEPENDENCY_ERROR", ("dependency", "requirements", "package")),
    ("SCHEMA_VALIDATION", ("schema", "validationerror", "schema validation")),
    ("CONTINUITY_FAILURE", ("continuation", "lineage", "predecessor")),
    ("AUTHORITY_BOUNDARY", ("authority", "credential", "permission", "forbidden")),
    ("TIMEOUT", ("timeout", "timed out")),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def classify_failure(obs: dict[str, Any]) -> str:
    explicit = _clean(obs.get("failure_class")).upper()
    if explicit:
        return explicit
    haystack = " ".join(
        _clean(obs.get(key)).lower()
        for key in ("subject", "failure_message", "annotation", "job", "workflow")
    )
    for klass, needles in FAILURE_CLASS_RULES:
        if any(needle in haystack for needle in needles):
            return klass
    return "UNKNOWN_FAILURE"


def failure_fingerprint(obs: dict[str, Any], failure_class: str) -> str:
    explicit = _clean(obs.get("failure_fingerprint"))
    if explicit:
        return explicit.lower()
    message = _clean(obs.get("failure_message") or obs.get("annotation") or obs.get("subject")).lower()
    # Strip volatile commit-like tokens while retaining the semantic error shape.
    tokens = []
    for token in message.split():
        raw = token.strip("()[]{}:;,.")
        if 7 <= len(raw) <= 40 and all(ch in "0123456789abcdef" for ch in raw):
            continue
        tokens.append(token)
    normalized = " ".join(tokens)[:500]
    if not normalized:
        normalized = failure_class.lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]


def incident_key(obs: dict[str, Any], failure_class: str, fingerprint: str) -> str:
    parts = [
        _clean(obs.get("repository")).lower(),
        _clean(obs.get("workflow")).lower(),
        _clean(obs.get("job") or obs.get("check")).lower(),
        _clean(obs.get("branch") or obs.get("pr")).lower(),
        failure_class.lower(),
        fingerprint,
    ]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def default_ledger() -> dict[str, Any]:
    return {
        "schema": "stegverse.healer.github-failure-ledger/v0.1",
        "next_inventory_number": 1,
        "incidents": {},
        "identity_index": {},
        "message_index": {},
        "updated_at": None,
    }


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_ledger()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "stegverse.healer.github-failure-ledger/v0.1":
        raise ValueError("unsupported failure ledger schema")
    return data


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_observation(raw: dict[str, Any]) -> dict[str, Any]:
    required = ("message_id", "repository", "workflow", "received_at")
    missing = [key for key in required if not _clean(raw.get(key))]
    if missing:
        raise ValueError("missing required observation fields: " + ", ".join(missing))
    failure_class = classify_failure(raw)
    fingerprint = failure_fingerprint(raw, failure_class)
    return {
        "message_id": _clean(raw["message_id"]),
        "thread_id": _clean(raw.get("thread_id")),
        "internet_message_id": _clean(raw.get("internet_message_id")),
        "repository": _clean(raw["repository"]),
        "workflow": _clean(raw["workflow"]),
        "job": _clean(raw.get("job") or raw.get("check")),
        "branch": _clean(raw.get("branch")),
        "pr": _clean(raw.get("pr")),
        "commit_sha": _clean(raw.get("commit_sha")),
        "run_id": _clean(raw.get("run_id")),
        "received_at": _clean(raw["received_at"]),
        "subject": _clean(raw.get("subject")),
        "failure_message": _clean(raw.get("failure_message") or raw.get("annotation")),
        "failure_class": failure_class,
        "failure_fingerprint": fingerprint,
        "source": _clean(raw.get("source") or "github-email"),
    }


def _new_incident_id(ledger: dict[str, Any]) -> str:
    number = int(ledger.get("next_inventory_number", 1))
    ledger["next_inventory_number"] = number + 1
    return f"GF-{number:06d}"


def ingest_observation(ledger: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    obs = normalize_observation(raw)
    message_id = obs["message_id"]
    existing_message = ledger["message_index"].get(message_id)
    if existing_message:
        return {"result": "duplicate_noop", "incident_id": existing_message, "observation": obs}

    key = incident_key(obs, obs["failure_class"], obs["failure_fingerprint"])
    incident_id = ledger["identity_index"].get(key)
    created = incident_id is None
    if created:
        incident_id = _new_incident_id(ledger)
        ledger["identity_index"][key] = incident_id
        ledger["incidents"][incident_id] = {
            "incident_id": incident_id,
            "identity_hash": key,
            "repository": obs["repository"],
            "workflow": obs["workflow"],
            "job": obs["job"],
            "branch_or_pr": obs["branch"] or obs["pr"],
            "failure_class": obs["failure_class"],
            "failure_fingerprint": obs["failure_fingerprint"],
            "state": "OPEN",
            "first_seen": obs["received_at"],
            "last_seen": obs["received_at"],
            "occurrence_count": 0,
            "message_ids": [],
            "commits": [],
            "run_ids": [],
            "observations": [],
            "repair_refs": [],
            "sandbox_refs": [],
            "resolution_evidence": [],
            "neighbor_candidates": [],
            "archive_eligible_message_ids": [],
        }

    incident = ledger["incidents"][incident_id]
    incident["occurrence_count"] += 1
    incident["last_seen"] = max(str(incident["last_seen"]), obs["received_at"])
    incident["message_ids"].append(message_id)
    if obs["commit_sha"] and obs["commit_sha"] not in incident["commits"]:
        incident["commits"].append(obs["commit_sha"])
    if obs["run_id"] and obs["run_id"] not in incident["run_ids"]:
        incident["run_ids"].append(obs["run_id"])
    incident["observations"].append(obs)
    ledger["message_index"][message_id] = incident_id
    ledger["updated_at"] = utc_now()
    return {"result": "incident_created" if created else "incident_updated", "incident_id": incident_id, "observation": obs}


def transition_incident(
    ledger: dict[str, Any], incident_id: str, state: str, *, evidence_ref: str = "", repair_ref: str = "", sandbox_ref: str = ""
) -> dict[str, Any]:
    if incident_id not in ledger["incidents"]:
        raise KeyError(f"unknown incident: {incident_id}")
    state = state.upper()
    if state not in VALID_STATES:
        raise ValueError(f"invalid incident state: {state}")
    incident = ledger["incidents"][incident_id]
    requested_state = state
    if state in SANDBOX_INPUT_STATES:
        state = "SANDBOX_REQUIRED"
        if evidence_ref:
            incident["resolution_evidence"].append({"type": requested_state, "ref": evidence_ref, "recorded_at": utc_now()})
    incident["state"] = state
    if repair_ref and repair_ref not in incident["repair_refs"]:
        incident["repair_refs"].append(repair_ref)
    if sandbox_ref and sandbox_ref not in incident["sandbox_refs"]:
        incident["sandbox_refs"].append(sandbox_ref)
    if evidence_ref and requested_state not in SANDBOX_INPUT_STATES:
        incident["resolution_evidence"].append({"type": requested_state, "ref": evidence_ref, "recorded_at": utc_now()})
    if state == "RESOLVED":
        if not incident["resolution_evidence"]:
            raise ValueError("RESOLVED requires durable evidence_ref")
        incident["archive_eligible_message_ids"] = list(dict.fromkeys(incident["message_ids"]))
    else:
        incident["archive_eligible_message_ids"] = []
    ledger["updated_at"] = utc_now()
    return {"result": "state_transitioned", "incident_id": incident_id, "state": state}


def build_neighbor_candidates(ledger: dict[str, Any], window_seconds: int = 900) -> None:
    rows: list[tuple[datetime, str, dict[str, Any]]] = []
    for incident_id, incident in ledger["incidents"].items():
        try:
            first = datetime.fromisoformat(str(incident["first_seen"]).replace("Z", "+00:00"))
        except ValueError:
            continue
        rows.append((first, incident_id, incident))
    rows.sort(key=lambda item: item[0])
    for _, incident_id, incident in rows:
        incident["neighbor_candidates"] = []
    for idx, (left_time, left_id, left) in enumerate(rows):
        for right_time, right_id, right in rows[idx + 1 :]:
            delta = (right_time - left_time).total_seconds()
            if delta > window_seconds:
                break
            if left["repository"] == right["repository"]:
                continue
            score = 1
            reasons = ["temporal_proximity"]
            if left["failure_class"] == right["failure_class"]:
                score += 2
                reasons.append("same_failure_class")
            if set(left.get("commits", [])) & set(right.get("commits", [])):
                score += 3
                reasons.append("shared_commit")
            candidate = {"incident_id": right_id, "repository": right["repository"], "delta_seconds": int(delta), "score": score, "reasons": reasons}
            left["neighbor_candidates"].append(candidate)


def summary(ledger: dict[str, Any]) -> dict[str, Any]:
    incidents = list(ledger["incidents"].values())
    failure_counts = Counter(item["failure_class"] for item in incidents)
    repo_counts = Counter(item["repository"] for item in incidents)
    occurrence_by_class: defaultdict[str, int] = defaultdict(int)
    for item in incidents:
        occurrence_by_class[item["failure_class"]] += int(item.get("occurrence_count", 0))
    archive_ids = []
    for item in incidents:
        archive_ids.extend(item.get("archive_eligible_message_ids", []))
    return {
        "schema": "stegverse.healer.github-failure-summary/v0.1",
        "generated_at": utc_now(),
        "incident_count": len(incidents),
        "observation_count": len(ledger["message_index"]),
        "open_incidents": sorted(item["incident_id"] for item in incidents if item["state"] not in TERMINAL_STATES),
        "sandbox_required_incidents": sorted(item["incident_id"] for item in incidents if item["state"] == "SANDBOX_REQUIRED"),
        "resolved_incidents": sorted(item["incident_id"] for item in incidents if item["state"] == "RESOLVED"),
        "failure_family_incident_frequency": dict(sorted(failure_counts.items())),
        "failure_family_observation_frequency": dict(sorted(occurrence_by_class.items())),
        "repository_incident_frequency": dict(sorted(repo_counts.items())),
        "repeated_incidents": sorted(
            ({"incident_id": item["incident_id"], "occurrence_count": item["occurrence_count"]} for item in incidents if int(item["occurrence_count"]) > 1),
            key=lambda row: (-row["occurrence_count"], row["incident_id"]),
        ),
        "archive_eligible_message_ids": sorted(set(archive_ids)),
        "authority_effect": False,
        "heartbeat_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--ingest", type=Path, action="append", default=[])
    parser.add_argument("--transition-incident")
    parser.add_argument("--state")
    parser.add_argument("--evidence-ref", default="")
    parser.add_argument("--repair-ref", default="")
    parser.add_argument("--sandbox-ref", default="")
    parser.add_argument("--neighbor-window-seconds", type=int, default=900)
    args = parser.parse_args()

    ledger = load_ledger(args.ledger)
    results = []
    for path in args.ingest:
        raw = json.loads(path.read_text(encoding="utf-8"))
        results.append(ingest_observation(ledger, raw))
    if args.transition_incident:
        if not args.state:
            raise ValueError("--state is required with --transition-incident")
        results.append(
            transition_incident(
                ledger,
                args.transition_incident,
                args.state,
                evidence_ref=args.evidence_ref,
                repair_ref=args.repair_ref,
                sandbox_ref=args.sandbox_ref,
            )
        )
    build_neighbor_candidates(ledger, args.neighbor_window_seconds)
    save_json(args.ledger, ledger)
    output = summary(ledger)
    if args.summary:
        save_json(args.summary, output)
    print(json.dumps({"results": results, "summary": output}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
