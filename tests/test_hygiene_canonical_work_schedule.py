from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RT_ID = "RT-CANONICAL-WORK-PORTABLE-DISPATCH-001"
GOAL = "HYGIENE-CAUSAL-ROOTS-001"
COSV = "10100000100000"


class HygieneCanonicalWorkScheduleTests(unittest.TestCase):
    def test_hygiene_canonical_work_uses_existing_neutral_scheduler_carrier(self) -> None:
        schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        self.assertEqual(schedule["schema"], "stegverse.reusable-task-schedule/v1")
        rows = [
            row for row in schedule["tasks"]
            if row.get("reusable_task_id") == RT_ID
            and row.get("tracking_task_id") == GOAL
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["tracking_task_id"], GOAL)
        self.assertEqual(row["cosv_task_vector"], COSV)
        self.assertEqual(row["repository"], "StegVerse-Labs/.github")
        self.assertIs(row["enabled"], True)
        self.assertEqual(row["run_hours_utc"], list(range(24)))
        self.assertEqual(row["retry_interval_minutes"], 15)
        self.assertEqual(row["max_attempts_per_slot"], 4)
        self.assertEqual(
            row["parameters"],
            {
                "only_consumer": "canonical_work_coordination",
                "goal_task_id": GOAL,
            },
        )
        self.assertIn("no-second-scheduler", row["status"])

    def test_hygiene_binding_reuses_existing_neutral_trigger_and_runtime_bootstrap(self) -> None:
        carrier = (ROOT / "app" / "reusable_task_scheduler.py").read_text(encoding="utf-8")
        self.assertIn('NEUTRAL_SCHEDULER_ID = "RT-REUSABLE-TASK-SCHEDULER-001"', carrier)
        self.assertIn('NEUTRAL_TRIGGER_REL = Path("scripts/trigger_reusable_task.py")', carrier)
        self.assertIn('SOURCE_REFRESH_TASK_ID = "RT-SOVEREIGN-SOURCE-REFRESH-001"', carrier)
        self.assertIn('RUNTIME_ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"', carrier)
        self.assertIn("CONSUMER_CARRIER_ONLY", carrier)
        self.assertIn("second_scheduler_created", carrier)
        self.assertIn("second_user_operated_device_required", carrier)


if __name__ == "__main__":
    unittest.main()


class StegHealthCanonicalWorkScheduleTests(unittest.TestCase):
    def test_steghealth_kv_interlock_uses_existing_portable_dispatch_with_unique_slot_key(self) -> None:
        schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        rows = [
            row for row in schedule["tasks"]
            if row.get("reusable_task_id") == RT_ID
            and row.get("tracking_task_id") == "STEGHEALTH-KV-INTERLOCK-PRODUCTION-ENDPOINT-001"
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["cosv_task_vector"], "60000000111000")
        self.assertEqual(row["repository"], "StegVerse-Labs/.github")
        self.assertEqual(row["invocation_key"], "STEGHEALTH-KV-INTERLOCK-PRODUCTION-ENDPOINT-001")
        self.assertEqual(
            row["parameters"],
            {
                "only_consumer": "canonical_work_coordination",
                "goal_task_id": "STEGHEALTH-KV-INTERLOCK-PRODUCTION-ENDPOINT-001",
            },
        )
        self.assertIn("no-second-scheduler", row["status"])

    def test_existing_hygiene_binding_remains_present_and_distinct(self) -> None:
        schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        rows = [row for row in schedule["tasks"] if row.get("reusable_task_id") == RT_ID]
        goals = {row.get("tracking_task_id") for row in rows}
        self.assertIn("HYGIENE-CAUSAL-ROOTS-001", goals)
        self.assertIn("STEGHEALTH-KV-INTERLOCK-PRODUCTION-ENDPOINT-001", goals)
