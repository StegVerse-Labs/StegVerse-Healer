"""Non-authorizing intake of a manifest-selected remediation proposal.

The source proposal and manifest transition are evidence only. This adapter does
not dispatch, approve, correct a manifest, or mint an organization receipt.
"""
from __future__ import annotations

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
    # The actual SDK profile-DENY schema carries original_request_sha256,
    # original_wire_manifest_sha256 and claimed_request_sha256. It does not
    # carry a request_sha256 or canonical_manifest_sha256 field directly.
    if denial.get("original_request_sha256") != request.get("request_sha256"):
        raise ValueError("SDK_DENY_REQUEST_BINDING_MISMATCH:original_request_sha256")
    if denial.get("claimed_request_sha256") != request.get("request_sha256"):
        raise ValueError("SDK_DENY_REQUEST_BINDING_MISMATCH:claimed_request_sha256")
    if denial.get("original_wire_manifest_sha256") != request.get("canonical_manifest_sha256"):
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
