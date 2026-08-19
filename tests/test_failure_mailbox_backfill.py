from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from failure_mailbox.backfill import run_backfill


class FailureMailboxBackfillTests(unittest.TestCase):
    def message(self, message_id: str, workflow: str, run_id: int, *, commit: str = "86971ef") -> dict:
        return {
            "id": message_id,
            "thread_id": f"t-{message_id}",
            "email_ts": "2026-07-08T01:57:38-07:00",
            "subject": f"[StegVerse-Labs/StegVerse-SCW] Run failed: {workflow} - repair-repo-alignment-check-v2 ({commit})",
            "snippet": f"{workflow}: No jobs were run",
            "body": f"{workflow}: No jobs were run\nhttps://github.com/StegVerse-Labs/StegVerse-SCW/actions/runs/{run_id}",
        }

    def test_backfill_preserves_incidents_and_builds_amplification_episode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "mail.jsonl"
            ledger = root / "ledger.json"
            rows = [
                self.message("m1", ".github/workflows/a.yml", 1001),
                self.message("m2", ".github/workflows/b.yml", 1002),
            ]
            source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            report = run_backfill(input_path=source, ledger_path=ledger)

        self.assertEqual(report["counters"]["input_rows"], 2)
        self.assertEqual(report["counters"]["parsed_notifications"], 2)
        self.assertEqual(report["counters"]["incident_created"], 2)
        self.assertEqual(report["incident_summary"]["incident_count"], 2)
        self.assertEqual(report["episode_summary"]["amplification_episode_count"], 1)
        self.assertEqual(report["episode_summary"]["largest_workflow_fanout_episode"], 2)
        self.assertFalse(report["source"]["mailbox_mutated"])
        self.assertFalse(report["authority_effect"])

    def test_duplicate_replay_is_noop_across_backfills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "mail.jsonl"
            ledger = root / "ledger.json"
            source.write_text(json.dumps(self.message("m1", "Test Readiness", 1001)) + "\n", encoding="utf-8")
            first = run_backfill(input_path=source, ledger_path=ledger)
            second = run_backfill(input_path=source, ledger_path=ledger)

        self.assertEqual(first["counters"]["incident_created"], 1)
        self.assertEqual(second["counters"]["duplicate_noop"], 1)
        self.assertEqual(second["incident_summary"]["incident_count"], 1)

    def test_unsupported_or_invalid_rows_are_quarantined(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "mail.jsonl"
            ledger = root / "ledger.json"
            source.write_text(
                "{not-json}\n" + json.dumps({"id": "x", "email_ts": "2026-01-01T00:00:00Z", "subject": "not github"}) + "\n",
                encoding="utf-8",
            )
            report = run_backfill(input_path=source, ledger_path=ledger)

        self.assertEqual(report["counters"]["input_rows"], 2)
        self.assertEqual(report["counters"]["quarantined"], 2)
        self.assertEqual(report["counters"]["parsed_notifications"], 0)
        self.assertEqual(report["quality"]["parse_success_rate"], 0.0)
        self.assertEqual(len(report["quarantine"]), 2)


if __name__ == "__main__":
    unittest.main()
