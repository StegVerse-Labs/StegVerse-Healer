from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]


class TestRepoStandardsST018TaskManager(unittest.TestCase):
    def test_target_is_bound_to_existing_scheduler(self):
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/repo-standards"
            and target.get("workflow") == "st018-local-task-manager"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["run_hours_utc"], [0, 6, 12, 18])
        self.assertIn("st018-task-manager", matches[0]["aliases"])

    def test_missing_task_manager_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo-standards"
            (repo / "orchestration").mkdir(parents=True)
            (repo / "orchestration" / "st018-task-registry.json").write_text("{}\n", encoding="utf-8")
            roots = {"StegVerse-Labs/repo-standards": repo}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/repo-standards", "workflow": "st018-local-task-manager"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "RSTD_ST018_TASK_MANAGER_MISSING")

    def test_missing_task_registry_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo-standards"
            (repo / "tools").mkdir(parents=True)
            (repo / "tools" / "run_st018_task_manager.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
            roots = {"StegVerse-Labs/repo-standards": repo}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/repo-standards", "workflow": "st018-local-task-manager"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "RSTD_ST018_TASK_REGISTRY_MISSING")

    def test_handler_executes_local_task_manager_and_requires_pass_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo-standards"
            (repo / "tools").mkdir(parents=True)
            (repo / "orchestration").mkdir(parents=True)
            (repo / "reports").mkdir(parents=True)
            (repo / "orchestration" / "st018-task-registry.json").write_text('{"tasks":[]}\n', encoding="utf-8")
            (repo / "tools" / "run_st018_task_manager.py").write_text(
                "import json\n"
                "from pathlib import Path\n"
                "Path('reports/st018-task-execution.report.json').write_text(json.dumps({'status':'PASS'}))\n",
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/repo-standards": repo}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/repo-standards", "workflow": "st018-local-task-manager"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_RSTD_ST018_TASK_MANAGER")
            self.assertEqual(result["receipt"]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
