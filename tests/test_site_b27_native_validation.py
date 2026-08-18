from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]


class TestSiteB27NativeValidation(unittest.TestCase):
    def target(self) -> dict:
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "site-b27-native-validation"
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_target_reuses_existing_scheduler_without_token_or_remote_checkout(self):
        target = self.target()
        self.assertEqual(target["run_hours_utc"], [0, 6, 12, 18])
        self.assertIn("site-b27-validation", target["aliases"])
        serialized = json.dumps(target).lower()
        self.assertIn("no-github-token", serialized)
        self.assertIn("no-remote-checkout", serialized)
        self.assertIn("no-artifact-custody", serialized)

    def test_missing_validator_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            roots = {"StegVerse-Labs/Site": site}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "site-b27-native-validation"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_B27_VALIDATOR_MISSING")

    def _build_fake_site(self, root: Path) -> None:
        scripts = [
            "check_thought_experiments_publication.py",
            "write_site_workflow_inventory.py",
            "check_site_workflow_inventory.py",
            "check_session_work_claims.py",
            "site_handoff_orchestrator.py",
            "check_ecosystem_heartbeat_orchestration.py",
            "check_ecosystem_chat_application.py",
            "check_iphone_heartbeat_transition_projection.py",
            "run_sandbox_validation.py",
            "check_stegfin_phone_projection.py",
        ]
        (root / "scripts").mkdir(parents=True)
        for name in scripts:
            (root / "scripts" / name).write_text("raise SystemExit(0)\n", encoding="utf-8")
        (root / "data" / "tasks").mkdir(parents=True)
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / "data" / "tasks" / "SITE-ACTIONS-COST-CONTAINMENT-001-B27.json").write_text(
            json.dumps({
                "credential_authority": "TV/TVC",
                "non_tv_tvc_secret_or_token_allowed": False,
                "github_actions_runtime_authority": "NONE",
                "render_required": False,
            }),
            encoding="utf-8",
        )

    def test_pass_receipt_requires_exact_local_head_and_non_authorizing_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            self._build_fake_site(site)
            roots = {"StegVerse-Labs/Site": site}
            head = "a" * 40

            def fake_run(command, cwd, env_extra=None, timeout=180):
                if command[:3] == ["git", "rev-parse", "HEAD"]:
                    return {"command": command, "returncode": 0, "stdout_tail": head + "\n", "stderr_tail": ""}
                script = command[-1]
                if script == "scripts/check_thought_experiments_publication.py":
                    (site / "thought-experiments-publication.report.json").write_text(
                        json.dumps({"state": "PASS", "authority_effect": False, "activation_effect": False}),
                        encoding="utf-8",
                    )
                if script == "scripts/write_site_workflow_inventory.py":
                    (site / "data" / "site-workflow-inventory.json").write_text(
                        json.dumps({
                            "workflow_file_count": 97,
                            "canonical_count": 3,
                            "migration_required_operational_count": 94,
                            "placeholder_count": 0,
                        }),
                        encoding="utf-8",
                    )
                return {"command": command, "returncode": 0, "stdout_tail": "PASS\n", "stderr_tail": ""}

            with patch.object(sovereign_scheduler, "_run", side_effect=fake_run):
                result = sovereign_scheduler._execute_target(
                    {"repo": "StegVerse-Labs/Site", "workflow": "site-b27-native-validation"},
                    roots,
                    json.dumps({key: str(value) for key, value in roots.items()}),
                )

            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_B27_VALIDATION")
            receipt = result["receipt"]
            self.assertEqual(receipt["state"], "PASS")
            self.assertEqual(receipt["source_head"], head)
            self.assertEqual(receipt["credential_authority"], "TV/TVC")
            self.assertIs(receipt["github_token_required"], False)
            self.assertIs(receipt["remote_checkout_required"], False)
            self.assertIs(receipt["artifact_custody_required"], False)
            self.assertIs(receipt["repository_writeback_authority"], False)
            self.assertIs(receipt["runtime_authority"], False)
            self.assertIs(receipt["wallet_signing_broadcast_authority"], False)
            self.assertIs(receipt["publication_authority"], False)
            self.assertIs(receipt["settlement_authority"], False)
            self.assertEqual(receipt["workflow_file_count"], 97)
            self.assertEqual(receipt["canonical_count"], 3)
            self.assertEqual(receipt["migration_required_operational_count"], 94)
            self.assertEqual(receipt["placeholder_count"], 0)

    def test_validator_failure_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            self._build_fake_site(site)
            roots = {"StegVerse-Labs/Site": site}

            def fake_run(command, cwd, env_extra=None, timeout=180):
                if command[:3] == ["git", "rev-parse", "HEAD"]:
                    return {"command": command, "returncode": 0, "stdout_tail": "b" * 40 + "\n", "stderr_tail": ""}
                return {"command": command, "returncode": 1, "stdout_tail": "", "stderr_tail": "blocked"}

            with patch.object(sovereign_scheduler, "_run", side_effect=fake_run):
                result = sovereign_scheduler._execute_target(
                    {"repo": "StegVerse-Labs/Site", "workflow": "site-b27-native-validation"},
                    roots,
                    json.dumps({key: str(value) for key, value in roots.items()}),
                )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_B27_VALIDATION_BLOCKED")

    def test_credential_bearing_environment_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            self._build_fake_site(site)
            roots = {"StegVerse-Labs/Site": site}
            with patch.dict(os.environ, {"GITHUB_TOKEN": "forbidden"}, clear=False):
                result = sovereign_scheduler._execute_target(
                    {"repo": "StegVerse-Labs/Site", "workflow": "site-b27-native-validation"},
                    roots,
                    json.dumps({key: str(value) for key, value in roots.items()}),
                )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_B27_FORBIDDEN_CREDENTIAL_ENV")


if __name__ == "__main__":
    unittest.main()
