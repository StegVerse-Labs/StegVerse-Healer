import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import audit_schedules


class QuietEnforcerCostIntegrationTests(unittest.TestCase):
    def _env(self, targets: Path, receipt: Path, repo_root: Path) -> dict[str, str]:
        policy = Path(__file__).resolve().parents[1] / "data" / "actions_cost_policy.json"
        return {
            "TARGETS_FILE": str(targets),
            "QUIET_RECEIPT": str(receipt),
            "ACTIONS_COST_POLICY": str(policy),
            "STEGVERSE_REPO_ROOTS_JSON": json.dumps({"StegVerse-Labs/Repo": str(repo_root)}),
        }

    def test_quiet_enforcer_embeds_ranked_actions_cost_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_root = tmp_path / "Repo"
            workflow = repo_root / ".github" / "workflows" / "validate.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                """name: Validate\non:\n  push: {}\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo pass\n""",
                encoding="utf-8",
            )
            targets = tmp_path / "targets.json"
            targets.write_text(json.dumps({"targets": [{"repo": "StegVerse-Labs/Repo", "workflow": "validate.yml", "enabled": True, "run_hours_utc": [3]}]}), encoding="utf-8")
            receipt = tmp_path / "quiet.json"
            env = self._env(targets, receipt, repo_root)
            for name in audit_schedules.FORBIDDEN_CREDENTIALS:
                env.pop(name, None)
            clean = {k: v for k, v in os.environ.items() if k not in audit_schedules.FORBIDDEN_CREDENTIALS}
            clean.update(env)
            with mock.patch.dict(os.environ, clean, clear=True):
                self.assertEqual(audit_schedules.main(), 0)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "stegverse.healer.quiet-enforcer-receipt.v3")
            self.assertEqual(payload["state"], "COMPLETE")
            self.assertEqual(payload["summary"]["violation_count"], 0)
            self.assertGreaterEqual(payload["summary"]["cost_review_candidate_count"], 1)
            self.assertFalse(payload["cost_analysis"]["github_token_required"])
            self.assertFalse(payload["cost_analysis"]["network_required"])
            self.assertEqual(payload["cost_analysis"]["authority_effect"], "NONE")
            top = payload["cost_analysis"]["top_remediation_candidates"]
            self.assertTrue(top)
            self.assertTrue(top[0]["workflow"].endswith("validate.yml"))
            self.assertIn("UNFILTERED_PUSH", top[0]["review_reasons"])

    def test_quiet_enforcer_still_fails_repository_local_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_root = tmp_path / "Repo"
            workflow = repo_root / ".github" / "workflows" / "hourly.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(
                """name: Hourly\non:\n  schedule:\n    - cron: '0 * * * *'\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo pass\n""",
                encoding="utf-8",
            )
            targets = tmp_path / "targets.json"
            targets.write_text(json.dumps({"targets": [{"repo": "StegVerse-Labs/Repo", "workflow": "hourly.yml", "enabled": True}]}), encoding="utf-8")
            receipt = tmp_path / "quiet.json"
            env = self._env(targets, receipt, repo_root)
            clean = {k: v for k, v in os.environ.items() if k not in audit_schedules.FORBIDDEN_CREDENTIALS}
            clean.update(env)
            with mock.patch.dict(os.environ, clean, clear=True):
                self.assertEqual(audit_schedules.main(), 1)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(payload["state"], "FAILED")
            self.assertEqual(payload["summary"]["violation_count"], 1)
            self.assertEqual(payload["cost_analysis"]["scheduled_workflow_count"], 1)
            self.assertEqual(payload["cost_analysis"]["estimated_scheduled_job_starts_per_month"], 744.0)


if __name__ == "__main__":
    unittest.main()
