from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RT_ID = "RT-CANONICAL-WORK-PORTABLE-DISPATCH-001"
GOAL = "KV-CONNECTION-REVALIDATION-WORKER-001"
COSV = "50000000102000"


class KVRevalidationCanonicalWorkScheduleTests(unittest.TestCase):
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

    def test_no_duplicate_scheduler_or_runtime_parameters_are_added(self) -> None:
        schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        row = next(
            row for row in schedule["tasks"]
            if row.get("reusable_task_id") == RT_ID
            and row.get("tracking_task_id") == GOAL
        )
        self.assertEqual(set(row["parameters"]), {"only_consumer", "goal_task_id"})
        self.assertNotIn("runtime", row["parameters"])
        self.assertNotIn("scheduler", row["parameters"])
        self.assertNotIn("device", row["parameters"])


if __name__ == "__main__":
    unittest.main()
