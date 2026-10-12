import unittest
from app.manifest_remediation_intake import ingest_manifest_remediation, classify_sdk_manifest_deny


def fixture():
    binding = {"transition_id": "remediate-002", "canonical_manifest_sha256": "a" * 64,
               "route_id": "manifest-selected", "processing_capability": "remediation",
               "authority_effect": "NONE_BINDING_ONLY"}
    proposal = {"schema": "stegverse.remediation.manifest-transition-proposal/v1",
                "task_id": "task", "cosv_id": "cosv", "failed_transition_id": "attempt-001",
                "failed_disposition": "DENY", "proposed_transition_id": "remediate-002",
                "correction_ref": "correction", "governance_decision_ref": "decision-request",
                "manifest_transition": binding, "approval_result": "NOT_EVALUATED",
                "execution_authority_granted": False}
    return proposal, binding


class ManifestIntakeTests(unittest.TestCase):
    def test_intake_is_non_authorizing(self):
        proposal, binding = fixture()
        result = ingest_manifest_remediation(proposal, binding)
        self.assertEqual(result["state"], "DETECTED")
        self.assertFalse(result["execution_authority_granted"])
        self.assertFalse(result["recovery_verified"])

    def test_reject_route_substitution(self):
        proposal, binding = fixture()
        with self.assertRaisesRegex(ValueError, "EXACT_MANIFEST_TRANSITION_BINDING_REQUIRED"):
            ingest_manifest_remediation(proposal, {**binding, "route_id": "alternate"})

    def test_reject_forged_approval(self):
        proposal, binding = fixture()
        proposal["approval_result"] = "ALLOW"
        with self.assertRaisesRegex(ValueError, "PROPOSAL_AUTHORITY_ESCALATION"):
            ingest_manifest_remediation(proposal, binding)



class SDKDenyClassificationTests(unittest.TestCase):
    def fixture(self):
        request = {"request_sha256": "a" * 64, "canonical_manifest_sha256": "b" * 64,
                   "graph_id": "graph", "processing_capability": "ecosystem_diagnostic"}
        denial = {**request, "schema": "stegverse.sdk.manifest-profile-disposition/v1",
                  "state": "DENY", "disposition": "DENY", "terminal": False,
                  "automatic_retry_permitted": False, "evaluation_boundary": "SDK_MANIFEST_PROFILE",
                  "authentic_intr_admission_observed": False,
                  "source_disposition_ref": "source-deny", "reason_code": "binding_mismatch",
                  "failed_predicate": "binding_mismatch",
                  "retry_condition": "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT"}
        return denial, request

    def test_classification_never_authorizes(self):
        denial, request = self.fixture()
        out = classify_sdk_manifest_deny(denial, request)
        self.assertEqual(out["suggested_action"], "RE_MANIFEST")
        self.assertEqual(out["governance_disposition"], "NOT_EVALUATED")
        self.assertFalse(out["execution_authority_granted"])
        self.assertEqual(out["original_request_sha256"], request["request_sha256"])

    def test_reject_request_substitution(self):
        denial, request = self.fixture()
        with self.assertRaisesRegex(ValueError, "SDK_DENY_REQUEST_BINDING_MISMATCH"):
            classify_sdk_manifest_deny(denial, {**request, "request_sha256": "c" * 64})

    def test_reject_authenticity_escalation(self):
        denial, request = self.fixture()
        denial["authentic_intr_admission_observed"] = True
        with self.assertRaisesRegex(ValueError, "SDK_DENY_BOUNDARY_ESCALATION"):
            classify_sdk_manifest_deny(denial, request)

if __name__ == "__main__":
    unittest.main()
