from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.site_erl_sync import execute_site_erl_sync

ROOT = Path(__file__).resolve().parents[1]


class TestSiteErlSync(unittest.TestCase):
    def target(self) -> dict:
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "executive-rhetoric-ledger-local-sync"
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_target_uses_existing_daily_scheduler_without_token_metadata(self):
        target = self.target()
        self.assertEqual(target["run_hours_utc"], [14])
        self.assertEqual(target["source_repository"], "StegVerse-Labs/Executive_Rhetoric_Ledger")
        self.assertEqual(target["source_path"], "publication/compendium.json")
        self.assertEqual(target["destination_path"], "public/data/executive-rhetoric-ledger/compendium.json")
        serialized = json.dumps(target).lower().replace("no-github-token", "")
        self.assertNotIn("github_token", serialized)
        self.assertNotIn("gh_token", serialized)

    def test_local_copy_hash_and_destination_acknowledgment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            site = base / "Site"
            source = base / "Executive_Rhetoric_Ledger"
            (source / "publication").mkdir(parents=True)
            site.mkdir()
            payload = {"schema_version": "test", "entries": [{"id": "ERL-1", "claim": "bounded"}]}
            source_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
            (source / "publication" / "compendium.json").write_bytes(source_bytes)
            roots = {
                "StegVerse-Labs/Site": site,
                "StegVerse-Labs/Executive_Rhetoric_Ledger": source,
            }
            result = execute_site_erl_sync(self.target(), roots, {"repo": "StegVerse-Labs/Site", "workflow": "executive-rhetoric-ledger-local-sync"})
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_ERL_SYNC")
            destination = site / "public/data/executive-rhetoric-ledger/compendium.json"
            acknowledgment = site / "receipts/executive-rhetoric-ledger-ack.json"
            self.assertEqual(destination.read_bytes(), source_bytes)
            receipt = json.loads(acknowledgment.read_text(encoding="utf-8"))
            self.assertEqual(receipt["state"], "PASS")
            self.assertTrue(receipt["byte_equal"])
            self.assertEqual(receipt["source_sha256"], receipt["destination_sha256"])
            self.assertTrue(receipt["acknowledgment_owned_by_destination"])
            self.assertFalse(receipt["source_self_acknowledgment_allowed"])
            self.assertFalse(receipt["github_token_required"])
            self.assertFalse(receipt["remote_checkout_required"])
            self.assertFalse(receipt["artifact_custody_required"])
            self.assertFalse(receipt["repository_writeback_authority"])
            self.assertFalse(receipt["runtime_authority"])
            self.assertFalse(receipt["publication_authority"])
            self.assertFalse(receipt["activation_authority"])

    def test_missing_source_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            result = execute_site_erl_sync(
                self.target(),
                {"StegVerse-Labs/Site": site},
                {"repo": "StegVerse-Labs/Site", "workflow": "executive-rhetoric-ledger-local-sync"},
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_ERL_SYNC_SOURCE_ROOT_NOT_MATERIALIZED")

    def test_missing_source_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            site = base / "Site"
            source = base / "Executive_Rhetoric_Ledger"
            site.mkdir(); source.mkdir()
            result = execute_site_erl_sync(
                self.target(),
                {"StegVerse-Labs/Site": site, "StegVerse-Labs/Executive_Rhetoric_Ledger": source},
                {"repo": "StegVerse-Labs/Site", "workflow": "executive-rhetoric-ledger-local-sync"},
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_ERL_SYNC_SOURCE_MISSING")

    def test_invalid_json_fails_closed_without_destination_ack(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            site = base / "Site"
            source = base / "Executive_Rhetoric_Ledger"
            (source / "publication").mkdir(parents=True)
            site.mkdir()
            (source / "publication" / "compendium.json").write_text("{bad json", encoding="utf-8")
            result = execute_site_erl_sync(
                self.target(),
                {"StegVerse-Labs/Site": site, "StegVerse-Labs/Executive_Rhetoric_Ledger": source},
                {"repo": "StegVerse-Labs/Site", "workflow": "executive-rhetoric-ledger-local-sync"},
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_ERL_SYNC_SOURCE_INVALID_JSON")
            self.assertFalse((site / "public/data/executive-rhetoric-ledger/compendium.json").exists())
            self.assertFalse((site / "receipts/executive-rhetoric-ledger-ack.json").exists())

    def test_github_credentials_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            site = base / "Site"
            source = base / "Executive_Rhetoric_Ledger"
            (source / "publication").mkdir(parents=True)
            site.mkdir()
            (source / "publication" / "compendium.json").write_text("{}\n", encoding="utf-8")
            roots = {"StegVerse-Labs/Site": site, "StegVerse-Labs/Executive_Rhetoric_Ledger": source}
            with patch.dict(os.environ, {"GITHUB_TOKEN": "forbidden"}, clear=False):
                result = execute_site_erl_sync(
                    self.target(), roots,
                    {"repo": "StegVerse-Labs/Site", "workflow": "executive-rhetoric-ledger-local-sync"},
                )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_ERL_SYNC_FORBIDDEN_CREDENTIAL_ENV")
            self.assertIn("GITHUB_TOKEN", result["forbidden"])


if __name__ == "__main__":
    unittest.main()
