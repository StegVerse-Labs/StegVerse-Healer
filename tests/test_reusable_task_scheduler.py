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
    def _schedule(self, path: Path) -> None:
        path.write_text(json.dumps({
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

    def _github_root(self, tmp_root: Path) -> Path:
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
            "params=json.loads(a.parameters_json)\n"
            "assert Path(params['source_root']).resolve()==Path.cwd().resolve()\n"
            "assert Path(params['runtime_root']).resolve()!=Path.cwd().resolve()\n"
            "Path(a.receipt).parent.mkdir(parents=True,exist_ok=True)\n"
            "Path(a.receipt).write_text(json.dumps({'schema':'stegverse.reusable-task-trigger-receipt/v1','state':'AUTOMATABLE_STEPS_EXHAUSTED','invocation_id':a.invocation_id,'parameters':params})+'\\n')\n",
            encoding="utf-8",
        )
        return github_root

    def _runtime_root(self, path: Path) -> Path:
        runtime_root = path
        request = runtime_root / subject.RUNTIME_REQUIRED_REL
        request.parent.mkdir(parents=True, exist_ok=True)
        request.write_text("{}\n", encoding="utf-8")
        return runtime_root

    def test_hourly_slot_executes_once_then_reuses_resident_receipt(self) -> None:
        now = dt.datetime(2026, 9, 9, 9, 15, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = self._github_root(tmp_root)
            runtime_root = self._runtime_root(tmp_root / "heartbeat-runtime")
            schedule = tmp_root / "schedule.json"
            self._schedule(schedule)

            def fresh_base_receipt(_config_path: Path) -> dict[str, object]:
                return {"schema":"stegverse.healer.sovereign_scheduler_receipt/v0.1","state":"COMPLETE"}

            with mock.patch.object(subject.base, "build_and_execute", side_effect=fresh_base_receipt), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.dict("os.environ", {
                     "RUN_SCOPE":"all",
                     "DISPATCH_MODE":"schedule",
                     "STEGVERSE_HEARTBEAT_ROOT": str(runtime_root),
                 }, clear=False):
                first = subject.build_and_execute(tmp_root / "targets.json", schedule)
                second = subject.build_and_execute(tmp_root / "targets.json", schedule)

            self.assertEqual(first["state"], "COMPLETE")
            self.assertEqual(first["selected_reusable_tasks"], 1)
            self.assertEqual(first["resident_runtime_root"], str(runtime_root.resolve()))
            self.assertEqual(first["resident_runtime_root_source"], "EXPLICIT_NONSECRET_RUNTIME_ROOT")
            first_row = first["reusable_task_schedule"][0]
            self.assertEqual(first_row["outcome"], "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED")
            self.assertEqual(first_row["invocation_id"], "rt-native-email-action-monitor-001-20260909T09Z")
            receipt = Path(first_row["receipt_ref"])
            self.assertTrue(receipt.is_file())
            self.assertTrue(str(receipt).startswith(str(runtime_root.resolve())))
            self.assertEqual(Path(first_row["source_root"]), github_root.resolve())
            self.assertEqual(Path(first_row["runtime_root"]), runtime_root.resolve())

            second_row = second["reusable_task_schedule"][0]
            self.assertEqual(second_row["outcome"], "ALREADY_RAN_THIS_SCHEDULE_SLOT")
            self.assertEqual(second_row["invocation_id"], first_row["invocation_id"])

    def test_canonical_local_runtime_discovery_without_forwarded_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            runtime_root = self._runtime_root(home / ".local" / "state" / "stegverse" / "heartbeat-runtime")
            with mock.patch.object(subject.Path, "home", return_value=home), \
                 mock.patch.dict("os.environ", {"STEGVERSE_HEARTBEAT_ROOT": ""}, clear=False):
                resolved, source = subject._resident_runtime_root()
            self.assertEqual(resolved, runtime_root.resolve())
            self.assertEqual(source, "CANONICAL_LOCAL_RUNTIME_DISCOVERY")

    def test_missing_resident_runtime_blocks_instead_of_using_source_as_runtime(self) -> None:
        now = dt.datetime(2026, 9, 9, 9, 15, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = self._github_root(tmp_root)
            schedule = tmp_root / "schedule.json"
            self._schedule(schedule)

            with mock.patch.object(subject.base, "build_and_execute", return_value={"schema":"stegverse.healer.sovereign_scheduler_receipt/v0.1","state":"COMPLETE"}), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.object(subject.Path, "home", return_value=tmp_root / "no-home-runtime"), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE":"all","DISPATCH_MODE":"schedule","STEGVERSE_HEARTBEAT_ROOT":""}, clear=False):
                result = subject.build_and_execute(tmp_root / "targets.json", schedule)

            self.assertEqual(result["state"], "BLOCKED")
            row = result["reusable_task_schedule"][0]
            self.assertEqual(row["outcome"], "RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED")
            self.assertIsNone(result["resident_runtime_root"])
            self.assertEqual(result["resident_runtime_root_source"], "CANONICAL_RUNTIME_NOT_FOUND")

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
