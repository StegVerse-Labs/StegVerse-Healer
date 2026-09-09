from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import reusable_task_scheduler as subject  # noqa: E402


class ReusableTaskSchedulerTests(unittest.TestCase):
    def test_hourly_slot_executes_once_then_reuses_receipt(self) -> None:
        now = dt.datetime(2026, 9, 9, 9, 15, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = tmp_root / ".github"
            trigger = github_root / "scripts" / "trigger_reusable_task.py"
            trigger.parent.mkdir(parents=True)
            trigger.write_text(
                "#!/usr/bin/env python3\n"
                "import argparse,json\n"
                "from pathlib import Path\n"
                "p=argparse.ArgumentParser()\n"
                "p.add_argument('--reusable-task-id');p.add_argument('--invocation-id');p.add_argument('--parameters-json');p.add_argument('--task-id');p.add_argument('--cosv-task-vector');p.add_argument('--receipt')\n"
                "a=p.parse_args()\n"
                "Path(a.receipt).parent.mkdir(parents=True,exist_ok=True)\n"
                "Path(a.receipt).write_text(json.dumps({'schema':'stegverse.reusable-task-trigger-receipt/v1','state':'AUTOMATABLE_STEPS_EXHAUSTED','invocation_id':a.invocation_id})+'\\n')\n",
                encoding="utf-8",
            )
            schedule = tmp_root / "schedule.json"
            schedule.write_text(json.dumps({
                "schema": "stegverse.healer.reusable-task-schedule/v1",
                "tasks": [{
                    "reusable_task_id": "RT-NATIVE-EMAIL-ACTION-MONITOR-001",
                    "tracking_task_id": "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001",
                    "cosv_task_vector": "10100000100000",
                    "repository": "StegVerse-Labs/.github",
                    "enabled": True,
                    "run_hours_utc": list(range(24)),
                    "parameters": {"bounded_mailbox_scope": "github"},
                }],
            }), encoding="utf-8")

            def fresh_base_receipt(_config_path: Path) -> dict[str, object]:
                return {"schema":"stegverse.healer.sovereign_scheduler_receipt/v0.1","state":"COMPLETE"}

            with mock.patch.object(subject.base, "build_and_execute", side_effect=fresh_base_receipt), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE":"all","DISPATCH_MODE":"schedule"}, clear=False):
                first = subject.build_and_execute(tmp_root / "targets.json", schedule)
                second = subject.build_and_execute(tmp_root / "targets.json", schedule)

            self.assertEqual(first["state"], "COMPLETE")
            self.assertEqual(first["selected_reusable_tasks"], 1)
            first_row = first["reusable_task_schedule"][0]
            self.assertEqual(first_row["outcome"], "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED")
            self.assertEqual(first_row["invocation_id"], "rt-native-email-action-monitor-001-20260909T09Z")
            self.assertTrue(Path(first_row["receipt_ref"]).is_file())

            second_row = second["reusable_task_schedule"][0]
            self.assertEqual(second_row["outcome"], "ALREADY_RAN_THIS_SCHEDULE_SLOT")
            self.assertEqual(second_row["invocation_id"], first_row["invocation_id"])

    def test_config_binds_email_monitor_every_utc_hour(self) -> None:
        config = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        rows = [row for row in config["tasks"] if row["reusable_task_id"] == "RT-NATIVE-EMAIL-ACTION-MONITOR-001"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["tracking_task_id"], "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001")
        self.assertEqual(row["cosv_task_vector"], "10100000100000")
        self.assertEqual(row["run_hours_utc"], list(range(24)))
        self.assertTrue(row["enabled"])


if __name__ == "__main__":
    unittest.main()
