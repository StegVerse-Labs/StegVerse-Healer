from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]


class TestSiteHeartbeatResponseCarrier(unittest.TestCase):
    def target(self) -> dict:
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "heartbeat-response-sovereign-carrier"
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def init_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "tests@stegverse.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "StegVerse Tests"], cwd=root, check=True)
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)

    def write_scripts(self, root: Path, failing: str | None = None) -> None:
        scripts = root / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        names = {
            "process_heartbeat_response_node.py": "node_apply",
            "collect_heartbeat_response_receipts.py": "collector_apply",
            "check_heartbeat_response_network.py": "network_validation",
        }
        for name, label in names.items():
            code = 1 if label == failing else 0
            (scripts / name).write_text(
                "import sys\n"
                f"print('{label}')\n"
                f"raise SystemExit({code})\n",
                encoding="utf-8",
            )

    def execute(self, site: Path) -> dict:
        roots = {"StegVerse-Labs/Site": site}
        return sovereign_scheduler._execute_target(
            {"repo": "StegVerse-Labs/Site", "workflow": "heartbeat-response-sovereign-carrier"},
            roots,
            json.dumps({key: str(value) for key, value in roots.items()}),
        )

    def test_target_reuses_existing_hourly_scheduler(self):
        target = self.target()
        self.assertEqual(target["run_hours_utc"], list(range(24)))
        self.assertEqual(target["canonical_owner"], "StegVerse-Labs/Site#234")
        self.assertEqual(target["migration_issue"], "StegVerse-Labs/Site#411")
        self.assertIn("heartbeat-response-watchdog", target["aliases"])

    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            result = self.execute(site)
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_HEARTBEAT_RESPONSE_CARRIER_SOURCE_MISSING")

    def test_forbidden_github_credential_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            with patch.dict(os.environ, {"GITHUB_TOKEN": "forbidden"}, clear=False):
                result = self.execute(site)
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_HEARTBEAT_RESPONSE_FORBIDDEN_CREDENTIAL_ENV")
            self.assertIn("GITHUB_TOKEN", result["forbidden"])

    def test_local_carrier_runs_apply_and_validation_without_writeback_authority(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            self.init_repo(site)
            self.write_scripts(site)
            result = self.execute(site)
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_HEARTBEAT_RESPONSE_CARRIER")
            receipt = result["receipt"]
            self.assertEqual(receipt["state"], "PASS")
            self.assertEqual(len(receipt["source_head"]), 40)
            self.assertEqual(receipt["credential_authority"], "TV/TVC")
            self.assertIs(receipt["github_token_required"], False)
            self.assertIs(receipt["remote_checkout_required"], False)
            self.assertIs(receipt["artifact_custody_required"], False)
            self.assertIs(receipt["repository_writeback_authority"], False)
            self.assertIs(receipt["local_state_mutation"], True)
            self.assertIs(receipt["runtime_authority"], False)
            self.assertIs(receipt["activation_authority"], False)
            self.assertEqual(
                [entry["label"] for entry in result["execution"]],
                ["node_apply", "collector_apply", "network_validation"],
            )

    def test_failed_collector_blocks_before_network_validation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            self.init_repo(site)
            self.write_scripts(site, failing="collector_apply")
            result = self.execute(site)
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_HEARTBEAT_RESPONSE_SOVEREIGN_EXECUTION_BLOCKED")
            self.assertEqual(result["failed_step"], "collector_apply")
            self.assertEqual(len(result["execution"]), 2)


if __name__ == "__main__":
    unittest.main()
