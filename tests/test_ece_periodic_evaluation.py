import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ece_cycle", ROOT / "app" / "ece_periodic_evaluation.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

# Exact label StegVerse-SDK main puts on local diagnostic output (stegverse/cli.py LOCAL_ENCLOSED_LANE).
SDK_LOCAL_ENCLOSED_LANE = {
    "lane": "SDK_LOCAL_ENCLOSED_VALIDATION",
    "canonical": False,
    "authorizing": False,
    "selected_by_manifest_route": False,
    "canonical_lifecycle_performed": False,
    "custody_store_is_local": True,
    "may_be_promoted_to_canonical_closure": False,
    "authority_effect": "NONE_ENCLOSED_VALIDATION_ONLY",
}


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

    def _diagnostic_result(self):
        return {
            "schema": "stegverse.ecosystem-diagnostic-result.v1",
            "processing_capability": "ecosystem_diagnostic",
            "route_id": "stegverse.route.ecosystem-diagnostic.v1",
            "results": [{
                "test_id": "ece:sdk:route_installed",
                "component_id": "sdk",
                "predicate_id": "route_installed",
                "observation_state": "PASS",
                "evidence_refs": ["receipt:abc"],
            }],
            "mutation_performed": False,
            "authority_effect": "NONE_DIAGNOSTIC_ONLY",
            "continuity_state_present": False,
        }

    def test_current_sdk_enclosed_diagnostic_output_is_read_through_its_local_label(self):
        enclosed = {
            "canonical_entrypoint": "stegverse.manifest_execution.execute_manifest",
            "local_operation": "ecosystem_diagnostic",
            "sdk_execution_lane": dict(SDK_LOCAL_ENCLOSED_LANE),
            "result": self._diagnostic_result(),
        }
        translated = MOD._ece_observations_from_diagnostic(enclosed, "d" * 64)
        row = translated["observations"][0]
        self.assertEqual(row["state"], "PASS")
        self.assertIn("sdk-diagnostic-result-sha256:" + "d" * 64, row["evidence"])

    def test_enclosed_output_that_is_not_this_operation_or_claims_authority_fails_closed(self):
        cases = {
            "other_operation": {"local_operation": "replay"},
            "authorizing": {"sdk_execution_lane": dict(SDK_LOCAL_ENCLOSED_LANE, authorizing=True)},
            "canonical": {"sdk_execution_lane": dict(SDK_LOCAL_ENCLOSED_LANE, canonical=True)},
            "other_lane": {"sdk_execution_lane": dict(SDK_LOCAL_ENCLOSED_LANE, lane="CANONICAL")},
            "lane_missing": {"sdk_execution_lane": None},
            "result_missing": {"result": None},
        }
        for name, change in cases.items():
            with self.subTest(name):
                enclosed = {
                    "local_operation": "ecosystem_diagnostic",
                    "sdk_execution_lane": dict(SDK_LOCAL_ENCLOSED_LANE),
                    "result": self._diagnostic_result(),
                }
                enclosed.update(change)
                with self.assertRaisesRegex(ValueError, "SDK_DIAGNOSTIC_RESULT_ENCLOSURE_INVALID"):
                    MOD._ece_observations_from_diagnostic(enclosed, "e" * 64)


if __name__ == "__main__":
    unittest.main()
