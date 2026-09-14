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


class ResidentRuntimeRootBootstrapTests(unittest.TestCase):
    def test_existing_source_refresh_can_materialize_missing_canonical_root(self) -> None:
        now = dt.datetime(2026, 9, 14, 18, 30, tzinfo=dt.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            home = tmp_root / "home"
            github_root = tmp_root / ".github"
            trigger = github_root / "scripts" / "trigger_reusable_task.py"
            trigger.parent.mkdir(parents=True)
            trigger.write_text("# neutral reusable trigger\n", encoding="utf-8")
            schedule = tmp_root / "schedule.json"
            schedule.write_text(json.dumps({
                "schema": subject.SCHEDULE_SCHEMA,
                "tasks": [{
                    "reusable_task_id": subject.SOURCE_REFRESH_TASK_ID,
                    "tracking_task_id": "SITE-PUBLICATION-NATIVE-RUNTIME-EXECUTION-001",
                    "cosv_task_vector": "50000000102000",
                    "repository": "StegVerse-Labs/.github",
                    "enabled": True,
                    "run_hours_utc": list(range(24)),
                    "retry_interval_minutes": 15,
                    "max_attempts_per_slot": 4,
                    "parameters": {},
                }],
            }), encoding="utf-8")

            def fake_run(command, cwd, env, timeout):
                runtime_root = Path(env[subject.RUNTIME_ROOT_ENV])
                marker = runtime_root / "control/resident-execution-request.d/canonical-work-stegbrowser-runtime-consumption-001.json"
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_text("{}\n", encoding="utf-8")
                receipt = Path(command[command.index("--receipt") + 1])
                invocation = command[command.index("--invocation-id") + 1]
                result = receipt.with_name(f"{invocation}.runner-result.json")
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_text(json.dumps({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) + "\n", encoding="utf-8")
                result.write_text(json.dumps({
                    "schema": "stegverse.reusable-task-runner-result/v1",
                    "due_task_count": 1,
                    "outcomes": [{
                        "reusable_task_id": subject.SOURCE_REFRESH_TASK_ID,
                        "state": "ENTROPY_RECOVERY_RECORDED",
                        "slot_satisfied": True,
                    }],
                }) + "\n", encoding="utf-8")
                return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

            with mock.patch.object(subject.base, "build_and_execute", return_value={"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "COMPLETE"}), \
                 mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
                 mock.patch.object(subject.base, "_now", return_value=now), \
                 mock.patch.object(subject.base, "_run", side_effect=fake_run), \
                 mock.patch.object(subject.Path, "home", return_value=home), \
                 mock.patch.dict("os.environ", {"RUN_SCOPE": "all", "STEGVERSE_HEARTBEAT_ROOT": ""}, clear=False):
                result = subject.build_and_execute(tmp_root / "targets.json", schedule)

            expected_root = (home / ".local" / "state" / "stegverse" / "heartbeat-runtime").resolve()
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["resident_runtime_root"], str(expected_root))
            self.assertEqual(result["resident_runtime_materialization_target"], str(expected_root))
            self.assertEqual(result["resident_runtime_materialization_target_source"], "CANONICAL_LOCAL_RUNTIME_MATERIALIZATION_TARGET")
            self.assertEqual(result["resident_custody_root_observation"]["state"], "RESIDENT_CUSTODY_ROOT_OBSERVED")
            self.assertIn(
                "control/resident-execution-request.d/canonical-work-stegbrowser-runtime-consumption-001.json",
                result["resident_custody_root_observation"]["matched_marker_relative_paths"],
            )
            self.assertEqual(result["neutral_reusable_task_scheduler"]["state"], "DELEGATED")


if __name__ == "__main__":
    unittest.main()
