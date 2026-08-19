#!/usr/bin/env python3
"""Aggregate failure incidents into deterministic amplification episodes.

Incidents preserve workflow/job identity. Episodes sit above incidents and group a
bounded burst by repository, branch/PR, commit and failure class so systemic fanout
can be measured without incorrectly collapsing distinct workflow failures.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from datetime import datetime
from typing import Any


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _episode_id(parts: list[str]) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"FE-{digest}"


def build_failure_episodes(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for incident in ledger.get("incidents", {}).values():
        repository = _clean(incident.get("repository"))
        context = _clean(incident.get("branch_or_pr"))
        failure_class = _clean(incident.get("failure_class")) or "UNKNOWN_FAILURE"
        commits = incident.get("commits") or [""]
        observations = incident.get("observations") or []
        for commit in commits:
            commit = _clean(commit)
            if not commit:
                continue
            key = (repository, context, commit, failure_class)
            bucket = buckets.setdefault(
                key,
                {
                    "repository": repository,
                    "context": context,
                    "commit_sha": commit,
                    "failure_class": failure_class,
                    "incident_ids": set(),
                    "workflow_names": set(),
                    "message_ids": set(),
                    "first_seen": None,
                    "last_seen": None,
                },
            )
            bucket["incident_ids"].add(_clean(incident.get("incident_id")))
            bucket["workflow_names"].add(_clean(incident.get("workflow")))
            for obs in observations:
                if _clean(obs.get("commit_sha")) != commit:
                    continue
                mid = _clean(obs.get("message_id"))
                if mid:
                    bucket["message_ids"].add(mid)
                seen = _clean(obs.get("received_at"))
                if seen:
                    try:
                        stamp = datetime.fromisoformat(seen.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    if bucket["first_seen"] is None or stamp < bucket["first_seen"]:
                        bucket["first_seen"] = stamp
                    if bucket["last_seen"] is None or stamp > bucket["last_seen"]:
                        bucket["last_seen"] = stamp

    episodes: list[dict[str, Any]] = []
    for (repository, context, commit, failure_class), bucket in buckets.items():
        incident_ids = sorted(value for value in bucket["incident_ids"] if value)
        workflows = sorted(value for value in bucket["workflow_names"] if value)
        message_ids = sorted(bucket["message_ids"])
        first = bucket["first_seen"]
        last = bucket["last_seen"]
        duration = int((last - first).total_seconds()) if first and last else 0
        notification_count = len(message_ids)
        incident_count = len(incident_ids)
        episode = {
            "episode_id": _episode_id([repository.lower(), context.lower(), commit.lower(), failure_class.lower()]),
            "repository": repository,
            "context": context,
            "commit_sha": commit,
            "failure_class": failure_class,
            "incident_ids": incident_ids,
            "workflow_names": workflows,
            "message_ids": message_ids,
            "incident_count": incident_count,
            "workflow_count": len(workflows),
            "notification_count": notification_count,
            "notification_per_incident": (notification_count / incident_count) if incident_count else 0.0,
            "duration_seconds": duration,
            "first_seen": first.isoformat() if first else None,
            "last_seen": last.isoformat() if last else None,
            "amplification_candidate": notification_count > 1 or len(workflows) > 1,
            "causality_claimed": False,
            "authority_effect": False,
            "heartbeat_effect": False,
        }
        episodes.append(episode)
    episodes.sort(key=lambda row: (-row["notification_count"], row["episode_id"]))
    return episodes


def episode_summary(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    by_class = Counter(row["failure_class"] for row in episodes)
    amplified = [row for row in episodes if row["amplification_candidate"]]
    return {
        "schema": "stegverse.healer.failure-episode-summary/v0.1",
        "episode_count": len(episodes),
        "amplification_episode_count": len(amplified),
        "failure_class_episode_frequency": dict(sorted(by_class.items())),
        "largest_notification_episode": max((row["notification_count"] for row in episodes), default=0),
        "largest_workflow_fanout_episode": max((row["workflow_count"] for row in episodes), default=0),
        "authority_effect": False,
        "heartbeat_effect": False,
    }
