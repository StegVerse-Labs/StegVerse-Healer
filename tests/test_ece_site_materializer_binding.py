from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ece_runner", ROOT / "app" / "run_ece_periodic_evaluation.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def base_result(root: Path) -> dict:
    output = root / "receipts" / "ecosystem-continuity"
    output.mkdir(parents=True)
    result = {
        "schema": "stegverse.healer-ecosystem-continuity-cycle/v1",
        "state": "COMPLETE",
        "site_projection_ref": str((output / "site-projection.latest.json").resolve()),
        "site_projection_sha256": "a" * 64,
        "authority_effect": "NONE",
        "execution": [],
    }
    (output / "cycle.latest.json").write_text(json.dumps(result), encoding="utf-8")
    return result


class SiteMaterializerBindingTests(unittest.TestCase):
    def test_missing_served_root_is_honest_not_bound_not_failure(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {}, clear=True):
            runtime = Path(td)
            result = MOD.bind_site_materialization(base_result(runtime), {}, runtime)
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["site_materialization_state"], "NOT_BOUND")
            self.assertFalse(result["site_live_publication_observed"])
            retained = json.loads((runtime / "receipts" / "ecosystem-continuity" / "cycle.latest.json").read_text())
            self.assertEqual(retained["site_materialization_state"], "NOT_BOUND")

    def test_explicit_served_root_requires_local_site_source(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"STEGVERSE_SITE_SERVED_ROOT": str(Path(td) / "served")}, clear=True):
            runtime = Path(td) / "runtime"
            result = MOD.bind_site_materialization(base_result(runtime), {}, runtime)
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "ECE_SITE_LOCAL_SOURCE_MISSING_FOR_MATERIALIZER")

    def test_noncomplete_cycle_is_not_materialized(self):
        with tempfile.TemporaryDirectory() as td, patch.dict(os.environ, {"STEGVERSE_SITE_SERVED_ROOT": str(Path(td) / "served")}, clear=True):
            result = {"state": "BLOCKED", "outcome": "UPSTREAM_BLOCK"}
            self.assertIs(MOD.bind_site_materialization(result, {}, Path(td)), result)


if __name__ == "__main__":
    unittest.main()
