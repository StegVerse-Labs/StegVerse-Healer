#!/usr/bin/env python3
"""Dependency-aware candidate analysis for cross-repository failure episodes.

This layer consumes already-built failure episodes plus declared repository edges.
It may increase confidence that two temporally adjacent failures are structurally
related, but it never asserts causality or grants repair/execution authority.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _stamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _edge_index(graph: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("source") or "").strip()
        target = str(edge.get("target") or "").strip()
        if source and target:
            index[(source, target)] = edge
    return index


def build_dependency_candidates(
    episodes: list[dict[str, Any]],
    graph: dict[str, Any],
    *,
    window_seconds: int = 900,
) -> list[dict[str, Any]]:
    edges = _edge_index(graph)
    candidates: list[dict[str, Any]] = []
    for source_episode in episodes:
        source_repo = str(source_episode.get("repository") or "")
        source_time = _stamp(source_episode.get("first_seen"))
        if source_time is None:
            continue
        for target_episode in episodes:
            if source_episode is target_episode:
                continue
            target_repo = str(target_episode.get("repository") or "")
            edge = edges.get((source_repo, target_repo))
            if edge is None:
                continue
            target_time = _stamp(target_episode.get("first_seen"))
            if target_time is None:
                continue
            delta = (target_time - source_time).total_seconds()
            absolute_delta = abs(delta)
            if absolute_delta > window_seconds:
                continue

            score = 3
            reasons = ["declared_dependency_edge", "temporal_proximity"]
            if delta >= 0:
                score += 1
                reasons.append("observed_order_matches_declared_direction")
            else:
                reasons.append("observed_order_opposes_declared_direction")
            if source_episode.get("failure_class") == target_episode.get("failure_class"):
                score += 1
                reasons.append("same_semantic_failure_family")

            candidates.append({
                "source_episode_id": source_episode.get("episode_id"),
                "source_repository": source_repo,
                "target_episode_id": target_episode.get("episode_id"),
                "target_repository": target_repo,
                "relationship": edge.get("relationship"),
                "authority_ref": edge.get("authority_ref"),
                "delta_seconds": int(delta),
                "absolute_delta_seconds": int(absolute_delta),
                "score": score,
                "reasons": reasons,
                "causality_claimed": False,
                "authority_effect": False,
                "heartbeat_effect": False,
            })
    candidates.sort(key=lambda row: (-int(row["score"]), int(row["absolute_delta_seconds"]), str(row["source_episode_id"]), str(row["target_episode_id"])))
    return candidates


def dependency_candidate_summary(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "stegverse.healer.failure-dependency-candidate-summary/v0.1",
        "candidate_count": len(candidates),
        "direction_matching_count": sum("observed_order_matches_declared_direction" in row.get("reasons", []) for row in candidates),
        "direction_opposing_count": sum("observed_order_opposes_declared_direction" in row.get("reasons", []) for row in candidates),
        "highest_score": max((int(row.get("score", 0)) for row in candidates), default=0),
        "causality_claimed": False,
        "authority_effect": False,
        "heartbeat_effect": False,
    }
