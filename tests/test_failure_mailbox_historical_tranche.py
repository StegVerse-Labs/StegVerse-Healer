from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from failure_mailbox.backfill import run_backfill

ROOT = Path(__file__).resolve().parents[1]
TRANCHE = ROOT / "failure_mailbox" / "benchmarks" / "historical-tranche-001-sanitized.jsonl"


class FailureMailboxHistoricalTrancheTests(unittest.TestCase):
    def test_sanitized_scw_tranche_preserves_incidents_and_reduces_to_episodes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = Path(temp_dir) / "ledger.json"
            report = run_backfill(input_path=TRANCHE, ledger_path=ledger)

        self.assertEqual(report["counters"]["input_rows"], 47)
        self.assertEqual(report["counters"]["parsed_notifications"], 47)
        self.assertEqual(report["counters"]["quarantined"], 0)
        self.assertEqual(report["incident_summary"]["incident_count"], 47)
        self.assertEqual(report["quality"]["notification_to_incident_ratio"], 1.0)
        self.assertEqual(report["episode_summary"]["episode_count"], 2)
        self.assertEqual(report["episode_summary"]["amplification_episode_count"], 2)
        self.assertEqual(report["episode_summary"]["largest_notification_episode"], 45)
        self.assertEqual(report["episode_summary"]["largest_workflow_fanout_episode"], 45)
        classes = report["episode_summary"]["failure_class_episode_frequency"]
        self.assertEqual(classes["NO_JOBS_RUN"], 1)
        self.assertEqual(classes["WORKFLOW_JOB_FAILURE"], 1)
        self.assertFalse(report["authority_effect"])
        self.assertFalse(report["heartbeat_effect"])
        self.assertFalse(report["source"]["mailbox_mutated"])


if __name__ == "__main__":
    unittest.main()
