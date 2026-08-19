from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from failure_mailbox.backfill import run_backfill
from failure_mailbox.dependency_analysis import build_dependency_candidates, dependency_candidate_summary
from failure_mailbox.episode_analysis import build_failure_episodes
from failure_mailbox.incident_engine import load_ledger

ROOT = Path(__file__).resolve().parents[1]
TRANCHE = ROOT / "failure_mailbox" / "benchmarks" / "historical-multirepo-window-001-sanitized.jsonl"
GRAPH = ROOT / "failure_mailbox" / "dependency_edges.json"


class FailureMailboxMultiRepoWindowTests(unittest.TestCase):
    def test_bounded_window_separates_transport_semantics_and_dependency_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger_path = Path(temp_dir) / "ledger.json"
            report = run_backfill(input_path=TRANCHE, ledger_path=ledger_path)
            ledger = load_ledger(ledger_path)

        self.assertEqual(report["counters"]["input_rows"], 21)
        self.assertEqual(report["counters"]["parsed_notifications"], 21)
        self.assertEqual(report["counters"]["quarantined"], 0)
        self.assertEqual(report["notification_result_frequency"]["WORKFLOW_JOB_FAILURE"], 21)
        self.assertEqual(report["incident_summary"]["incident_count"], 7)
        self.assertEqual(report["episode_summary"]["episode_count"], 13)
        self.assertEqual(report["episode_summary"]["amplification_episode_count"], 6)
        self.assertEqual(report["incident_summary"]["failure_family_incident_frequency"]["CONTINUITY_FAILURE"], 1)
        self.assertEqual(report["incident_summary"]["failure_family_incident_frequency"]["UNKNOWN_FAILURE"], 6)

        episodes = build_failure_episodes(ledger)
        graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        candidates = build_dependency_candidates(episodes, graph, window_seconds=900)
        summary = dependency_candidate_summary(candidates)

        self.assertEqual(summary["candidate_count"], 11)
        self.assertEqual(summary["direction_matching_count"], 6)
        self.assertEqual(summary["direction_opposing_count"], 5)
        self.assertTrue(all(row["causality_claimed"] is False for row in candidates))

        site_to_publisher = [row for row in candidates if row["source_repository"] == "StegVerse-Labs/Site"]
        publisher_to_wiki = [row for row in candidates if row["source_repository"] == "GCAT-BCAT-Engine/Publisher"]
        self.assertEqual(len(site_to_publisher), 6)
        self.assertTrue(all("observed_order_matches_declared_direction" in row["reasons"] for row in site_to_publisher))
        self.assertEqual(len(publisher_to_wiki), 5)
        self.assertTrue(all("observed_order_opposes_declared_direction" in row["reasons"] for row in publisher_to_wiki))

        self.assertFalse(report["authority_effect"])
        self.assertFalse(report["heartbeat_effect"])
        self.assertFalse(report["source"]["mailbox_mutated"])


if __name__ == "__main__":
    unittest.main()
