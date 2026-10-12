import unittest
import hashlib
import json
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
                   "wire_manifest_sha256": "c" * 64,
                   "graph_id": "graph", "processing_capability": "ecosystem_diagnostic"}
        denial = {**request, "schema": "stegverse.sdk.manifest-profile-disposition/v1",
                  "original_request_sha256": hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest(),
                  "claimed_request_sha256": request["request_sha256"],
                  "original_wire_manifest_sha256": request["wire_manifest_sha256"],
                  "state": "DENY", "disposition": "DENY", "terminal": False,
                  "automatic_retry_permitted": False, "evaluation_boundary": "SDK_MANIFEST_PROFILE",
                  "authentic_intr_admission_observed": False,
                  "source_disposition_ref": "source-deny", "reason_code": "binding_mismatch",
                  "failed_predicate": "binding_mismatch",
                  "retry_condition": "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT",
                  "transition_id": "SDK_MANIFEST_BINDING", "transport_validated": True,
                  "repair_owner": "StegVerse-org/StegVerse-SDK:stegverse/manifest_builder.py",
                  "authority_effect": "NONE_MANIFEST_PROFILE_DENY_ONLY"}
        return denial, request

    def test_classification_never_authorizes(self):
        denial, request = self.fixture()
        out = classify_sdk_manifest_deny(denial, request)
        self.assertEqual(out["suggested_action"], "RE_MANIFEST")
        self.assertEqual(out["governance_disposition"], "NOT_EVALUATED")
        self.assertFalse(out["execution_authority_granted"])
        self.assertEqual(out["original_request_sha256"], request["request_sha256"])
        self.assertEqual(out["original_request_document_sha256"], denial["original_request_sha256"])
        self.assertEqual(out["original_wire_manifest_sha256"], request["wire_manifest_sha256"])

    def test_canonical_projection_differs_from_wire_and_is_not_used_as_wire(self):
        denial, request = self.fixture()
        self.assertNotEqual(request["canonical_manifest_sha256"], request["wire_manifest_sha256"])
        self.assertEqual(classify_sdk_manifest_deny(denial, request)["state"], "DETECTED")
        altered_request = {**request, "wire_manifest_sha256": request["canonical_manifest_sha256"]}
        altered_denial = dict(denial)
        altered_denial["original_request_sha256"] = hashlib.sha256(json.dumps(
            altered_request, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(ValueError, "original_wire_manifest_sha256"):
            classify_sdk_manifest_deny(altered_denial, altered_request)

    def test_missing_request_wire_identity_fails_closed(self):
        denial, request = self.fixture()
        request.pop("wire_manifest_sha256")
        with self.assertRaisesRegex(ValueError, "SDK_DENY_REQUEST_FIELD_REQUIRED:wire_manifest_sha256"):
            classify_sdk_manifest_deny(denial, request)

    def test_full_request_digest_is_not_embedded_claimed_digest(self):
        denial, request = self.fixture()
        self.assertNotEqual(denial["original_request_sha256"], request["request_sha256"])
        self.assertEqual(classify_sdk_manifest_deny(denial, request)["state"], "DETECTED")
        altered = dict(denial)
        altered["original_request_sha256"] = request["request_sha256"]
        with self.assertRaisesRegex(ValueError, "original_request_sha256"):
            classify_sdk_manifest_deny(altered, request)

    def test_reject_request_substitution(self):
        denial, request = self.fixture()
        with self.assertRaisesRegex(ValueError, "SDK_DENY_REQUEST_BINDING_MISMATCH"):
            classify_sdk_manifest_deny(denial, {**request, "request_sha256": "c" * 64})

    def test_reject_wire_manifest_substitution(self):
        denial, request = self.fixture()
        denial["original_wire_manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "SDK_DENY_REQUEST_BINDING_MISMATCH"):
            classify_sdk_manifest_deny(denial, request)

    def test_reject_claimed_request_substitution(self):
        denial, request = self.fixture()
        denial["claimed_request_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "SDK_DENY_REQUEST_BINDING_MISMATCH"):
            classify_sdk_manifest_deny(denial, request)

    def test_cannot_reclassify_arbitrary_transition_as_sdk_binding_deny(self):
        denial, request = self.fixture()
        denial["transition_id"] = "ARBITRARY_TRANSITION"
        with self.assertRaisesRegex(ValueError, "SDK_DENY_CONTRACT_MISMATCH:transition_id"):
            classify_sdk_manifest_deny(denial, request)

    def test_cannot_promote_unvalidated_transport(self):
        denial, request = self.fixture()
        denial["transport_validated"] = False
        with self.assertRaisesRegex(ValueError, "SDK_DENY_CONTRACT_MISMATCH:transport_validated"):
            classify_sdk_manifest_deny(denial, request)

    def test_cannot_reassign_repair_owner(self):
        denial, request = self.fixture()
        denial["repair_owner"] = "caller"
        with self.assertRaisesRegex(ValueError, "SDK_DENY_CONTRACT_MISMATCH:repair_owner"):
            classify_sdk_manifest_deny(denial, request)

    def test_cannot_promote_authority_effect(self):
        denial, request = self.fixture()
        denial["authority_effect"] = "ALLOW"
        with self.assertRaisesRegex(ValueError, "SDK_DENY_CONTRACT_MISMATCH:authority_effect"):
            classify_sdk_manifest_deny(denial, request)

    def test_reason_and_predicate_must_match(self):
        denial, request = self.fixture()
        denial["failed_predicate"] = "different"
        with self.assertRaisesRegex(ValueError, "SDK_DENY_REASON_PREDICATE_MISMATCH"):
            classify_sdk_manifest_deny(denial, request)

    def test_terminal_deny_not_retried(self):
        denial, request = self.fixture()
        denial["terminal"] = True
        with self.assertRaisesRegex(ValueError, "NONTERMINAL_SDK_DENY_REQUIRED"):
            classify_sdk_manifest_deny(denial, request)

    def test_reject_authenticity_escalation(self):
        denial, request = self.fixture()
        denial["authentic_intr_admission_observed"] = True
        with self.assertRaisesRegex(ValueError, "SDK_DENY_BOUNDARY_ESCALATION"):
            classify_sdk_manifest_deny(denial, request)

if __name__ == "__main__":
    unittest.main()
