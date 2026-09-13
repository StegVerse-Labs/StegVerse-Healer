from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "data/reusable_task_schedule.json"


class ControlPlaneSourcePackageScheduleTests(unittest.TestCase):
    def test_package_producer_reuses_neutral_scheduler_and_publication_owner(self) -> None:
        schedule = json.loads(SCHEDULE.read_text(encoding="utf-8"))
        rows = [row for row in schedule["tasks"] if row.get("reusable_task_id") == "RT-CONTROL-PLANE-SOURCE-PACKAGE-001"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["tracking_task_id"], "SITE-PUBLICATION-NATIVE-RUNTIME-EXECUTION-001")
        self.assertEqual(row["cosv_task_vector"], "50000000102000")
        self.assertEqual(row["repository"], "StegVerse-Labs/.github")
        self.assertTrue(row["enabled"])
        self.assertEqual(row["run_hours_utc"], list(range(24)))
        self.assertEqual(row["retry_interval_minutes"], 15)
        self.assertEqual(row["max_attempts_per_slot"], 4)
        self.assertEqual(row["parameters"]["transport_execution"], "none-package-production-only")
        self.assertFalse(row["parameters"]["network_source_fetch_allowed"])
        self.assertFalse(row["parameters"]["second_user_operated_device_required"])


if __name__ == "__main__":
    unittest.main()
