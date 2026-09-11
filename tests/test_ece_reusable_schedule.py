import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class EcosystemContinuityScheduleTests(unittest.TestCase):
    def test_ece_schedule_binds_parent_task_every_utc_hour(self):
        config = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        rows = [row for row in config["tasks"] if row.get("reusable_task_id") == "RT-ECOSYSTEM-CONTINUITY-EVALUATION-001"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["tracking_task_id"], "ECOSYSTEM-CONTINUITY-EVALUATOR-001")
        self.assertEqual(row["cosv_task_vector"], "71000000100111")
        self.assertEqual(row["repository"], "StegVerse-Labs/.github")
        self.assertEqual(row["run_hours_utc"], list(range(24)))
        self.assertEqual(row["retry_interval_minutes"], 15)
        self.assertEqual(row["max_attempts_per_slot"], 4)
        self.assertIn("no-second-scheduler", row["status"])


if __name__ == "__main__":
    unittest.main()
