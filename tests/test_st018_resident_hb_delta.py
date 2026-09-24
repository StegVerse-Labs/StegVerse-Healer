from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import hb_delta_schedule as hb
from app import sovereign_scheduler


def carrier(epoch: int) -> dict:
    return {
        "schema": hb.HB_SCHEMA,
        "role": "REGULATORY_CARRIER_REFERENCE_FRAME",
        "frequency_rule": hb.HB_FREQUENCY,
        "authority_effect": "NONE",
        "activation_state": "ACTIVE",
        "epoch": epoch,
        "generation": epoch,
        "reference_frame": f"heartbeat_epoch:{epoch}",
        "legacy_cutover": {"closed": True, "legacy_epoch": 29},
        "oscillator": {
            "period_ns": 10_000_000,
            "mechanism": "INDEPENDENT_PHASE_OSCILLATOR",
            "progression_dependency": "OSCILLATOR_ONLY",
            "sampled_reference_epoch": epoch,
            "snapshot_is_observation_only": True,
        },
    }


class TestST018ResidentHBDelta(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "control").mkdir()
        (self.root / hb.LEGACY_SOURCE).write_text(
            json.dumps({"schema": "stegverse.org-heartbeat-state/v1", "epoch": 29}), encoding="utf-8"
        )
        self.legacy_digest = hashlib.sha256((self.root / hb.LEGACY_SOURCE).read_bytes()).hexdigest()
        (self.root / hb.CUTOVER_RECEIPT).parent.mkdir(parents=True)
        (self.root / hb.CUTOVER_RECEIPT).write_text(json.dumps({
            "schema": "stegverse.heartbeat-schema-cutover-receipt/v1",
            "state": "CLOSED_MIGRATED", "legacy_state_sha256": self.legacy_digest,
            "new_carrier_schema": hb.HB_SCHEMA, "first_new_epoch": 30,
        }), encoding="utf-8")
        self.env = patch.dict(os.environ, {"STEGVERSE_HEARTBEAT_ROOT": str(self.root)}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def hb(self, epoch: int):
        value = carrier(epoch)
        value["legacy_cutover"]["legacy_state_sha256"] = self.legacy_digest
        (self.root / hb.HB_SOURCE).write_text(json.dumps(value), encoding="utf-8")

    def complete(self):
        return {"state": "COMPLETE", "receipt": {"status": "PASS"}, "outcome": "SOVEREIGN_LOCAL_RSTD_ST018_TASK_MANAGER"}

    def failed(self):
        return {"state": "BLOCKED", "receipt": None, "outcome": "RSTD_ST018_TASK_MANAGER_FAILED"}

    def test_missing_or_invalid_hb_fails_closed_without_utc_fallback(self):
        self.assertEqual(hb.plan()["state"], "BLOCKED")
        self.hb(30)
        malformed = carrier(30)
        malformed["legacy_cutover"]["legacy_state_sha256"] = self.legacy_digest
        malformed["authority_effect"] = "HB_GRANTS_AUTHORITY"
        (self.root / hb.HB_SOURCE).write_text(json.dumps(malformed), encoding="utf-8")
        self.assertEqual(hb.plan()["state"], "BLOCKED")

    def test_first_observation_executes_once_then_requires_elapsed_references(self):
        self.hb(100)
        due = hb.plan()
        self.assertEqual(due["state"], "DUE")
        recorded = hb.record(due, self.complete())
        self.assertTrue(recorded["completion"])
        self.assertEqual(hb.plan()["state"], "NOT_DUE")
        self.hb(100 + hb.PERIOD_REFS - 1)
        self.assertEqual(hb.plan()["state"], "NOT_DUE")
        self.hb(100 + hb.PERIOD_REFS)
        self.assertEqual(hb.plan()["state"], "DUE")

    def test_failed_attempts_retry_only_after_hb_delta_and_are_bounded(self):
        self.hb(200)
        due = hb.plan()
        hb.record(due, self.failed())
        self.assertEqual(hb.plan()["reason"], "RETRY_HB_DELTA_BELOW_MINIMUM")
        for i in range(1, hb.MAX_ATTEMPTS):
            self.hb(200 + i * hb.RETRY_REFS)
            self.assertEqual(hb.plan()["state"], "DUE")
            hb.record(hb.plan(), self.failed())
        self.assertEqual(hb.plan()["reason"], "RETRY_WINDOW_EXHAUSTED")
        self.hb(200 + hb.PERIOD_REFS)
        self.assertEqual(hb.plan()["reason"], "RETRY_WINDOW_RECOVERED")

    def test_restart_recovers_exact_checkpoint_and_rejects_corruption(self):
        self.hb(400)
        hb.record(hb.plan(), self.complete())
        # Simulate process restart: no in-memory state is retained by the module.
        self.assertEqual(hb.plan()["state"], "NOT_DUE")
        path = self.root / hb.CHECKPOINT
        state = json.loads(path.read_text(encoding="utf-8"))
        state["last_complete_epoch"] = 1
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assertEqual(hb.plan()["reason"], "HB_DELTA_CHECKPOINT_INVALID")

    def test_mutated_legacy_cutover_source_fails_closed(self):
        self.hb(500)
        (self.root / hb.LEGACY_SOURCE).write_text("{}", encoding="utf-8")
        self.assertEqual(hb.plan()["state"], "BLOCKED")

    def test_epoch_regression_fails_closed(self):
        self.hb(500)
        hb.record(hb.plan(), self.complete())
        self.hb(499)
        self.assertEqual(hb.plan()["reason"], "HB_EPOCH_REGRESSION")

    def test_newer_authentic_carrier_observation_during_work_is_valid(self):
        self.hb(700)
        plan = hb.plan()
        self.hb(710)
        self.assertTrue(hb.record(plan, self.complete())["completion"])
        self.assertEqual(hb.plan()["state"], "NOT_DUE")
        state = json.loads((self.root / hb.CHECKPOINT).read_text(encoding="utf-8"))
        self.assertEqual(state["last_complete_epoch"], 710)

    def test_non_st018_targets_preserve_legacy_schedule(self):
        target = {"repo": "StegVerse-Labs/TV", "run_hours_utc": [6]}
        from datetime import datetime, timezone
        self.assertFalse(sovereign_scheduler._due(target, datetime(2026, 9, 24, 5, tzinfo=timezone.utc), "schedule"))
        self.assertTrue(sovereign_scheduler._due(target, datetime(2026, 9, 24, 6, tzinfo=timezone.utc), "schedule"))

    def test_existing_scheduler_selects_st018_only_when_hb_delta_due(self):
        repo = self.root / "repo-standards"
        repo.mkdir()
        (repo / "tools").mkdir()
        (repo / "orchestration").mkdir()
        (repo / "tools/run_st018_task_manager.py").write_text("pass", encoding="utf-8")
        (repo / "orchestration/st018-task-registry.json").write_text('{"tasks":[]}', encoding="utf-8")
        (repo / "reports").mkdir()
        (repo / "reports/st018-task-execution.report.json").write_text('{"status":"PASS"}', encoding="utf-8")
        config = self.root / "targets.json"
        config.write_text(json.dumps({"targets": [{
            "repo": "StegVerse-Labs/repo-standards",
            "workflow": "st018-local-task-manager", "enabled": True,
            "schedule_basis": "resident_hb_delta",
        }]}), encoding="utf-8")
        os.environ["STEGVERSE_REPO_ROOTS_JSON"] = json.dumps({"StegVerse-Labs/repo-standards": str(repo)})
        self.hb(900)
        with patch.object(sovereign_scheduler, "_run", return_value={"returncode": 0, "stdout_tail": "", "stderr_tail": ""}):
            first = sovereign_scheduler.build_and_execute(config)
            second = sovereign_scheduler.build_and_execute(config)
        self.assertEqual(first["state"], "COMPLETE")
        self.assertEqual(first["selected_targets"], 1)
        self.assertEqual(second["selected_targets"], 0)
        self.hb(900 + hb.PERIOD_REFS)
        with patch.object(sovereign_scheduler, "_run", return_value={"returncode": 0, "stdout_tail": "", "stderr_tail": ""}):
            third = sovereign_scheduler.build_and_execute(config)
        self.assertEqual(third["selected_targets"], 1)


if __name__ == "__main__":
    unittest.main()
