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
        self.assertIn("StegVerse-org/StegVerse-SDK", result["missing"])

    def test_missing_source_does_not_create_runtime_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            runtime = pathlib.Path(td)
            MOD.execute_periodic_ece({}, runtime)
            self.assertFalse((runtime / "receipts" / "ecosystem-continuity").exists())

    def test_diagnostic_request_covers_registry_and_preserves_missing_observation(self):
        registry = {
            "components": [{
                "component_id": "sdk",
                "authority_owner": "StegVerse-org/StegVerse-SDK",
                "predicates": [{"predicate_id": "route_installed"}],
            }]
        }
        request = MOD._diagnostic_request(registry, {"observations": []}, "2026-09-12T05:00:00Z")
        self.assertEqual(request["schema"], "stegverse.ecosystem-diagnostic-request.v1")
        self.assertEqual(request["scope"], "ecosystem")
        self.assertFalse(request["mutation_permitted"])
        self.assertEqual(request["expected_evidence_fields"], ["evidence_refs", "observed_at"])
        self.assertEqual(request["tests"][0]["component_id"], "sdk")
        self.assertIsNone(request["tests"][0]["observation"])

    def test_sdk_result_translation_binds_exact_result_hash(self):
        result = {
            "schema": "stegverse.ecosystem-diagnostic-result.v1",
            "processing_capability": "ecosystem_diagnostic",
            "route_id": "stegverse.route.ecosystem-diagnostic.v1",
            "scope": "ecosystem",
            "results": [{
                "test_id": "ece:sdk:route_installed",
                "component_id": "sdk",
                "predicate_id": "route_installed",
                "observation_state": "PASS",
                "evidence_refs": ["receipt:abc"],
                "evidence_age_seconds": 4,
                "authority_owner": "StegVerse-org/StegVerse-SDK",
                "detail": "observed",
                "mutation_performed": False,
            }],
            "mutation_performed": False,
            "authority_effect": "NONE_DIAGNOSTIC_ONLY",
            "continuity_state_present": False,
        }
        translated = MOD._ece_observations_from_diagnostic(result, "a" * 64)
        row = translated["observations"][0]
        self.assertEqual(row["state"], "PASS")
        self.assertIn("receipt:abc", row["evidence"])
        self.assertIn("sdk-diagnostic-result-sha256:" + "a" * 64, row["evidence"])
        self.assertEqual(row["sdk_diagnostic_test_id"], "ece:sdk:route_installed")

    def test_sdk_result_cannot_supply_continuity_state(self):
        result = {
            "schema": "stegverse.ecosystem-diagnostic-result.v1",
            "processing_capability": "ecosystem_diagnostic",
            "route_id": "stegverse.route.ecosystem-diagnostic.v1",
            "results": [],
            "mutation_performed": False,
            "authority_effect": "NONE_DIAGNOSTIC_ONLY",
            "continuity_state_present": False,
            "continuity_state": "CONTINUOUS",
        }
        with self.assertRaisesRegex(ValueError, "MUST_NOT_SUPPLY_CONTINUITY"):
            MOD._ece_observations_from_diagnostic(result, "b" * 64)

    def test_sdk_result_authority_drift_fails_closed(self):
        result = {
            "schema": "stegverse.ecosystem-diagnostic-result.v1",
            "processing_capability": "ecosystem_diagnostic",
            "route_id": "stegverse.route.ecosystem-diagnostic.v1",
            "results": [],
            "mutation_performed": False,
            "authority_effect": "EXECUTE",
            "continuity_state_present": False,
        }
        with self.assertRaisesRegex(ValueError, "AUTHORITY_DRIFT"):
            MOD._ece_observations_from_diagnostic(result, "c" * 64)


if __name__ == "__main__":
    unittest.main()
