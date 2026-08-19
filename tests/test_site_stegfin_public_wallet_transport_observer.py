from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import sovereign_scheduler

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BLOB = "114b3c39052d5b1622407080407259a0040a1369"


class TestSiteStegFinPublicWalletTransportObserver(unittest.TestCase):
    def target(self) -> dict:
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "stegfin-public-wallet-transport-observer"
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def execute(self, site: Path) -> dict:
        roots = {"StegVerse-Labs/Site": site}
        return sovereign_scheduler._execute_target(
            {"repo": "StegVerse-Labs/Site", "workflow": "stegfin-public-wallet-transport-observer"},
            roots,
            json.dumps({key: str(value) for key, value in roots.items()}),
        )

    def install_script(self, site: Path, payload: dict, exit_code: int = 0) -> None:
        scripts = site / "scripts"
        scripts.mkdir(parents=True, exist_ok=True)
        (scripts / "check_stegfin_public_wallet_transport.py").write_text(
            "import json, os\n"
            "from pathlib import Path\n"
            "p=Path(os.environ['STEGFIN_PUBLICATION_REPORT'])\n"
            f"p.write_text(json.dumps({payload!r}))\n"
            f"raise SystemExit({exit_code})\n",
            encoding="utf-8",
        )

    def test_target_is_superseded_and_disabled_on_existing_scheduler(self):
        target = self.target()
        self.assertIs(target["enabled"], False)
        self.assertEqual(target["run_hours_utc"], list(range(24)))
        self.assertIn("site-stegfin-publication", target["aliases"])
        self.assertEqual(target["canonical_owner"], "StegVerse-Labs/Site#388")
        self.assertEqual(target["canonical_surface"], ".github/workflows/validate.yml + scripts/check_stegfin_public_wallet_transport.py")
        self.assertIn("superseded-disabled", target["status"])
        self.assertIn("canonical-site-validation-lane", target["status"])

    def test_missing_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            result = self.execute(site)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "SITE_STEGFIN_PUBLICATION_OBSERVER_MISSING")

    def test_credential_bearing_environment_fails_closed_before_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            self.install_script(site, {})
            with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "forbidden"}, clear=False):
                result = self.execute(site)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "SITE_STEGFIN_PUBLICATION_FORBIDDEN_CREDENTIAL_ENV")
        self.assertIn("GITHUB_TOKEN", result["forbidden"])

    def test_exact_verified_publication_completes_without_authority(self):
        payload = {
            "state": "VERIFIED_PUBLICATION",
            "publication_proven": True,
            "observed_ui_blob": EXPECTED_BLOB,
            "credential_authority": "TV/TVC",
            "credential_requirement": "NONE",
            "non_tv_tvc_secret_or_token_used": False,
            "github_token_required": False,
            "render_required": False,
            "authority_effect": False,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            self.install_script(site, payload)
            result = self.execute(site)
        self.assertEqual(result["state"], "COMPLETE")
        self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_STEGFIN_PUBLICATION_OBSERVATION")
        self.assertIs(result["receipt"]["authority_effect"], False)
        self.assertIs(result["receipt"]["github_token_required"], False)
        self.assertEqual(result["receipt"]["credential_authority"], "TV/TVC")

    def test_wrong_blob_or_nonzero_observer_blocks(self):
        payload = {
            "state": "VERIFIED_PUBLICATION",
            "publication_proven": True,
            "observed_ui_blob": "wrong",
            "credential_authority": "TV/TVC",
            "credential_requirement": "NONE",
            "non_tv_tvc_secret_or_token_used": False,
            "github_token_required": False,
            "render_required": False,
            "authority_effect": False,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            self.install_script(site, payload)
            wrong_blob = self.execute(site)
            self.install_script(site, payload, exit_code=1)
            nonzero = self.execute(site)
        self.assertEqual(wrong_blob["state"], "BLOCKED")
        self.assertEqual(wrong_blob["outcome"], "SOVEREIGN_LOCAL_SITE_STEGFIN_PUBLICATION_OBSERVATION")
        self.assertEqual(nonzero["state"], "BLOCKED")
        self.assertEqual(nonzero["outcome"], "SITE_STEGFIN_PUBLICATION_OBSERVATION_BLOCKED")


if __name__ == "__main__":
    unittest.main()
