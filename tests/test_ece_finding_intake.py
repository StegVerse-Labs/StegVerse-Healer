import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ece_intake", ROOT / "app" / "ece_finding_intake.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def evaluation(state="FAIL"):
    return {
        "schema": "stegverse.ecosystem-continuity-evaluation.v1",
        "evaluation_id": "ece_0123456789abcdef01234567",
        "continuity_state": "INTERRUPTED",
        "authority_effect": "NONE_DIAGNOSTIC_ONLY",
        "findings": [{
            "finding_id": "ecef_0123456789abcdef01234567",
            "component_id": "intr",
            "predicate_id": "resident_route",
            "observation_state": state,
            "severity": "CRITICAL",
            "continuity_critical": True,
            "evidence": ["mr://ece/evidence/1"],
            "evidence_age_seconds": 2,
            "authority_owner": "Interlock/InTr",
            "remediation_class": "DISPATCHABLE",
            "remediation_state": "DETECTED",
        }],
    }


class IntakeTests(unittest.TestCase):
    def test_non_pass_finding_becomes_detected_intake_only(self):
        result = MOD.ingest(evaluation())
        self.assertEqual(result["authority_effect"], "NONE_INTAKE_ONLY")
        self.assertEqual(result["recovery_rule"], "LATER_INDEPENDENT_ECE_PASS_REQUIRED")
        self.assertEqual(len(result["items"]), 1)
        item = result["items"][0]
        self.assertEqual(item["healer_state"], "DETECTED")
        self.assertFalse(item["recovery_verified"])
        self.assertEqual(item["dispatch_authority_effect"], "NONE_INTAKE_ONLY")

    def test_pass_is_not_queued_as_repair(self):
        result = MOD.ingest(evaluation("PASS"))
        self.assertEqual(result["items"], [])

    def test_authorizing_evaluation_is_rejected(self):
        source = evaluation()
        source["authority_effect"] = "EXECUTE"
        with self.assertRaisesRegex(ValueError, "ECE_AUTHORITY_EFFECT_REJECTED"):
            MOD.ingest(source)

    def test_snapshot_is_deterministic(self):
        left = MOD.ingest(evaluation())["items"][0]["finding_snapshot_sha256"]
        right = MOD.ingest(evaluation())["items"][0]["finding_snapshot_sha256"]
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
