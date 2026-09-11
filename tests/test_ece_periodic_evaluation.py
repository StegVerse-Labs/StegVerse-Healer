import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ece_cycle", ROOT / "app" / "ece_periodic_evaluation.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PeriodicEvaluationTests(unittest.TestCase):
    def test_missing_required_local_source_blocks_without_authority(self):
        with tempfile.TemporaryDirectory() as td:
            result = MOD.execute_periodic_ece({}, pathlib.Path(td))
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "ECE_REQUIRED_LOCAL_SOURCE_MISSING")
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertIn("master-records/orchestration", result["missing"])
        self.assertIn("StegVerse-Labs/.github", result["missing"])

    def test_missing_source_does_not_create_runtime_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = pathlib.Path(td)
            MOD.execute_periodic_ece({}, runtime)
            self.assertFalse((runtime / "receipts" / "ecosystem-continuity").exists())


if __name__ == "__main__":
    unittest.main()
