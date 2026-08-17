from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]


class TestSiteMarketplaceCoinbaseObserver(unittest.TestCase):
    def test_target_is_bound_to_existing_sovereign_scheduler(self):
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target
            for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "marketplace-coinbase-local-observer"
        ]
        self.assertEqual(len(matches), 1)
        target = matches[0]
        self.assertTrue(target["enabled"])
        self.assertEqual(target["run_hours_utc"], list(range(24)))
        self.assertIn("site-marketplace-coinbase", target["aliases"])

    def test_marketplace_credentials_are_forbidden(self):
        for name in ("MARKETPLACE_COINBASE_EVIDENCE_TOKEN", "STEGVERSE_CROSS_REPO_READ_TOKEN"):
            with self.subTest(name=name), mock.patch.dict(os.environ, {name: "forbidden"}, clear=False):
                with self.assertRaisesRegex(RuntimeError, "FORBIDDEN_GITHUB_CREDENTIAL_ENV"):
                    sovereign_scheduler._forbid_github_credentials()

    def test_handler_executes_only_materialized_site_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            scripts = site / "scripts"
            scripts.mkdir(parents=True)
            observer = scripts / "advance_marketplace_coinbase_activation.py"
            observer.write_text(
                "import json\nprint(json.dumps({'state':'ACTIVE_STEGVERSE_CONTINUATION','tasks':4}))\n",
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/Site": site}
            roots_json = json.dumps({key: str(value) for key, value in roots.items()})
            target = {"repo": "StegVerse-Labs/Site", "workflow": "marketplace-coinbase-local-observer"}
            result = sovereign_scheduler._execute_target(target, roots, roots_json)
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_MARKETPLACE_OBSERVATION")
            self.assertEqual(result["receipt"]["state"], "ACTIVE_STEGVERSE_CONTINUATION")
            self.assertIn("STEGVERSE_REPO_ROOTS_JSON", roots_json and result["execution"]["command"] and "STEGVERSE_REPO_ROOTS_JSON")

    def test_missing_site_observer_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            target = {"repo": "StegVerse-Labs/Site", "workflow": "marketplace-coinbase-local-observer"}
            result = sovereign_scheduler._execute_target(target, {"StegVerse-Labs/Site": site}, json.dumps({"StegVerse-Labs/Site": str(site)}))
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_MARKETPLACE_OBSERVER_MISSING")


if __name__ == "__main__":
    unittest.main()
