from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from failure_mailbox.backfill import run_backfill
from failure_mailbox.coverage_monitor import evaluate_coverage

ROOT = Path(__file__).resolve().parents[1]
WINDOW = ROOT / "failure_mailbox" / "benchmarks" / "historical-recent-window-002-sanitized.jsonl"


class FailureMailboxRecentWindowTests(unittest.TestCase):
    def test_recent_window_reconstructs_recurrence_without_cross_repo_collapse(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = Path(temp_dir) / "ledger.json"
            report = run_backfill(input_path=WINDOW, ledger_path=ledger)

        self.assertEqual(report["counters"]["input_rows"], 24)
        self.assertEqual(report["counters"]["parsed_notifications"], 24)
        self.assertEqual(report["counters"]["quarantined"], 0)
        self.assertEqual(report["incident_summary"]["observation_count"], 24)
        self.assertEqual(report["incident_summary"]["incident_count"], 15)

        repo_frequency = report["incident_summary"]["repository_incident_frequency"]
        self.assertEqual(repo_frequency["StegVerse-Labs/StegVerse-Healer"], 1)
        self.assertEqual(repo_frequency["master-records/orchestration"], 3)
        self.assertEqual(repo_frequency["StegVerse-Labs/Ecosystem-Delegation"], 3)
        self.assertEqual(repo_frequency["GCAT-BCAT-Engine/Publisher"], 2)
        self.assertEqual(repo_frequency["Admissible-Existence/RTG"], 2)
        self.assertEqual(len(repo_frequency), 9)

        repeated = report["incident_summary"]["repeated_incidents"]
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]["occurrence_count"], 10)

        coverage = evaluate_coverage(
            source_count=24,
            ingested_count=report["counters"]["parsed_notifications"],
            window_start="2026-08-18T19:00:00-07:00",
            window_end="2026-08-18T19:20:00-07:00",
            source_ref="benchmark://recent-window/source",
            ingestion_ref="benchmark://recent-window/backfill",
        )
        self.assertEqual(coverage["state"], "COMPLETE_COVERAGE")
        self.assertFalse(report["quality"]["causality_claimed"])
        self.assertFalse(report["authority_effect"])
        self.assertFalse(report["heartbeat_effect"])
        self.assertFalse(report["source"]["mailbox_mutated"])


if __name__ == "__main__":
    unittest.main()
