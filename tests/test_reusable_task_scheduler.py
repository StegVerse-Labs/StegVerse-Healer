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
            "schema": "stegverse.reusable-task-schedule/v1",
            "tasks": [{
                "reusable_task_id": "RT-NATIVE-EMAIL-ACTION-MONITOR-001",
                "tracking_task_id": "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001",
                "cosv_task_vector": "10100000100000",
                "repository": "StegVerse-Labs/.github",
                "enabled": True,
                "run_hours_utc": list(range(24)),
                "retry_interval_minutes": 15,
                "max_attempts_per_slot": 4,
                "parameters": {"bounded_mailbox_scope": "github"},
            }],
        }), encoding="utf-8")

    def _schedule_with_source_refresh(self, path: Path) -> None:
        path.write_text(json.dumps({
            "schema": "stegverse.reusable-task-schedule/v1",
            "tasks": [
                {
                    "reusable_task_id": "RT-SOVEREIGN-SOURCE-REFRESH-001",
                    "tracking_task_id": "SOVEREIGN-SOURCE-REFRESH-001",
                    "cosv_task_vector": "40000100100000",
                    "repository": "StegVerse-Labs/.github",
                    "enabled": True,
                    "run_hours_utc": list(range(24)),
                    "retry_interval_minutes": 15,
                    "max_attempts_per_slot": 4,
                    "parameters": {},
                },
                {
                    "reusable_task_id": "RT-STEGBROWSER-RUNTIME-CONSUMPTION-001",
                    "tracking_task_id": "STEG-BROWSER-RUNTIME-CONSUMPTION-001",
                    "cosv_task_vector": "40000100100000",
                    "repository": "StegVerse-Labs/.github",
                    "enabled": True,
                    "run_hours_utc": list(range(24)),
                    "retry_interval_minutes": 15,
                    "max_attempts_per_slot": 4,
                    "parameters": {},
                },
            ],
        }), encoding="utf-8")

    def _github_root(self, tmp_root: Path) -> Path:
        github_root = tmp_root / ".github"
        trigger = github_root / "scripts" / "trigger_reusable_task.py"
        trigger.parent.mkdir(parents=True)
        trigger.write_text("# neutral reusable trigger\n", encoding="utf-8")
        return github_root

    def _runtime_root(self, path: Path, marker: Path | None = None) -> Path:
        request = path / (marker or subject.RUNTIME_REQUIRED_REL)
        request.parent.mkdir(parents=True, exist_ok=True)
        request.write_text("{}\n", encoding="utf-8")
        return path

    def test_healer_delegates_reusable_schedule_to_neutral_scheduler(self) -> None:
        now = dt.datetime(2026, 9, 13, 20, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = self._github_root(tmp_root)
            runtime_root = self._runtime_root(tmp_root / "heartbeat-runtime")
            schedule = tmp_root / "schedule.json"
            self._schedule(schedule)

            def fake_run(command, cwd, env, timeout):
                self.assertEqual(command[command.index("--reusable-task-id") + 1], subject.NEUTRAL_SCHEDULER_ID)
                receipt = Path(command[command.index("--receipt") + 1])
                invocation = command[command.index("--invocation-id") + 1]
                result = receipt.with_name(f"{invocation}.runner-result.json")
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_text(json.dumps({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) + "\n")
                result.write_text(json.dumps({
                    "schema": "stegverse.reusable-task-runner-result/v1",
                    "due_task_count": 1,
                    "outcomes": [{
                        "reusable_task_id": "RT-NATIVE-EMAIL-ACTION-MONITOR-001",
                        "state": "BOUNDARY_RECORDED",
                        "child_receipt_state": "BOUNDARY_RECORDED",
                        "slot_satisfied": False,
                    }],
                }) + "\n")
                return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

            with mock.patch.object(subject.base, "build_and_execute", return_value={"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "COMPLETE"}), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.object(subject.base, "_run", side_effect=fake_run), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE": "all", "STEGVERSE_HEARTBEAT_ROOT": str(runtime_root)}, clear=False):
                result = subject.build_and_execute(tmp_root / "targets.json", schedule)

            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["reusable_task_scheduler_owner"], "RT-REUSABLE-TASK-SCHEDULER-001")
            self.assertEqual(result["healer_scheduler_role"], "CONSUMER_CARRIER_ONLY")
            self.assertEqual(result["reusable_task_schedule_schema"], "stegverse.reusable-task-schedule/v1")
            self.assertEqual(result["selected_reusable_tasks"], 1)
            self.assertEqual(result["reusable_task_schedule"][0]["state"], "BOUNDARY_RECORDED")
            self.assertEqual(result["neutral_reusable_task_scheduler"]["state"], "DELEGATED")
            observation = result["resident_custody_root_observation"]
            self.assertEqual(observation["schema"], "stegverse.healer.resident-custody-root-observation/v1")
            self.assertEqual(observation["task_id"], "STEG-BROWSER-RESIDENT-CUSTODY-ROOT-OBSERVATION-001")
            self.assertEqual(observation["cosv_task_vector"], "40000100100000")
            self.assertEqual(observation["state"], "RESIDENT_CUSTODY_ROOT_OBSERVED")
            self.assertEqual(observation["github_runtime_authority"], "NONE")
            self.assertEqual(observation["credential_authority"], "TV/TVC")
            self.assertFalse(observation["runtime_completion_claimed"])
            self.assertFalse(observation["second_scheduler_created"])
            self.assertFalse(observation["second_user_operated_device_required"])
            self.assertIn(str(subject.RUNTIME_REQUIRED_REL), observation["matched_marker_relative_paths"])
            retention = result["resident_custody_root_observation_retention"]
            self.assertEqual(retention["state"], "RETAINED")
            self.assertEqual(retention["packet_relative_path"], str(subject.ROOT_OBSERVATION_RECEIPT_REL))
            self.assertEqual(retention["packet_state"], "RESIDENT_CUSTODY_ROOT_OBSERVED")
            self.assertEqual(retention["github_runtime_authority"], "NONE")
            packet_path = Path(retention["packet_ref"])
            retained_packet = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(retained_packet["state"], "RESIDENT_CUSTODY_ROOT_OBSERVED")
            self.assertEqual(retained_packet["retention_authority_effect"], "NONE_RETENTION_ONLY")
            self.assertFalse(retained_packet["runtime_completion_claimed"])
            self.assertFalse(retained_packet["request_consumption_claimed"])

    def test_retains_not_observed_packet_to_materialization_target_without_runtime_claim(self) -> None:
        now = dt.datetime(2026, 9, 13, 20, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = self._github_root(tmp_root)
            schedule = tmp_root / "schedule.json"
            self._schedule_with_source_refresh(schedule)

            def fake_run(command, cwd, env, timeout):
                receipt = Path(command[command.index("--receipt") + 1])
                invocation = command[command.index("--invocation-id") + 1]
                result = receipt.with_name(f"{invocation}.runner-result.json")
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_text(json.dumps({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) + "\n")
                result.write_text(json.dumps({
                    "schema": "stegverse.reusable-task-runner-result/v1",
                    "due_task_count": 0,
                    "outcomes": [],
                }) + "\n")
                return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

            with mock.patch.object(subject.base, "build_and_execute", return_value={"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "COMPLETE"}), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.object(subject.base, "_run", side_effect=fake_run), \
                 mock.patch.object(subject.Path, "home", return_value=tmp_root / "home"), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE": "all", "STEGVERSE_HEARTBEAT_ROOT": ""}, clear=False):
                result = subject.build_and_execute(tmp_root / "targets.json", schedule)

            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["resident_custody_root_observation"]["state"], "RESIDENT_CUSTODY_ROOT_NOT_OBSERVED")
            retention = result["resident_custody_root_observation_retention"]
            self.assertEqual(retention["state"], "RETAINED")
            self.assertEqual(retention["packet_state"], "RESIDENT_CUSTODY_ROOT_NOT_OBSERVED")
            self.assertEqual(retention["retained_under_root_source"], "CANONICAL_LOCAL_RUNTIME_MATERIALIZATION_TARGET")
            packet = json.loads(Path(retention["packet_ref"]).read_text(encoding="utf-8"))
            self.assertEqual(packet["state"], "RESIDENT_CUSTODY_ROOT_NOT_OBSERVED")
            self.assertEqual(packet["task_id"], "STEG-BROWSER-RESIDENT-CUSTODY-ROOT-OBSERVATION-001")
            self.assertEqual(packet["cosv_task_vector"], "40000100100000")
            self.assertEqual(packet["retained_under_root_source"], "CANONICAL_LOCAL_RUNTIME_MATERIALIZATION_TARGET")
            self.assertFalse(packet["runtime_completion_claimed"])
            self.assertFalse(packet["request_consumption_claimed"])

    def test_canonical_local_runtime_discovery_without_forwarded_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            runtime_root = self._runtime_root(home / ".local" / "state" / "stegverse" / "heartbeat-runtime")
            with mock.patch.object(subject.Path, "home", return_value=home), \
                 mock.patch.dict("os.environ", {"STEGVERSE_HEARTBEAT_ROOT": ""}, clear=False):
                resolved, source = subject._resident_runtime_root()
            self.assertEqual(resolved, runtime_root.resolve())
            self.assertEqual(source, "CANONICAL_LOCAL_RUNTIME_DISCOVERY")

    def test_runtime_discovery_accepts_stegbrowser_resident_request_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            marker = Path("control/resident-execution-request.d/canonical-work-stegbrowser-runtime-consumption-001.json")
            runtime_root = self._runtime_root(home / ".local" / "state" / "stegverse" / "heartbeat-runtime", marker)
            with mock.patch.object(subject.Path, "home", return_value=home), \
                 mock.patch.dict("os.environ", {"STEGVERSE_HEARTBEAT_ROOT": ""}, clear=False):
                resolved, source = subject._resident_runtime_root()
            self.assertEqual(resolved, runtime_root.resolve())
            self.assertEqual(source, "CANONICAL_LOCAL_RUNTIME_DISCOVERY")

    def test_missing_resident_runtime_records_neutral_scheduler_boundary(self) -> None:
        now = dt.datetime(2026, 9, 13, 20, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = self._github_root(tmp_root)
            schedule = tmp_root / "schedule.json"
            self._schedule(schedule)
            with mock.patch.object(subject.base, "build_and_execute", return_value={"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "COMPLETE"}), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.object(subject.Path, "home", return_value=tmp_root / "no-home-runtime"), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE": "all", "STEGVERSE_HEARTBEAT_ROOT": ""}, clear=False):
                result = subject.build_and_execute(tmp_root / "targets.json", schedule)
            self.assertEqual(result["state"], "BLOCKED")
            delegation = result["neutral_reusable_task_scheduler"]
            self.assertEqual(delegation["boundary"], "RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED")
            self.assertIsNone(result["resident_runtime_root"])
            observation = result["resident_custody_root_observation"]
            self.assertEqual(observation["state"], "RESIDENT_CUSTODY_ROOT_NOT_OBSERVED")
            self.assertEqual(observation["task_id"], "STEG-BROWSER-RESIDENT-CUSTODY-ROOT-OBSERVATION-001")
            self.assertEqual(observation["authority_effect"], "NONE_OBSERVATION_ONLY")
            self.assertEqual(observation["matched_marker_relative_paths"], [])
            retention = result["resident_custody_root_observation_retention"]
            self.assertEqual(retention["state"], "NOT_RETAINED")
            self.assertEqual(retention["reason"], "NO_RESIDENT_RUNTIME_ROOT_OR_MATERIALIZATION_TARGET")

    def test_explicit_invalid_runtime_root_records_invalid_observation(self) -> None:
        now = dt.datetime(2026, 9, 13, 20, 0, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            github_root = self._github_root(tmp_root)
            schedule = tmp_root / "schedule.json"
            self._schedule(schedule)
            invalid_runtime_root = tmp_root / "empty-runtime-root"
            invalid_runtime_root.mkdir()
            with mock.patch.object(subject.base, "build_and_execute", return_value={"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "COMPLETE"}), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE": "all", "STEGVERSE_HEARTBEAT_ROOT": str(invalid_runtime_root)}, clear=False):
                result = subject.build_and_execute(tmp_root / "targets.json", schedule)
            self.assertEqual(result["state"], "BLOCKED")
            observation = result["resident_custody_root_observation"]
            self.assertEqual(observation["state"], "RESIDENT_CUSTODY_ROOT_INVALID")
            self.assertIsNone(observation["resident_runtime_root"])
            self.assertEqual(observation["resident_runtime_root_source"], "EXPLICIT_RUNTIME_ROOT_INVALID")
            self.assertEqual(result["resident_custody_root_observation_retention"]["state"], "NOT_RETAINED")

    def test_config_is_neutral_schedule_with_bounded_retry_parameters(self) -> None:
        config = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
        self.assertEqual(config["schema"], "stegverse.reusable-task-schedule/v1")
        rows = [row for row in config["tasks"] if row["reusable_task_id"] == "RT-NATIVE-EMAIL-ACTION-MONITOR-001"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["retry_interval_minutes"], 15)
        self.assertEqual(row["max_attempts_per_slot"], 4)
        self.assertTrue(row["enabled"])


if __name__ == "__main__":
    unittest.main()
