from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RT_ID = "RT-CANONICAL-WORK-PORTABLE-DISPATCH-001"
GOAL = "ENTITY-AUTONOMOUS-GOVERNED-PROGRESSION-RUNTIME-ADOPTION-001"
COSV = "10100000100000"


class EntityAutonomousCanonicalWorkCarrierTests(unittest.TestCase):
    def test_goal_uses_existing_neutral_portable_dispatch_carrier(self) -> None:
        schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        rows = [
            row for row in schedule["tasks"]
            if row.get("reusable_task_id") == RT_ID
            and row.get("tracking_task_id") == GOAL
        ]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["cosv_task_vector"], COSV)
        self.assertEqual(row["repository"], "StegVerse-Labs/.github")
        self.assertTrue(row["enabled"])
        self.assertEqual(row["invocation_key"], GOAL)
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

    def test_source_refresh_precedes_autonomous_progression_goal(self) -> None:
        schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        refresh_index = next(
            i for i, row in enumerate(schedule["tasks"])
            if row.get("reusable_task_id") == "RT-SOVEREIGN-SOURCE-REFRESH-001"
        )
        goal_index = next(
            i for i, row in enumerate(schedule["tasks"])
            if row.get("reusable_task_id") == RT_ID
            and row.get("tracking_task_id") == GOAL
        )
        self.assertLess(refresh_index, goal_index)

    def test_existing_neutral_scheduler_remains_only_carrier(self) -> None:
        carrier = (ROOT / "app" / "reusable_task_scheduler.py").read_text(encoding="utf-8")
        self.assertIn('NEUTRAL_SCHEDULER_ID = "RT-REUSABLE-TASK-SCHEDULER-001"', carrier)
        self.assertIn('NEUTRAL_TRIGGER_REL = Path("scripts/trigger_reusable_task.py")', carrier)
        self.assertIn("CONSUMER_CARRIER_ONLY", carrier)
        self.assertIn("second_scheduler_created", carrier)


if __name__ == "__main__":
    unittest.main()
