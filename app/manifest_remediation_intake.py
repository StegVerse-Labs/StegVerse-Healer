"""Non-authorizing intake of a manifest-selected remediation proposal.

The source proposal and manifest transition are evidence only. This adapter does
not dispatch, approve, correct a manifest, or mint an organization receipt.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

SCHEMA = "stegverse.healer.manifest-remediation-intake/v1"


def ingest_manifest_remediation(proposal: Mapping[str, Any], manifest_transition: Mapping[str, Any]) -> dict[str, Any]:
    if proposal.get("schema") != "stegverse.remediation.manifest-transition-proposal/v1":
        raise ValueError("REMEDIATION_PROPOSAL_SCHEMA_REQUIRED")
    if proposal.get("failed_disposition") not in {"DENY", "FAIL_CLOSED"}:
        raise ValueError("NON_ALLOW_PREDECESSOR_REQUIRED")
    if proposal.get("approval_result") != "NOT_EVALUATED" or proposal.get("execution_authority_granted") is not False:
        raise ValueError("PROPOSAL_AUTHORITY_ESCALATION")
    if not isinstance(manifest_transition, Mapping) or proposal.get("manifest_transition") != dict(manifest_transition):
        raise ValueError("EXACT_MANIFEST_TRANSITION_BINDING_REQUIRED")
    if manifest_transition.get("transition_id") != proposal.get("proposed_transition_id"):
        raise ValueError("MANIFEST_TRANSITION_ID_MISMATCH")
    if manifest_transition.get("authority_effect") != "NONE_BINDING_ONLY":
        raise ValueError("MANIFEST_BINDING_AUTHORITY_ESCALATION")
    for key in ("canonical_manifest_sha256", "route_id", "processing_capability"):
        if not isinstance(manifest_transition.get(key), str) or not manifest_transition[key]:
            raise ValueError(f"MANIFEST_TRANSITION_FIELD_REQUIRED:{key}")
    return {
        "schema": SCHEMA,
        "task_id": proposal["task_id"],
        "cosv_id": proposal["cosv_id"],
        "failed_transition_id": proposal["failed_transition_id"],
        "proposed_transition_id": proposal["proposed_transition_id"],
        "manifest_transition": dict(manifest_transition),
        "correction_ref": proposal["correction_ref"],
        "governance_decision_ref": proposal["governance_decision_ref"],
        "state": "DETECTED",
        "next_action": "AWAIT_SEPARATE_MANIFEST_GOVERNANCE_ADMISSION",
        "governance_disposition": "NOT_EVALUATED",
        "recovery_verified": False,
        "execution_authority_granted": False,
        "authority_effect": "NONE_INTAKE_ONLY",
    }


def classify_sdk_manifest_deny(denial: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a source-level SDK DENY for governance; never authorize a retry.

    This is a non-authorizing Healer classification, not an InTr disposition or
    a replacement for the canonical organization .github decision interface.
    """
    if denial.get("schema") != "stegverse.sdk.manifest-profile-disposition/v1":
        raise ValueError("SDK_DENY_SCHEMA_REQUIRED")
    if (denial.get("state") != "DENY" or denial.get("disposition") != "DENY"
            or denial.get("terminal") is not False
            or denial.get("automatic_retry_permitted") is not False):
        raise ValueError("NONTERMINAL_SDK_DENY_REQUIRED")
    if (denial.get("evaluation_boundary") != "SDK_MANIFEST_PROFILE"
            or denial.get("authentic_intr_admission_observed") is not False):
        raise ValueError("SDK_DENY_BOUNDARY_ESCALATION")
    # Match the SDK's source-profile DENY invariants before recommending a
    # remediation action. Healer must not promote a caller-crafted DENY into
    # a governance candidate by checking hashes alone.
    required = {
        "transition_id": "SDK_MANIFEST_BINDING",
        "retry_condition": "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT",
        "transport_validated": True,
        "repair_owner": "StegVerse-org/StegVerse-SDK:stegverse/manifest_builder.py",
        "authority_effect": "NONE_MANIFEST_PROFILE_DENY_ONLY",
    }
    for key, value in required.items():
        if denial.get(key) != value:
            raise ValueError(f"SDK_DENY_CONTRACT_MISMATCH:{key}")
    observed_key = "organization_master_records_organization_record_observed"
    legacy_observed_key = "organization_master_records_closure_observed"
    observed = denial.get(observed_key, denial.get(legacy_observed_key))
    if observed is not False:
        raise ValueError("SDK_DENY_ORGANIZATION_RECORD_ESCALATION")
    if denial.get("failed_predicate") != denial.get("reason_code"):
        raise ValueError("SDK_DENY_REASON_PREDICATE_MISMATCH")
    for key in ("request_sha256", "wire_manifest_sha256", "graph_id", "processing_capability"):
        if not isinstance(request.get(key), str) or not request[key]:
            raise ValueError(f"SDK_DENY_REQUEST_FIELD_REQUIRED:{key}")
    # The actual SDK profile-DENY schema carries original_request_sha256,
    # original_wire_manifest_sha256 and claimed_request_sha256. It does not
    # carry a request_sha256 or canonical_manifest_sha256 field directly.
    # The SDK source-profile DENY distinguishes the digest of the *entire*
    # rejected request from its embedded claimed request_sha256. Match the SDK
    # canonical JSON hash contract, never equate these different identities.
    full_request_digest = hashlib.sha256(json.dumps(
        dict(request), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()
    if denial.get("original_request_sha256") != full_request_digest:
        raise ValueError("SDK_DENY_REQUEST_BINDING_MISMATCH:original_request_sha256")
    if denial.get("claimed_request_sha256") != request.get("request_sha256"):
        raise ValueError("SDK_DENY_REQUEST_BINDING_MISMATCH:claimed_request_sha256")
    # Original wire and canonical projection are distinct identities. A request
    # may legitimately have a different canonical_manifest_sha256. The source
    # DENY binds the *wire* bytes, never the normalized projection digest.
    if denial.get("original_wire_manifest_sha256") != request.get("wire_manifest_sha256"):
        raise ValueError("SDK_DENY_REQUEST_BINDING_MISMATCH:original_wire_manifest_sha256")
    for key in ("graph_id", "processing_capability"):
        if denial.get(key) != request.get(key):
            raise ValueError(f"SDK_DENY_REQUEST_BINDING_MISMATCH:{key}")
    if (not isinstance(denial.get("source_disposition_ref"), str)
            or not denial["source_disposition_ref"]
            or not isinstance(denial.get("reason_code"), str)
            or not denial["reason_code"]):
        raise ValueError("SDK_DENY_EVIDENCE_REQUIRED")
    return {
        "schema": "stegverse.healer.sdk-deny-classification/v1",
        "state": "DETECTED",
        "source_disposition_ref": denial["source_disposition_ref"],
        "original_request_sha256": request["request_sha256"],
        "original_request_document_sha256": full_request_digest,
        "original_wire_manifest_sha256": request["wire_manifest_sha256"],
        "reason_code": denial["reason_code"],
        "failed_predicate": denial.get("failed_predicate"),
        "suggested_action": "RE_MANIFEST" if denial.get("retry_condition") ==
            "CORRECT_ENVELOPE_IN_EXISTING_MANIFEST_BUILDER_THEN_NEW_GOVERNED_ATTEMPT"
            else "GOVERNANCE_REVIEW_REQUIRED",
        "governance_disposition": "NOT_EVALUATED",
        "execution_authority_granted": False,
        "next_action": "AWAIT_ORGANIZATION_GITHUB_GOVERNED_RETURN",
        "authority_effect": "NONE_CLASSIFICATION_ONLY",
    }


# Source-profile DENYs whose manifest stays valid: the failure was at the site
# that denied it, so once its owner repairs that site the unchanged manifest is
# resubmitted as a new governed attempt. Any other retry condition is not
# guessed at here; it goes to governance review.
_RESUBMIT_RETRY_CONDITIONS = frozenset({
    "NEW_GOVERNED_ATTEMPT_AFTER_EXISTING_OWNER_DISPATCH_REPAIR",
})


def _sha256_document(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(
        dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def classify_sdk_source_profile_deny(denial: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Classify an SDK source-profile DENY (error at the site of the deny).

    Mirrors the SDK's ``_validate_profile_source_deny`` contract. Maps to
    RESUBMIT of the unchanged manifest after the named owner repairs the denying
    site. Terminal FAIL_CLOSED is never classified for retry. Non-authorizing.
    """
    if denial.get("schema") != "stegverse.sdk.manifest-profile-disposition/v1":
        raise ValueError("SDK_DENY_SCHEMA_REQUIRED")
    if denial.get("state") != "DENY" or denial.get("disposition") != "DENY" or denial.get("terminal") is not False:
        raise ValueError("NONTERMINAL_SDK_DENY_REQUIRED")
    if denial.get("automatic_retry_permitted") is not False:
        raise ValueError("SDK_DENY_RETRY_CONTRACT_MISMATCH")
    if denial.get("evaluation_boundary") != "SDK_MANIFEST_PROFILE_SOURCE_ONLY":
        raise ValueError("SDK_DENY_BOUNDARY_ESCALATION")
    if denial.get("authentic_intr_disposition_observed") is not False:
        raise ValueError("SDK_DENY_AUTHENTICITY_ESCALATION")
    observed = denial.get("organization_master_records_organization_record_observed",
                          denial.get("organization_master_records_closure_observed"))
    if observed is not False:
        raise ValueError("SDK_DENY_ORGANIZATION_RECORD_ESCALATION")
    for key in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
                "graph_id", "processing_capability"):
        if not isinstance(request.get(key), str) or not request[key]:
            raise ValueError(f"SDK_DENY_REQUEST_FIELD_REQUIRED:{key}")
        if denial.get(key) != request[key]:
            raise ValueError(f"SDK_DENY_REQUEST_BINDING_MISMATCH:{key}")
    original = request.get("canonical_manifest")
    payload = original.get("payload") if isinstance(original, Mapping) else None
    if isinstance(payload, Mapping):
        for field in ("goal_task_id", "cosv"):
            if payload.get(field) != denial.get(field):
                raise ValueError(f"SDK_DENY_ORIGINAL_LINEAGE_MISMATCH:{field}")
    for key in ("reason_code", "failed_predicate", "transition_id", "repair_owner",
                "retry_condition", "source_disposition_ref"):
        if not isinstance(denial.get(key), str) or not denial[key]:
            raise ValueError("SDK_DENY_EVIDENCE_REQUIRED")
    if not isinstance(denial.get("evidence_refs"), list):
        raise ValueError("SDK_DENY_EVIDENCE_REQUIRED")
    resubmit = denial["retry_condition"] in _RESUBMIT_RETRY_CONDITIONS
    return {
        "schema": "stegverse.healer.sdk-deny-classification/v1",
        "state": "DETECTED",
        "source_disposition_ref": denial["source_disposition_ref"],
        "original_request_sha256": request["request_sha256"],
        "original_request_document_sha256": _sha256_document(request),
        "original_wire_manifest_sha256": request["wire_manifest_sha256"],
        "reason_code": denial["reason_code"],
        "failed_predicate": denial["failed_predicate"],
        "failure_site": "DENYING_SITE",
        "site_repair_owner": denial["repair_owner"],
        "suggested_action": "RESUBMIT" if resubmit else "GOVERNANCE_REVIEW_REQUIRED",
        "governance_disposition": "NOT_EVALUATED",
        "execution_authority_granted": False,
        "next_action": "AWAIT_ORGANIZATION_GITHUB_GOVERNED_RETURN",
        "authority_effect": "NONE_CLASSIFICATION_ONLY",
    }


def _classify_terminal_or_unmapped(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a non-ALLOW that no specific contract above covers.

    Every non-ALLOW reaches Healer. Bindings the result carries must match the
    request; the failure is retained; an unmapped condition goes to governance
    review. A terminal FAIL_CLOSED is mapped but only for a separately governed
    re-entry, never an automatic retry.
    """
    for key in ("request_sha256", "wire_manifest_sha256", "canonical_manifest_sha256",
                "graph_id", "processing_capability"):
        if key in result and result.get(key) != request.get(key):
            raise ValueError(f"SDK_NON_ALLOW_REQUEST_BINDING_MISMATCH:{key}")
    for key in ("request_sha256", "wire_manifest_sha256"):
        if not isinstance(request.get(key), str) or not request[key]:
            raise ValueError(f"SDK_NON_ALLOW_REQUEST_FIELD_REQUIRED:{key}")
    for key in ("authentic_intr_disposition_observed", "authentic_intr_admission_observed"):
        if result.get(key) is True:
            raise ValueError("SDK_NON_ALLOW_AUTHENTICITY_ESCALATION")
    predicate = result.get("failed_predicate") or result.get("reason_code")
    if not isinstance(predicate, str) or not predicate:
        raise ValueError("SDK_NON_ALLOW_FAILED_PREDICATE_REQUIRED")
    terminal = result.get("disposition") == "FAIL_CLOSED"
    reentry_only = result.get("retry_condition") == "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY"
    return {
        "schema": "stegverse.healer.sdk-deny-classification/v1",
        "state": "DETECTED",
        "source_disposition": result.get("disposition"),
        "source_evaluation_boundary": result.get("evaluation_boundary"),
        "source_disposition_ref": result.get("source_disposition_ref") or "",
        "original_request_sha256": request["request_sha256"],
        "original_request_document_sha256": _sha256_document(request),
        "original_wire_manifest_sha256": request["wire_manifest_sha256"],
        "reason_code": result.get("reason_code") or predicate,
        "failed_predicate": predicate,
        "failure_site": "DENYING_SITE" if reentry_only else "UNMAPPED",
        "site_repair_owner": result.get("repair_owner"),
        "suggested_action": "RESUBMIT" if (terminal and reentry_only) else "GOVERNANCE_REVIEW_REQUIRED",
        "terminal_attempt": terminal,
        "reentry": "SEPARATELY_GOVERNED_FUTURE_REENTRY_ONLY" if terminal else "NEW_GOVERNED_ATTEMPT",
        "automatic_retry_permitted": False,
        "governance_disposition": "NOT_EVALUATED",
        "execution_authority_granted": False,
        "next_action": "AWAIT_ORGANIZATION_GITHUB_GOVERNED_RETURN",
        "authority_effect": "NONE_CLASSIFICATION_ONLY",
    }


def classify_sdk_deny(result: Mapping[str, Any], request: Mapping[str, Any]) -> dict[str, Any]:
    """Healer entry point for every SDK non-ALLOW (DENY or FAIL_CLOSED).

    SDK_MANIFEST_PROFILE envelope DENY -> RE_MANIFEST via the Manifest Builder;
    SDK_MANIFEST_PROFILE_SOURCE_ONLY site DENY -> RESUBMIT; terminal FAIL_CLOSED
    -> mapped for separately governed re-entry only; anything else -> retained
    and sent to governance review. Only an ALLOW is not classified here.
    """
    disposition = result.get("disposition")
    if disposition == "ALLOW":
        raise ValueError("ALLOW_IS_NOT_A_REMEDIATION_INPUT")
    if disposition not in ("DENY", "FAIL_CLOSED"):
        raise ValueError("SDK_NON_ALLOW_DISPOSITION_REQUIRED")
    boundary = result.get("evaluation_boundary")
    if disposition == "DENY" and result.get("terminal") is False:
        if boundary == "SDK_MANIFEST_PROFILE":
            return classify_sdk_manifest_deny(result, request)
        if boundary == "SDK_MANIFEST_PROFILE_SOURCE_ONLY":
            return classify_sdk_source_profile_deny(result, request)
    return _classify_terminal_or_unmapped(result, request)
