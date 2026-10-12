import hashlib
import json
import unittest
from copy import deepcopy

from app.manifest_remediation_intake import (
    classify_sdk_deny,
    classify_sdk_source_profile_deny,
)


def _request():
    return {
        "request_sha256": "a" * 64,
        "wire_manifest_sha256": "b" * 64,
        "canonical_manifest_sha256": "c" * 64,
        "graph_id": "graph-1",
        "processing_capability": "ecosystem_diagnostic",
        "canonical_manifest": {"payload": {"goal_task_id": "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003",
                                           "cosv": "50000000100000"}},
    }


def _denial(request):
    # Field values follow the SDK's source-profile DENY contract
    # (stegverse/manifest_state_transition_runtime.py::_validate_profile_source_deny).
    return {
        "schema": "stegverse.sdk.manifest-profile-disposition/v1",
        "state": "DENY", "disposition": "DENY", "terminal": False,
        "automatic_retry_permitted": False,
        "evaluation_boundary": "SDK_MANIFEST_PROFILE_SOURCE_ONLY",
        "authentic_intr_disposition_observed": False,
        "organization_master_records_organization_record_observed": False,
        "request_sha256": request["request_sha256"],
        "wire_manifest_sha256": request["wire_manifest_sha256"],
        "canonical_manifest_sha256": request["canonical_manifest_sha256"],
        "graph_id": request["graph_id"],
        "processing_capability": request["processing_capability"],
        "goal_task_id": "MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003",
        "cosv": "50000000100000",
        "reason_code": "ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED",
        "failed_predicate": "ECOSYSTEM_DIAGNOSTIC_NONWORKER_DISPATCH_UNWIRED",
        "transition_id": "SDK_ECOSYSTEM_DIAGNOSTIC_DISPATCH",
        "repair_owner": "EXISTING_SDK_ECOSYSTEM_DIAGNOSTIC_AND_STEGBROWSER_INTR_OWNERS",
        "retry_condition": "NEW_GOVERNED_ATTEMPT_AFTER_EXISTING_OWNER_DISPATCH_REPAIR",
        "source_disposition_ref": "runtime-state/sdk-manifest-state-transition/dispositions/verified-request.json",
        "evidence_refs": ["StegVerse-Labs/.github:workers/manifest_state_transition_intr_ingress.py"],
    }


