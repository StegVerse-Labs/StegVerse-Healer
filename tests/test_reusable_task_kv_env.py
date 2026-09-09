from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from app import reusable_task_scheduler as scheduler


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

    def test_scheduled_reusable_task_receives_kv_root(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / ".github"
            runtime = base / "heartbeat-runtime"
            (source / "scripts").mkdir(parents=True)
            (source / "scripts" / "trigger_reusable_task.py").write_text("# trigger\n", encoding="utf-8")
            (runtime / scheduler.RUNTIME_REQUIRED_REL).parent.mkdir(parents=True)
            (runtime / scheduler.RUNTIME_REQUIRED_REL).write_text("{}\n", encoding="utf-8")
            kv_root = base / "KnowledgeVault"
            kv_root.mkdir()
            captured = {}

            def fake_run(command, cwd, env, timeout):
                captured.update(env)
                receipt_path = Path(command[command.index("--receipt") + 1])
                receipt_path.parent.mkdir(parents=True, exist_ok=True)
                receipt_path.write_text(json.dumps({"state": "HANDOFF_READY"}) + "\n", encoding="utf-8")
                return {"returncode": 0, "stdout": "", "stderr": ""}

            task = {
                "reusable_task_id": "RT-NATIVE-EMAIL-ACTION-MONITOR-001",
                "tracking_task_id": "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001",
                "cosv_task_vector": "10100000100000",
                "repository": "StegVerse-Labs/.github",
                "parameters": {},
            }
            with patch.dict(os.environ, {"STEGVERSE_KV_ROOT": str(kv_root)}, clear=False), patch.object(scheduler.base, "_run", side_effect=fake_run):
                result = scheduler._execute_reusable_task(
                    task,
                    {"StegVerse-Labs/.github": source},
                    json.dumps({"StegVerse-Labs/.github": str(source)}),
                    runtime,
                    "EXPLICIT_NONSECRET_RUNTIME_ROOT",
                    datetime(2026, 9, 9, 14, 0, tzinfo=timezone.utc),
                )
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(captured["STEGVERSE_KV_ROOT"], str(kv_root))
            self.assertIn("STEGVERSE_KV_ROOT", result["kv_path_env_forwarded"])


if __name__ == "__main__":
    unittest.main()
