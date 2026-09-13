from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import reusable_task_scheduler as scheduler  # noqa: E402


class ReusableTaskKVEnvTests(unittest.TestCase):
    def test_kv_path_projection_forwards_only_present_nonsecret_paths(self):
        with patch.dict(os.environ, {
            "STEGVERSE_KV_ROOT": "/local/KnowledgeVault",
            "STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT": "/provider/KnowledgeVault",
        }, clear=True):
            self.assertEqual(scheduler._kv_path_env(), {
                "STEGVERSE_KV_ROOT": "/local/KnowledgeVault",
                "STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT": "/provider/KnowledgeVault",
            })

    def test_neutral_scheduler_delegation_receives_kv_root(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / ".github"
            runtime = base / "heartbeat-runtime"
            schedule = base / "schedule.json"
            (source / "scripts").mkdir(parents=True)
            (source / "scripts" / "trigger_reusable_task.py").write_text("# trigger\n", encoding="utf-8")
            (runtime / scheduler.RUNTIME_REQUIRED_REL).parent.mkdir(parents=True)
            (runtime / scheduler.RUNTIME_REQUIRED_REL).write_text("{}\n", encoding="utf-8")
            schedule.write_text(json.dumps({"schema": scheduler.SCHEDULE_SCHEMA, "tasks": []}) + "\n", encoding="utf-8")
            kv_root = base / "KnowledgeVault"
            kv_root.mkdir()
            captured = {}

            def fake_run(command, cwd, env, timeout):
                captured.update(env)
                receipt = Path(command[command.index("--receipt") + 1])
                invocation = command[command.index("--invocation-id") + 1]
                result = receipt.with_name(f"{invocation}.runner-result.json")
                receipt.parent.mkdir(parents=True, exist_ok=True)
                receipt.write_text(json.dumps({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) + "\n", encoding="utf-8")
                result.write_text(json.dumps({"schema": "stegverse.reusable-task-runner-result/v1", "due_task_count": 0, "outcomes": []}) + "\n", encoding="utf-8")
                return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

            with patch.dict(os.environ, {"STEGVERSE_KV_ROOT": str(kv_root)}, clear=False), patch.object(scheduler.base, "_run", side_effect=fake_run):
                result = scheduler._invoke_neutral_scheduler(
                    roots={"StegVerse-Labs/.github": source},
                    runtime_root=runtime,
                    runtime_root_source="EXPLICIT_NONSECRET_RUNTIME_ROOT",
                    schedule_path=schedule,
                    now=datetime(2026, 9, 13, 20, 30, tzinfo=timezone.utc),
                    scope="all",
                )

            self.assertEqual(result["state"], "DELEGATED")
            self.assertEqual(captured["STEGVERSE_KV_ROOT"], str(kv_root))
            self.assertEqual(captured["STEGVERSE_HEARTBEAT_ROOT"], str(runtime))
            self.assertIn("STEGVERSE_REPO_ROOTS_JSON", captured)


if __name__ == "__main__":
    unittest.main()