class SourceProfileDenyClassificationTests(unittest.TestCase):
    def test_site_error_maps_to_resubmit_without_authority(self):
        request = _request()
        out = classify_sdk_source_profile_deny(_denial(request), request)
        self.assertEqual(out["suggested_action"], "RESUBMIT")
        self.assertEqual(out["failure_site"], "DENYING_SITE")
        self.assertEqual(out["site_repair_owner"],
                         "EXISTING_SDK_ECOSYSTEM_DIAGNOSTIC_AND_STEGBROWSER_INTR_OWNERS")
        self.assertEqual(out["governance_disposition"], "NOT_EVALUATED")
        self.assertFalse(out["execution_authority_granted"])
        self.assertEqual(out["authority_effect"], "NONE_CLASSIFICATION_ONLY")
        self.assertEqual(out["original_request_document_sha256"], hashlib.sha256(json.dumps(
            request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest())

    def test_unmapped_retry_condition_goes_to_governance_review(self):
        request = _request()
        denial = _denial(request)
        denial["retry_condition"] = "SOMETHING_ELSE"
        self.assertEqual(classify_sdk_source_profile_deny(denial, request)["suggested_action"],
                         "GOVERNANCE_REVIEW_REQUIRED")

    def test_terminal_fail_closed_is_not_classified_for_retry(self):
        request = _request()
        denial = _denial(request)
        denial.update({"state": "FAIL_CLOSED", "disposition": "FAIL_CLOSED", "terminal": True})
        with self.assertRaisesRegex(ValueError, "NONTERMINAL_SDK_DENY_REQUIRED"):
            classify_sdk_source_profile_deny(denial, request)

    def test_request_substitution_rejected(self):
        request = _request()
        denial = _denial(request)
        for key in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
                    "graph_id", "processing_capability"):
            forged = deepcopy(denial)
            forged[key] = "forged"
            with self.assertRaisesRegex(ValueError, f"SDK_DENY_REQUEST_BINDING_MISMATCH:{key}"):
                classify_sdk_source_profile_deny(forged, request)

    def test_lineage_substitution_rejected(self):
        request = _request()
        denial = _denial(request)
        denial["cosv"] = "99999999999999"
        with self.assertRaisesRegex(ValueError, "SDK_DENY_ORIGINAL_LINEAGE_MISMATCH:cosv"):
            classify_sdk_source_profile_deny(denial, request)

    def test_authority_and_custody_escalation_rejected(self):
        request = _request()
        for key, expected in (("authentic_intr_disposition_observed", "SDK_DENY_AUTHENTICITY_ESCALATION"),
                              ("organization_master_records_organization_record_observed",
                               "SDK_DENY_ORGANIZATION_RECORD_ESCALATION"),
                              ("automatic_retry_permitted", "SDK_DENY_RETRY_CONTRACT_MISMATCH")):
            denial = _denial(request)
            denial[key] = True
            with self.assertRaisesRegex(ValueError, expected):
                classify_sdk_source_profile_deny(denial, request)

    def test_missing_evidence_rejected(self):
        request = _request()
        denial = _denial(request)
        denial["source_disposition_ref"] = ""
        with self.assertRaisesRegex(ValueError, "SDK_DENY_EVIDENCE_REQUIRED"):
            classify_sdk_source_profile_deny(denial, request)

    def test_boundary_dispatch(self):
        request = _request()
        self.assertEqual(classify_sdk_deny(_denial(request), request)["suggested_action"], "RESUBMIT")
        # A source-profile DENY cannot be relabelled as an envelope DENY.
        relabelled = _denial(request)
        relabelled["evaluation_boundary"] = "SDK_MANIFEST_PROFILE"
        with self.assertRaises(ValueError):
            classify_sdk_deny(relabelled, request)

    def test_every_non_allow_is_classified(self):
        request = _request()
        terminal = _denial(request)
        terminal.update({"state": "FAIL_CLOSED", "disposition": "FAIL_CLOSED", "terminal": True,
                         "evaluation_boundary": "SDK_ADMITTED_DIAGNOSTIC_CONSUMER_LOCAL",
                         "retry_condition": "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY"})
        out = classify_sdk_deny(terminal, request)
        self.assertEqual(out["suggested_action"], "RESUBMIT")
        self.assertTrue(out["terminal_attempt"])
        self.assertEqual(out["reentry"], "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY")
        self.assertFalse(out["automatic_retry_permitted"])
        self.assertFalse(out["execution_authority_granted"])
        unknown = _denial(request)
        unknown["evaluation_boundary"] = "SOME_OTHER_EVALUATOR"
        out = classify_sdk_deny(unknown, request)
        self.assertEqual(out["suggested_action"], "GOVERNANCE_REVIEW_REQUIRED")
        self.assertEqual(out["failed_predicate"], unknown["failed_predicate"])
        self.assertEqual(out["source_evaluation_boundary"], "SOME_OTHER_EVALUATOR")

    def test_unmapped_non_allow_still_binds_to_its_request(self):
        request = _request()
        forged = _denial(request)
        forged.update({"evaluation_boundary": "SOME_OTHER_EVALUATOR", "request_sha256": "f" * 64})
        with self.assertRaisesRegex(ValueError, "SDK_NON_ALLOW_REQUEST_BINDING_MISMATCH:request_sha256"):
            classify_sdk_deny(forged, request)
        escalated = _denial(request)
        escalated.update({"evaluation_boundary": "SOME_OTHER_EVALUATOR",
                          "authentic_intr_disposition_observed": True})
        with self.assertRaisesRegex(ValueError, "SDK_NON_ALLOW_AUTHENTICITY_ESCALATION"):
            classify_sdk_deny(escalated, request)

    def test_allow_is_not_a_remediation_input(self):
        request = _request()
        allowed = _denial(request)
        allowed["disposition"] = "ALLOW"
        with self.assertRaisesRegex(ValueError, "ALLOW_IS_NOT_A_REMEDIATION_INPUT"):
            classify_sdk_deny(allowed, request)

if __name__ == "__main__":
    unittest.main()
