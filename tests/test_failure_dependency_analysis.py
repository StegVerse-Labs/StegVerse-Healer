from __future__ import annotations

import unittest

from failure_mailbox.dependency_analysis import build_dependency_candidates, dependency_candidate_summary


class FailureDependencyAnalysisTests(unittest.TestCase):
    def graph(self) -> dict:
        return {
            "edges": [
                {"source": "Org/A", "target": "Org/B", "relationship": "feeds", "authority_ref": "repo:a"},
                {"source": "Org/B", "target": "Org/C", "relationship": "feeds", "authority_ref": "repo:b"},
            ]
        }

    def test_declared_edge_and_matching_order_raise_candidate_not_causality(self) -> None:
        episodes = [
            {"episode_id": "FE-A", "repository": "Org/A", "first_seen": "2026-01-01T00:00:00Z", "failure_class": "X"},
            {"episode_id": "FE-B", "repository": "Org/B", "first_seen": "2026-01-01T00:01:00Z", "failure_class": "X"},
        ]
        rows = build_dependency_candidates(episodes, self.graph(), window_seconds=300)
        self.assertEqual(len(rows), 1)
        self.assertIn("declared_dependency_edge", rows[0]["reasons"])
        self.assertIn("observed_order_matches_declared_direction", rows[0]["reasons"])
        self.assertIn("same_semantic_failure_family", rows[0]["reasons"])
        self.assertFalse(rows[0]["causality_claimed"])

    def test_opposing_order_is_preserved_as_counterevidence(self) -> None:
        episodes = [
            {"episode_id": "FE-B", "repository": "Org/B", "first_seen": "2026-01-01T00:02:00Z", "failure_class": "Y"},
            {"episode_id": "FE-C", "repository": "Org/C", "first_seen": "2026-01-01T00:01:00Z", "failure_class": "Z"},
        ]
        rows = build_dependency_candidates(episodes, self.graph(), window_seconds=300)
        self.assertEqual(len(rows), 1)
        self.assertLess(rows[0]["delta_seconds"], 0)
        self.assertIn("observed_order_opposes_declared_direction", rows[0]["reasons"])
        summary = dependency_candidate_summary(rows)
        self.assertEqual(summary["direction_opposing_count"], 1)
        self.assertEqual(summary["direction_matching_count"], 0)
        self.assertFalse(summary["causality_claimed"])

    def test_temporal_neighbor_without_declared_edge_is_not_dependency_candidate(self) -> None:
        episodes = [
            {"episode_id": "FE-A", "repository": "Org/A", "first_seen": "2026-01-01T00:00:00Z", "failure_class": "X"},
            {"episode_id": "FE-C", "repository": "Org/C", "first_seen": "2026-01-01T00:00:01Z", "failure_class": "X"},
        ]
        self.assertEqual(build_dependency_candidates(episodes, self.graph(), window_seconds=300), [])


if __name__ == "__main__":
    unittest.main()
