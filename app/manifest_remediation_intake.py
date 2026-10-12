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
