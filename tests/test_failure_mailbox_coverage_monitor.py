from __future__ import annotations

import unittest

from failure_mailbox.coverage_monitor import evaluate_coverage


class FailureMailboxCoverageMonitorTests(unittest.TestCase):
    def test_complete_coverage(self) -> None:
        result = evaluate_coverage(
            source_count=24,
            ingested_count=24,
            window_start="2026-08-18T19:00:00-07:00",
            window_end="2026-08-18T19:20:00-07:00",
            source_ref="gmail:github-notifications-window",
            ingestion_ref="failure-mailbox:shadow-ledger-window",
        )
        self.assertEqual(result["state"], "COMPLETE_COVERAGE")
        self.assertEqual(result["coverage_ratio"], 1.0)
        self.assertEqual(result["missing_count"], 0)
        self.assertTrue(result["healthy"])
        self.assertFalse(result["action_required"])

    def test_partial_coverage(self) -> None:
        result = evaluate_coverage(
            source_count=24,
            ingested_count=18,
            window_start="2026-08-18T19:00:00-07:00",
            window_end="2026-08-18T19:20:00-07:00",
        )
        self.assertEqual(result["state"], "PARTIAL_COVERAGE")
        self.assertEqual(result["coverage_ratio"], 0.75)
        self.assertEqual(result["missing_count"], 6)
        self.assertFalse(result["healthy"])
        self.assertTrue(result["action_required"])

    def test_source_activity_with_zero_intake_is_coverage_gap(self) -> None:
        result = evaluate_coverage(
            source_count=24,
            ingested_count=0,
            window_start="2026-08-18T19:00:00-07:00",
            window_end="2026-08-18T19:20:00-07:00",
            source_ref="gmail:direct-github-notification-count",
            ingestion_ref="gmail:legacy-failure-label-count",
        )
        self.assertEqual(result["state"], "COVERAGE_GAP")
        self.assertEqual(result["coverage_ratio"], 0.0)
        self.assertEqual(result["missing_count"], 24)
        self.assertFalse(result["healthy"])
        self.assertTrue(result["action_required"])
        self.assertFalse(result["mailbox_mutation_authority"])
        self.assertFalse(result["authority_effect"])
        self.assertFalse(result["heartbeat_effect"])

    def test_no_source_activity_is_not_a_gap(self) -> None:
        result = evaluate_coverage(
            source_count=0,
            ingested_count=0,
            window_start="2026-08-18T18:00:00-07:00",
            window_end="2026-08-18T18:20:00-07:00",
        )
        self.assertEqual(result["state"], "NO_SOURCE_ACTIVITY")
        self.assertEqual(result["coverage_ratio"], 1.0)
        self.assertTrue(result["healthy"])
        self.assertFalse(result["action_required"])

    def test_ingested_count_greater_than_source_is_invalid_evidence(self) -> None:
        result = evaluate_coverage(
            source_count=10,
            ingested_count=11,
            window_start="2026-08-18T19:00:00-07:00",
            window_end="2026-08-18T19:20:00-07:00",
        )
        self.assertEqual(result["state"], "INVALID_COVERAGE_EVIDENCE")
        self.assertIsNone(result["coverage_ratio"])
        self.assertFalse(result["healthy"])
        self.assertTrue(result["action_required"])

    def test_negative_counts_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_coverage(
                source_count=-1,
                ingested_count=0,
                window_start="2026-08-18T19:00:00-07:00",
                window_end="2026-08-18T19:20:00-07:00",
            )

    def test_missing_window_boundary_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_coverage(
                source_count=1,
                ingested_count=1,
                window_start="",
                window_end="2026-08-18T19:20:00-07:00",
            )


if __name__ == "__main__":
    unittest.main()
