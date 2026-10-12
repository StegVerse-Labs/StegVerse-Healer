import unittest
from app.manifest_remediation_intake import ingest_manifest_remediation


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


if __name__ == "__main__":
    unittest.main()
