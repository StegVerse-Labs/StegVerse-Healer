from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from failure_mailbox.shadow import run_shadow_batch

ROOT = Path(__file__).resolve().parents[1]
RECENT = ROOT / "failure_mailbox" / "benchmarks" / "historical-recent-window-002-sanitized.jsonl"


class FailureMailboxShadowTests(unittest.TestCase):
    def test_recent_batch_is_complete_coverage_and_incremental_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "ledger.json"
            state = root / "shadow-state.json"
            report = run_shadow_batch(
                input_path=RECENT,
                ledger_path=ledger,
                state_path=state,
                batch_id="recent-002",
                source_count=24,
                window_start="2026-08-18T19:00:00-07:00",
                window_end="2026-08-18T19:20:00-07:00",
                source_ref="benchmark://recent-window/source",
            )

            self.assertEqual(report["result"], "PASS")
            self.assertEqual(report["coverage"]["state"], "COMPLETE_COVERAGE")
            self.assertEqual(report["quality"]["input_rows"], 24)
            self.assertEqual(report["quality"]["parsed_notifications"], 24)
            self.assertEqual(report["quality"]["quarantined"], 0)
            self.assertEqual(report["incident_summary"]["incident_count"], 15)
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(persisted["last_batch_id"], "recent-002")
            self.assertEqual(persisted["batches"]["recent-002"]["coverage_state"], "COMPLETE_COVERAGE")
            self.assertFalse(report["mailbox_mutated"])
            self.assertFalse(report["authority_effect"])
            self.assertFalse(report["heartbeat_effect"])

    def test_duplicate_batch_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "ledger.json"
            state = root / "shadow-state.json"
            kwargs = dict(
                input_path=RECENT,
                ledger_path=ledger,
                state_path=state,
                batch_id="recent-002",
                source_count=24,
                window_start="2026-08-18T19:00:00-07:00",
                window_end="2026-08-18T19:20:00-07:00",
            )
            first = run_shadow_batch(**kwargs)
            ledger_before = ledger.read_bytes()
            second = run_shadow_batch(**kwargs)
            self.assertEqual(first["result"], "PASS")
            self.assertEqual(second["result"], "DUPLICATE_BATCH_NOOP")
            self.assertEqual(ledger.read_bytes(), ledger_before)

    def test_conflicting_batch_replay_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "ledger.json"
            state = root / "shadow-state.json"
            run_shadow_batch(
                input_path=RECENT,
                ledger_path=ledger,
                state_path=state,
                batch_id="recent-002",
                source_count=24,
                window_start="2026-08-18T19:00:00-07:00",
                window_end="2026-08-18T19:20:00-07:00",
            )
            other = root / "other.jsonl"
            other.write_text('{"id":"different"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                run_shadow_batch(
                    input_path=other,
                    ledger_path=ledger,
                    state_path=state,
                    batch_id="recent-002",
                    source_count=1,
                    window_start="2026-08-18T19:00:00-07:00",
                    window_end="2026-08-18T19:20:00-07:00",
                )

    def test_transport_gap_is_separate_from_parse_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "ledger.json"
            state = root / "shadow-state.json"
            report = run_shadow_batch(
                input_path=RECENT,
                ledger_path=ledger,
                state_path=state,
                batch_id="gap-probe",
                source_count=25,
                window_start="2026-08-18T19:00:00-07:00",
                window_end="2026-08-18T19:20:00-07:00",
            )
            self.assertEqual(report["coverage"]["state"], "PARTIAL_COVERAGE")
            self.assertEqual(report["coverage"]["missing_count"], 1)
            self.assertEqual(report["quality"]["parse_success_rate"], 1.0)
            self.assertEqual(report["result"], "COVERAGE_ACTION_REQUIRED")

    def test_quarantine_does_not_masquerade_as_transport_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            batch = root / "batch.jsonl"
            batch.write_text(
                '{"id":"ok","email_ts":"2026-08-18T19:00:00-07:00","subject":"[StegVerse-Labs/StegVerse-Healer] Run failed: Test Readiness - main (abcdef0)","snippet":"All jobs have failed"}\n'
                '{"id":"unsupported","email_ts":"2026-08-18T19:00:01-07:00","subject":"unsupported subject"}\n',
                encoding="utf-8",
            )
            report = run_shadow_batch(
                input_path=batch,
                ledger_path=root / "ledger.json",
                state_path=root / "shadow-state.json",
                batch_id="quarantine-probe",
                source_count=2,
                window_start="2026-08-18T19:00:00-07:00",
                window_end="2026-08-18T19:01:00-07:00",
            )
            self.assertEqual(report["coverage"]["state"], "COMPLETE_COVERAGE")
            self.assertEqual(report["quality"]["input_rows"], 2)
            self.assertEqual(report["quality"]["parsed_notifications"], 1)
            self.assertEqual(report["quality"]["quarantined"], 1)
            self.assertEqual(report["result"], "PASS")


if __name__ == "__main__":
    unittest.main()
