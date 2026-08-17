from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]
LOCAL_CAPABILITY_MARKERS = "# STEGVERSE_REPO_ROOTS_JSON\n# GCAT-BCAT-Engine/Publisher\n"


class TestSiteMarketplaceProjectionImport(unittest.TestCase):
    def test_target_is_bound_to_existing_scheduler(self):
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "marketplace-coinbase-local-projection-import"
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["run_hours_utc"], list(range(24)))
        self.assertIn("marketplace-coinbase-projection", matches[0]["aliases"])

    def test_missing_site_importer_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            publisher = Path(temp_dir) / "Publisher"
            site.mkdir()
            publisher.mkdir()
            roots = {"StegVerse-Labs/Site": site, "GCAT-BCAT-Engine/Publisher": publisher}
            roots_json = json.dumps({key: str(value) for key, value in roots.items()})
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "marketplace-coinbase-local-projection-import"}, roots, roots_json
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_MARKETPLACE_PROJECTION_IMPORTER_MISSING")

    def test_legacy_remote_site_importer_fails_closed_before_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            publisher = Path(temp_dir) / "Publisher"
            scripts = site / "scripts"
            scripts.mkdir(parents=True)
            publisher.mkdir()
            (scripts / "import_marketplace_coinbase_accessibility.py").write_text(
                "from urllib import request\nSOURCE='https://raw.githubusercontent.com/example/repo/main/state.json'\n",
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/Site": site, "GCAT-BCAT-Engine/Publisher": publisher}
            roots_json = json.dumps({key: str(value) for key, value in roots.items()})
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "marketplace-coinbase-local-projection-import"}, roots, roots_json
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_MARKETPLACE_PROJECTION_LOCAL_CAPABILITY_NOT_INSTALLED")

    def test_missing_publisher_repo_fails_closed_after_capability_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            scripts = site / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "import_marketplace_coinbase_accessibility.py").write_text(
                LOCAL_CAPABILITY_MARKERS + "raise SystemExit(0)\n", encoding="utf-8"
            )
            roots = {"StegVerse-Labs/Site": site}
            roots_json = json.dumps({key: str(value) for key, value in roots.items()})
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "marketplace-coinbase-local-projection-import"}, roots, roots_json
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "PUBLISHER_LOCAL_REPOSITORY_NOT_MATERIALIZED")

    def test_handler_executes_local_site_importer_with_local_publisher(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            publisher = Path(temp_dir) / "Publisher"
            scripts = site / "scripts"
            data = site / "data"
            scripts.mkdir(parents=True)
            data.mkdir(parents=True)
            publisher.mkdir()
            importer = scripts / "import_marketplace_coinbase_accessibility.py"
            importer.write_text(
                LOCAL_CAPABILITY_MARKERS
                + "import json\n"
                + "from pathlib import Path\n"
                + "Path('data/marketplace-coinbase-accessibility-status.json').write_text(json.dumps({'state':'PAPER_ACCESSIBLE'}))\n",
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/Site": site, "GCAT-BCAT-Engine/Publisher": publisher}
            roots_json = json.dumps({key: str(value) for key, value in roots.items()})
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "marketplace-coinbase-local-projection-import"}, roots, roots_json
            )
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_MARKETPLACE_PROJECTION_IMPORT")
            self.assertEqual(result["receipt"]["state"], "PAPER_ACCESSIBLE")


if __name__ == "__main__":
    unittest.main()
