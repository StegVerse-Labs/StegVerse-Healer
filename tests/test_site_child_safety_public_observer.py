from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]


class TestSiteChildSafetyPublicObserver(unittest.TestCase):
    def target(self) -> dict:
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "child-safety-public-deployment-observer"
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_target_is_hourly_and_uses_existing_scheduler(self):
        target = self.target()
        self.assertEqual(target["run_hours_utc"], list(range(24)))
        self.assertIn("child-safety-public-observer", target["aliases"])
        self.assertNotIn("token", json.dumps(target).lower().replace("no-github-token", ""))

    def test_missing_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            roots = {"StegVerse-Labs/Site": site}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "child-safety-public-deployment-observer"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_CHILD_SAFETY_OBSERVER_MISSING")

    def test_local_pass_receipt_completes_without_artifact_custody(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            scripts = site / "scripts"
            scripts.mkdir(parents=True)
            script = scripts / "check_child_safety_public_deployment.py"
            script.write_text(
                "import json, os\n"
                "from pathlib import Path\n"
                "p=Path(os.environ['STEGVERSE_CHILD_SAFETY_REPORT'])\n"
                "p.write_text(json.dumps({'state':'VERIFIED_PUBLICLY_REACHABLE','authority_effect':False,'github_token_required':False,'artifact_custody_required':False}))\n",
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/Site": site}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "child-safety-public-deployment-observer"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_CHILD_SAFETY_PUBLIC_OBSERVATION")
            self.assertIs(result["receipt"]["authority_effect"], False)
            self.assertIs(result["receipt"]["github_token_required"], False)
            self.assertIs(result["receipt"]["artifact_custody_required"], False)

    def test_non_pass_receipt_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            scripts = site / "scripts"
            scripts.mkdir(parents=True)
            script = scripts / "check_child_safety_public_deployment.py"
            script.write_text(
                "import json, os\n"
                "from pathlib import Path\n"
                "p=Path(os.environ['STEGVERSE_CHILD_SAFETY_REPORT'])\n"
                "p.write_text(json.dumps({'state':'BLOCKED','authority_effect':False,'github_token_required':False,'artifact_custody_required':False}))\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/Site": site}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "child-safety-public-deployment-observer"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_CHILD_SAFETY_PUBLIC_ROUTE_BLOCKED")


if __name__ == "__main__":
    unittest.main()
