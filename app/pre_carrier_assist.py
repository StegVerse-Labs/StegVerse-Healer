from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

FORBIDDEN_CREDENTIALS = (
    "HEALER_GH_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "HEALER_PAT",
    "GH_STEGVERSE_AI_TOKEN",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "RENDER_API_KEY",
    "VERCEL_TOKEN",
    "CLOUDFLARE_API_TOKEN",
    "WALLET_PRIVATE_KEY",
    "PRIVATE_KEY",
)

REQUIRED_FILES = (
    "control/heartbeat-state.json",
    "heartbeat_runtime/engine_v12.py",
    "heartbeat_runtime/worker_runtime.py",
    "scripts/advance_heartbeat_transition.py",
    "management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json",
    "handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json",
    "control/worker-registry.json",
    "control/process-worker-adapters.json",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _roots() -> dict[str, Path]:
    raw = os.getenv("STEGVERSE_REPO_ROOTS_JSON", "").strip()
    if not raw:
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON is required")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON must be an object")
    roots: dict[str, Path] = {}
    for repo, value in parsed.items():
        if isinstance(repo, str) and isinstance(value, str):
            root = Path(value).expanduser().resolve()
            if root.is_dir():
                roots[repo] = root
    return roots


def _forbid_credentials() -> list[str]:
    return sorted(name for name in FORBIDDEN_CREDENTIALS if os.getenv(name))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_pre_carrier() -> dict[str, Any]:
    forbidden = _forbid_credentials()
    if forbidden:
        return {
            "schema": "stegverse.healer.pre_carrier_assist/v0.1",
            "state": "FAILED",
            "credential_authority": "TV/TVC",
            "credential_requirement": "NONE",
            "github_token_required": False,
            "non_tv_tvc_secret_or_token_used": False,
            "reason": "FORBIDDEN_CREDENTIAL_ENV_PRESENT",
            "forbidden": forbidden,
            "next_action": "remove forbidden credential material and retry the bounded local inspection",
        }

    roots = _roots()
    root = roots.get("StegVerse-Labs/.github")
    if root is None:
        return {
            "schema": "stegverse.healer.pre_carrier_assist/v0.1",
            "state": "BLOCKED",
            "credential_authority": "TV/TVC",
            "credential_requirement": "NONE",
            "github_token_required": False,
            "non_tv_tvc_secret_or_token_used": False,
            "reason": "CANONICAL_GITHUB_REPOSITORY_NOT_MATERIALIZED",
            "next_action": "materialize the already-authorized StegVerse-Labs/.github source locally; do not use remote checkout as production transport",
        }

    missing = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing:
        return {
            "schema": "stegverse.healer.pre_carrier_assist/v0.1",
            "state": "BLOCKED",
            "credential_authority": "TV/TVC",
            "credential_requirement": "NONE",
            "github_token_required": False,
            "non_tv_tvc_secret_or_token_used": False,
            "reason": "REQUIRED_LOCAL_SOURCE_MISSING",
            "missing": missing,
            "next_action": "restore the canonical local source capsule through its existing StegVerse owner before G18 transition execution",
        }

    legacy_path = root / "control/heartbeat-state.json"
    contract_path = root / "management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json"
    handoff_path = root / "handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json"
    legacy = _load_json(legacy_path)
    contract = _load_json(contract_path)
    handoff = _load_json(handoff_path)

    checks = {
        "legacy_epoch_is_29": legacy.get("epoch") == 29,
        "legacy_generation_is_29": legacy.get("generation") == 29,
        "contract_legacy_epoch_is_29": contract.get("legacy_epoch") == 29,
        "contract_legacy_source_immutable": contract.get("legacy_source_immutable") is True,
        "contract_first_successor_is_30": contract.get("first_successor_epoch") == 30,
        "contract_runtime_is_v12": contract.get("canonical_runtime") == "heartbeat_runtime.engine_v12.HeartbeatRuntime",
        "contract_worker_is_separate": contract.get("worker_runtime") == "heartbeat_runtime.worker_runtime.WorkerCoordinator",
        "contract_transition_producer_matches": contract.get("transition_producer") == "scripts/advance_heartbeat_transition.py",
        "contract_no_extra_machine": contract.get("another_physical_machine_required") is False,
        "contract_no_always_on_host": contract.get("always_on_external_host_required") is False,
        "contract_tv_tvc_authority": (contract.get("credential_boundary") or {}).get("credential_authority") == "TV/TVC",
        "contract_no_non_tv_tvc_secret": (contract.get("credential_boundary") or {}).get("non_tv_tvc_secret_or_token_allowed") is False,
        "handoff_g18_owner": (handoff.get("task") or {}).get("claim_state") == "MACHINE_OWNED_BOUND_G18",
        "handoff_fence_18": (handoff.get("task") or {}).get("fencing_token") == 18,
        "handoff_live_activation_unclaimed": (handoff.get("completion") or {}).get("live_activation_claimed") is False,
    }

    failed = sorted(name for name, passed in checks.items() if not passed)
    state = "READY_FOR_G18_TRANSITION" if not failed else "REVIEW_REQUIRED"
    next_action = (
        "G18 executes scripts/advance_heartbeat_transition.py under its existing admitted claim/fence; Healer does not execute or synthesize the carrier transition"
        if state == "READY_FOR_G18_TRANSITION"
        else "reconcile the listed canonical contract mismatch before G18 transition execution"
    )

    return {
        "schema": "stegverse.healer.pre_carrier_assist/v0.1",
        "state": state,
        "credential_authority": "TV/TVC",
        "credential_requirement": "NONE",
        "github_token_required": False,
        "non_tv_tvc_secret_or_token_used": False,
        "authority_effect": "NONE",
        "heartbeat_transition_executed": False,
        "hb30_synthesized": False,
        "legacy_state_sha256": _sha256(legacy_path),
        "checks": checks,
        "failed_checks": failed,
        "next_action": next_action,
    }


def main() -> int:
    try:
        receipt = inspect_pre_carrier()
    except Exception as exc:
        receipt = {
            "schema": "stegverse.healer.pre_carrier_assist/v0.1",
            "state": "FAILED",
            "credential_authority": "TV/TVC",
            "credential_requirement": "NONE",
            "github_token_required": False,
            "non_tv_tvc_secret_or_token_used": False,
            "authority_effect": "NONE",
            "heartbeat_transition_executed": False,
            "error": str(exc),
        }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt.get("state") == "READY_FOR_G18_TRANSITION" else 3


if __name__ == "__main__":
    raise SystemExit(main())
