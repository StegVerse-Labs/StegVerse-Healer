from __future__ import annotations

"""Healer carrier for the neutral reusable-task scheduler.

Healer retains its ordinary sovereign scheduler and Healer-specific schedule/config,
but it no longer owns generic reusable-task selection, slot idempotency, retry/backoff,
or child invocation. Those semantics belong to RT-REUSABLE-TASK-SCHEDULER-001 in
StegVerse-Labs/.github. This module discovers already-local inputs, invokes that
neutral reusable task once per Healer cycle, and projects its authentic result.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import sovereign_scheduler as base

SCHEDULE_FILE = Path(__file__).resolve().parents[1] / "data" / "reusable_task_schedule.json"
SCHEDULE_SCHEMA = "stegverse.reusable-task-schedule/v1"
NEUTRAL_SCHEDULER_ID = "RT-REUSABLE-TASK-SCHEDULER-001"
NEUTRAL_TRIGGER_REL = Path("scripts/trigger_reusable_task.py")
SOURCE_REFRESH_TASK_ID = "RT-SOVEREIGN-SOURCE-REFRESH-001"
RUNTIME_ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"
ROOT_OBSERVATION_SCHEMA = "stegverse.healer.resident-custody-root-observation/v1"
ROOT_OBSERVATION_TASK_ID = "STEG-BROWSER-RESIDENT-CUSTODY-ROOT-OBSERVATION-001"
ROOT_OBSERVATION_COSV = "40000100100000"
ROOT_OBSERVATION_RECEIPT_REL = Path("receipts/sovereign-host/stegbrowser-resident-custody-root-observation.latest.json")
RUNTIME_REQUIRED_MARKERS = (
    Path("control/resident-execution-request.d/native-email-action-monitor-001.json"),
    Path("control/resident-execution-request.d/canonical-work-stegbrowser-runtime-consumption-001.json"),
    Path("control/resident-execution-request.d/stegbrowser-tvc-source-promotion-001.json"),
    Path("receipts/sovereign-host/canonical-work-stegbrowser-runtime-consumption-request-consumption.latest.json"),
)
RUNTIME_REQUIRED_REL = RUNTIME_REQUIRED_MARKERS[0]
KV_PATH_ENV_NAMES = ("STEGVERSE_KV_ROOT", "STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT")
SOURCE_PREP_SCHEMA = "stegverse.sv-dn1.production-source-prep-receipt/v2"
SOURCE_PREP_RECEIPT_ENV = "STEGVERSE_SV_DN1_SOURCE_PREP_RECEIPT"
SOURCE_PREP_DEFAULT = Path.home() / ".stegverse" / "state" / "sv-dn1-production-source-prep" / "receipts" / "latest.json"
SOURCE_PREP_TASK_ID = "SV-DN1-PRODUCTION-SOURCE-PREP-001"
SOURCE_PREP_WORKER_ID = "sv-dn1-production-source-prep-worker"
SOURCE_PREP_COSV = "50000000102000"
SOURCE_PREP_MIN_FENCE_EXCLUSIVE = 22
SOURCE_PREP_BRIDGE_REL = Path("scripts/refresh_and_execute_resident_task.py")
SOURCE_PREP_COMPONENTS = {
    "stegverse.sdk": ("StegVerse-org/StegVerse-SDK", Path("stegverse/sovereign_validation_runtime.py")),
    "stegverse.stegcore": ("StegVerse-Labs/StegCore", Path("src/stegcore/steggate_runtime.py")),
    "stegverse.core-lite": ("Data-Continuation/core-lite", Path("core_lite/transaction_route.py")),
    "stegverse.master-records": ("master-records/orchestration", Path("services/manifest_receipt_custody.py")),
}
SHA256_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


def _load_schedule(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != SCHEDULE_SCHEMA:
        raise ValueError("neutral reusable task schedule schema mismatch")
    tasks = value.get("tasks")
    if not isinstance(tasks, list) or not all(isinstance(row, dict) for row in tasks):
        raise ValueError("reusable task schedule tasks must be objects")
    return tasks


def _schedule_enables_source_refresh(path: Path) -> bool:
    return any(
        row.get("reusable_task_id") == SOURCE_REFRESH_TASK_ID and row.get("enabled") is True
        for row in _load_schedule(path)
    )


def _matched_runtime_markers(root: Path) -> list[str]:
    return [str(marker) for marker in RUNTIME_REQUIRED_MARKERS if (root / marker).is_file()]


def _valid_runtime_root(root: Path) -> bool:
    return root.is_dir() and bool(_matched_runtime_markers(root))


def _runtime_root_candidates() -> list[Path]:
    home = Path.home()
    return [
        home / ".local" / "state" / "stegverse" / "heartbeat-runtime",
        home / "Library" / "Application Support" / "stegverse" / "heartbeat-runtime",
        home / ".stegverse" / "heartbeat-runtime",
        Path("/var/lib/stegverse/heartbeat-runtime"),
        Path("/srv/stegverse/heartbeat-runtime"),
    ]


def _resident_runtime_root() -> tuple[Path | None, str]:
    raw = str(os.getenv(RUNTIME_ROOT_ENV) or "").strip()
    if raw:
        root = Path(raw).expanduser().resolve()
        return (root, "EXPLICIT_NONSECRET_RUNTIME_ROOT") if _valid_runtime_root(root) else (None, "EXPLICIT_RUNTIME_ROOT_INVALID")

    valid: list[Path] = []
    for candidate in _runtime_root_candidates():
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        if _valid_runtime_root(resolved):
            valid.append(resolved)
    unique = list(dict.fromkeys(str(path) for path in valid))
    if len(unique) == 1:
        return Path(unique[0]), "CANONICAL_LOCAL_RUNTIME_DISCOVERY"
    if len(unique) > 1:
        return None, "CANONICAL_RUNTIME_AMBIGUOUS"
    return None, "CANONICAL_RUNTIME_NOT_FOUND"


def _resident_runtime_materialization_target(schedule_path: Path, runtime_root_source: str) -> tuple[Path | None, str]:
    if runtime_root_source == "CANONICAL_RUNTIME_AMBIGUOUS":
        return None, runtime_root_source
    if not _schedule_enables_source_refresh(schedule_path):
        return None, "SOURCE_REFRESH_NOT_ENABLED_FOR_MATERIALIZATION"

    raw = str(os.getenv(RUNTIME_ROOT_ENV) or "").strip()
    if raw:
        return Path(raw).expanduser().resolve(), "EXPLICIT_NONSECRET_RUNTIME_ROOT_MATERIALIZATION_TARGET"

    candidates = _runtime_root_candidates()
    mac_parent = Path.home() / "Library" / "Application Support"
    target = candidates[1] if mac_parent.is_dir() else candidates[0]
    return target.expanduser().resolve(), "CANONICAL_LOCAL_RUNTIME_MATERIALIZATION_TARGET"


def _resident_custody_root_observation(runtime_root: Path | None, runtime_root_source: str) -> dict[str, Any]:
    if runtime_root is not None:
        matched = _matched_runtime_markers(runtime_root)
        state = "RESIDENT_CUSTODY_ROOT_OBSERVED" if matched else "RESIDENT_CUSTODY_ROOT_INVALID"
        root_ref = str(runtime_root)
    elif runtime_root_source == "CANONICAL_RUNTIME_AMBIGUOUS":
        matched = []
        state = "RESIDENT_CUSTODY_ROOT_AMBIGUOUS"
        root_ref = None
    elif runtime_root_source == "EXPLICIT_RUNTIME_ROOT_INVALID":
        matched = []
        state = "RESIDENT_CUSTODY_ROOT_INVALID"
        root_ref = None
    else:
        matched = []
        state = "RESIDENT_CUSTODY_ROOT_NOT_OBSERVED"
        root_ref = None
    return {
        "schema": ROOT_OBSERVATION_SCHEMA,
        "task_id": ROOT_OBSERVATION_TASK_ID,
        "cosv_task_vector": ROOT_OBSERVATION_COSV,
        "state": state,
        "resident_runtime_root": root_ref,
        "resident_runtime_root_source": runtime_root_source,
        "matched_marker_relative_paths": matched,
        "required_first_receipt_relative_path": "receipts/sovereign-host/canonical-work-stegbrowser-runtime-consumption-request-consumption.latest.json",
        "authority_effect": "NONE_OBSERVATION_ONLY",
        "healer_carrier_authority": "SCHEDULING_AND_INVOCATION_TRANSPORT_ONLY",
        "github_runtime_authority": "NONE",
        "credential_authority": "TV/TVC",
        "workercoordinator_bypass_created": False,
        "second_scheduler_created": False,
        "second_user_operated_device_required": False,
        "runtime_completion_claimed": False,
    }


def _retain_resident_custody_root_observation(
    observation: dict[str, Any],
    *,
    retain_root: Path | None,
    retain_root_source: str,
    now,
) -> dict[str, Any]:
    base_result = {
        "schema": "stegverse.healer.resident-custody-root-observation-retention/v1",
        "task_id": ROOT_OBSERVATION_TASK_ID,
        "cosv_task_vector": ROOT_OBSERVATION_COSV,
        "packet_name": "resident_custody_root_observation",
        "authority_effect": "NONE_RETENTION_ONLY",
        "github_runtime_authority": "NONE",
        "credential_authority": "TV/TVC",
        "runtime_completion_claimed": False,
        "request_consumption_claimed": False,
        "workercoordinator_bypass_created": False,
        "second_scheduler_created": False,
        "second_user_operated_device_required": False,
    }
    if retain_root is None:
        return {**base_result, "state": "NOT_RETAINED", "reason": "NO_RESIDENT_RUNTIME_ROOT_OR_MATERIALIZATION_TARGET"}

    retained_packet = {
        **observation,
        "retained_packet": True,
        "retained_at": now.isoformat().replace("+00:00", "Z"),
        "retained_under_root_source": retain_root_source,
        "retention_authority_effect": "NONE_RETENTION_ONLY",
        "request_consumption_claimed": False,
    }
    payload = json.dumps(retained_packet, sort_keys=True, separators=(",", ":")) + "\n"
    packet_path = retain_root / ROOT_OBSERVATION_RECEIPT_REL
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(payload, encoding="utf-8")
    return {
        **base_result,
        "state": "RETAINED",
        "packet_ref": str(packet_path),
        "packet_relative_path": str(ROOT_OBSERVATION_RECEIPT_REL),
        "packet_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "retained_under_root": str(retain_root),
        "retained_under_root_source": retain_root_source,
        "packet_state": observation.get("state"),
    }


def _kv_path_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for name in KV_PATH_ENV_NAMES:
        raw = str(os.getenv(name) or "").strip()
        if raw:
            values[name] = raw
    return values


def _source_prep_receipt_path() -> Path:
    raw = str(os.getenv(SOURCE_PREP_RECEIPT_ENV) or "").strip()
    return Path(raw).expanduser().resolve() if raw else SOURCE_PREP_DEFAULT.expanduser().resolve()


def _verified_governance_component_roots() -> tuple[dict[str, Path], str]:
    path = _source_prep_receipt_path()
    if not path.is_file():
        return {}, "SV_DN1_SOURCE_PREP_RECEIPT_NOT_PRESENT"
    try:
        value = base._load_json(path)
    except Exception:
        return {}, "SV_DN1_SOURCE_PREP_RECEIPT_INVALID_JSON"
    required = {
        "schema": SOURCE_PREP_SCHEMA,
        "state": "COMPLETE",
        "transition_id": "SV_DN1_PRODUCTION_SOURCE_PREPARATION_COMPLETE",
        "task_id": SOURCE_PREP_TASK_ID,
        "worker_id": SOURCE_PREP_WORKER_ID,
        "source_identity_scheme": "sha256-content-manifest",
        "migration_anchors_verified": True,
        "current_source_identity_verified": True,
        "current_source_identity_scheme": "sha256-content-manifest",
        "network_source_fetch_performed": False,
        "github_platform_required": False,
        "credential_used": False,
        "github_token_used": False,
        "repository_writeback_performed": False,
    }
    if any(value.get(key) != expected for key, expected in required.items()):
        return {}, "SV_DN1_SOURCE_PREP_RECEIPT_NOT_ADMISSIBLE"
    claim_id = value.get("claim_id")
    fencing_token = value.get("fencing_token")
    if not isinstance(claim_id, str) or not claim_id.strip():
        return {}, "SV_DN1_SOURCE_PREP_CLAIM_ID_MISSING"
    if not isinstance(fencing_token, int) or fencing_token <= SOURCE_PREP_MIN_FENCE_EXCLUSIVE:
        return {}, "SV_DN1_SOURCE_PREP_FENCING_TOKEN_INVALID"
    roots = value.get("source_roots")
    identities = value.get("source_identities")
    if not isinstance(roots, dict) or not isinstance(identities, dict):
        return {}, "SV_DN1_SOURCE_PREP_ROOTS_OR_IDENTITIES_MISSING"
    if set(roots) != set(SOURCE_PREP_COMPONENTS) or set(identities) != set(SOURCE_PREP_COMPONENTS):
        return {}, "SV_DN1_SOURCE_PREP_COMPONENT_SET_MISMATCH"
    resolved: dict[str, Path] = {}
    for component_id, (repository, marker) in SOURCE_PREP_COMPONENTS.items():
        identity = identities.get(component_id)
        raw_root = roots.get(component_id)
        if not isinstance(identity, str) or not SHA256_ID.fullmatch(identity):
            return {}, f"SV_DN1_SOURCE_PREP_IDENTITY_INVALID:{component_id}"
        if not isinstance(raw_root, str) or not raw_root.strip():
            return {}, f"SV_DN1_SOURCE_PREP_ROOT_INVALID:{component_id}"
        root = Path(raw_root).expanduser().resolve()
        if not root.is_dir() or not (root / marker).is_file():
            return {}, f"SV_DN1_SOURCE_PREP_ROOT_NOT_MATERIALIZED:{component_id}"
        resolved[repository] = root
    return resolved, "SV_DN1_SOURCE_PREP_RECEIPT_VERIFIED"


def _source_prep_locator_env(roots: dict[str, Path]) -> dict[str, str]:
    mapping = {
        "STEGVERSE_SDK_SOURCE_ROOT": "StegVerse-org/StegVerse-SDK",
        "STEGVERSE_STEGCORE_SOURCE_ROOT": "StegVerse-Labs/StegCore",
        "STEGVERSE_CORE_LITE_SOURCE_ROOT": "Data-Continuation/core-lite",
        "STEGVERSE_MASTER_RECORDS_SOURCE_ROOT": "master-records/orchestration",
    }
    return {
        env_name: str(roots[repository])
        for env_name, repository in mapping.items()
        if repository in roots and roots[repository].is_dir()
    }


def _invoke_existing_source_prep_bridge(
    *,
    roots: dict[str, Path],
    runtime_root: Path | None,
    runtime_root_source: str,
) -> dict[str, Any]:
    base_result = {
        "task_id": SOURCE_PREP_TASK_ID,
        "cosv_task_vector": SOURCE_PREP_COSV,
        "runtime_root_source": runtime_root_source,
        "existing_bridge_ref": str(SOURCE_PREP_BRIDGE_REL),
        "new_scheduler_created": False,
        "new_dispatcher_created": False,
        "new_workercoordinator_created": False,
        "authority_effect": "EXISTING_ADMITTED_TASK_AUTHORITY_ONLY",
    }
    github_root = roots.get("StegVerse-Labs/.github")
    if github_root is None:
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "LOCAL_DOTGITHUB_SOURCE_NOT_MATERIALIZED"}
    if runtime_root is None:
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED"}
    bridge = github_root / SOURCE_PREP_BRIDGE_REL
    if not bridge.is_file():
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "EXISTING_TARGETED_RESIDENT_BRIDGE_NOT_MATERIALIZED"}

    command = [
        sys.executable,
        str(bridge),
        "--source-root", str(github_root),
        "--runtime-root", str(runtime_root),
        "--task-id", SOURCE_PREP_TASK_ID,
        "--cosv-task-vector", SOURCE_PREP_COSV,
    ]
    env = {
        RUNTIME_ROOT_ENV: str(runtime_root),
        **_source_prep_locator_env(roots),
    }
    execution = base._run(command, github_root, env, timeout=1200)
    prepared_roots, source_prep_state = _verified_governance_component_roots()
    return {
        **base_result,
        "state": "SOURCE_PREP_RECEIPT_VERIFIED" if prepared_roots else "BOUNDARY_RECORDED",
        "command": command,
        "execution": execution,
        "source_prep_state": source_prep_state,
        "verified_component_repositories": sorted(prepared_roots),
        "runtime_execution_attempted": True,
    }


def _neutral_scheduler_invocation_id(now) -> str:
    return f"healer-neutral-reusable-scheduler-{now.strftime('%Y%m%dT%H%M%SZ')}"


def _invoke_neutral_scheduler(
    *,
    roots: dict[str, Path],
    runtime_root: Path | None,
    runtime_root_source: str,
    schedule_path: Path,
    now,
    scope: str,
) -> dict[str, Any]:
    github_root = roots.get("StegVerse-Labs/.github")
    base_result: dict[str, Any] = {
        "reusable_task_id": NEUTRAL_SCHEDULER_ID,
        "runtime_root_source": runtime_root_source,
        "schedule_path": str(schedule_path),
        "authority_effect": "NONE_CARRIER_DELEGATION_ONLY",
    }
    if github_root is None:
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "LOCAL_DOTGITHUB_SOURCE_NOT_MATERIALIZED"}
    if runtime_root is None:
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED"}
    trigger = github_root / NEUTRAL_TRIGGER_REL
    if not trigger.is_file():
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "NEUTRAL_REUSABLE_TASK_TRIGGER_NOT_MATERIALIZED"}
    if not schedule_path.is_file():
        return {**base_result, "state": "BOUNDARY_RECORDED", "boundary": "HEALER_REUSABLE_TASK_SCHEDULE_NOT_MATERIALIZED"}
    _load_schedule(schedule_path)

    invocation_id = _neutral_scheduler_invocation_id(now)
    receipt_path = runtime_root / "receipts" / "reusable-task" / f"{invocation_id}.latest.json"
    result_path = receipt_path.with_name(f"{invocation_id}.runner-result.json")
    roots_json = json.dumps({repo: str(path) for repo, path in sorted(roots.items())}, sort_keys=True)
    parameters = {
        "schedule_path": str(schedule_path.resolve()),
        "runtime_root": str(runtime_root),
        "repo_roots_json": roots_json,
        "now_utc": now.isoformat().replace("+00:00", "Z"),
        "scope": scope,
    }
    command = [
        sys.executable,
        str(trigger),
        "--reusable-task-id", NEUTRAL_SCHEDULER_ID,
        "--invocation-id", invocation_id,
        "--parameters-json", json.dumps(parameters, sort_keys=True, separators=(",", ":")),
        "--receipt", str(receipt_path),
    ]
    env = {
        "STEGVERSE_REPO_ROOTS_JSON": roots_json,
        RUNTIME_ROOT_ENV: str(runtime_root),
        **_kv_path_env(),
    }
    execution = base._run(command, github_root, env, timeout=1800)
    trigger_receipt = base._load_json(receipt_path) if receipt_path.is_file() else None
    runner_result = base._load_json(result_path) if result_path.is_file() else None
    return {
        **base_result,
        "state": "DELEGATED" if execution.get("returncode") == 0 and isinstance(runner_result, dict) else "BOUNDARY_RECORDED",
        "invocation_id": invocation_id,
        "receipt_ref": str(receipt_path),
        "runner_result_ref": str(result_path),
        "execution": execution,
        "trigger_receipt": trigger_receipt,
        "runner_result": runner_result,
        "neutral_scheduler_execution_observed": isinstance(runner_result, dict),
    }


def build_and_execute(config_path: Path, schedule_path: Path = SCHEDULE_FILE) -> dict[str, Any]:
    receipt = base.build_and_execute(config_path)
    roots = base._repo_roots()
    scope = (os.getenv("RUN_SCOPE") or "all").strip().lower()
    now = base._now()

    pre_runtime_root, pre_runtime_root_source = _resident_runtime_root()
    invocation_runtime_root = pre_runtime_root
    invocation_runtime_root_source = pre_runtime_root_source
    if invocation_runtime_root is None:
        materialization_target, materialization_source = _resident_runtime_materialization_target(
            schedule_path,
            pre_runtime_root_source,
        )
        if materialization_target is not None:
            invocation_runtime_root = materialization_target
            invocation_runtime_root_source = materialization_source

    prepared_roots, source_prep_state = _verified_governance_component_roots()
    source_prep_bridge = {
        "task_id": SOURCE_PREP_TASK_ID,
        "state": "NOT_REQUIRED_RECEIPT_ALREADY_VERIFIED",
        "source_prep_state": source_prep_state,
        "authority_effect": "NONE",
    }
    if not prepared_roots:
        source_prep_bridge = _invoke_existing_source_prep_bridge(
            roots=roots,
            runtime_root=invocation_runtime_root,
            runtime_root_source=invocation_runtime_root_source,
        )
        prepared_roots, source_prep_state = _verified_governance_component_roots()
    for repository, path in prepared_roots.items():
        roots.setdefault(repository, path)

    delegation = _invoke_neutral_scheduler(
        roots=roots,
        runtime_root=invocation_runtime_root,
        runtime_root_source=invocation_runtime_root_source,
        schedule_path=schedule_path,
        now=now,
        scope=scope,
    )

    runtime_root, runtime_root_source = _resident_runtime_root()
    root_observation = _resident_custody_root_observation(runtime_root, runtime_root_source)
    retain_root = runtime_root if runtime_root is not None else invocation_runtime_root
    retain_root_source = runtime_root_source if runtime_root is not None else invocation_runtime_root_source
    retention = _retain_resident_custody_root_observation(
        root_observation,
        retain_root=retain_root,
        retain_root_source=retain_root_source,
        now=now,
    )
    runner_result = delegation.get("runner_result") if isinstance(delegation, dict) else None
    outcomes = runner_result.get("outcomes", []) if isinstance(runner_result, dict) else []

    receipt["reusable_task_schedule_schema"] = SCHEDULE_SCHEMA
    receipt["reusable_task_scheduler_owner"] = NEUTRAL_SCHEDULER_ID
    receipt["healer_scheduler_role"] = "CONSUMER_CARRIER_ONLY"
    receipt["selected_reusable_tasks"] = len(outcomes) if isinstance(outcomes, list) else 0
    receipt["reusable_task_schedule"] = outcomes if isinstance(outcomes, list) else []
    receipt["neutral_reusable_task_scheduler"] = delegation
    receipt["resident_custody_root_observation"] = root_observation
    receipt["resident_custody_root_observation_retention"] = retention
    receipt["resident_runtime_root"] = str(runtime_root) if runtime_root is not None else None
    receipt["resident_runtime_root_source"] = runtime_root_source
    receipt["resident_runtime_root_pre_delegation"] = str(pre_runtime_root) if pre_runtime_root is not None else None
    receipt["resident_runtime_root_pre_delegation_source"] = pre_runtime_root_source
    receipt["resident_runtime_materialization_target"] = (
        str(invocation_runtime_root)
        if pre_runtime_root is None and invocation_runtime_root is not None
        else None
    )
    receipt["resident_runtime_materialization_target_source"] = (
        invocation_runtime_root_source
        if pre_runtime_root is None and invocation_runtime_root is not None
        else None
    )
    receipt["kv_path_env_available"] = sorted(_kv_path_env())
    receipt["sv_dn1_source_prep_state"] = source_prep_state
    receipt["sv_dn1_source_prep_existing_bridge"] = source_prep_bridge
    receipt["sv_dn1_governance_component_roots_added"] = sorted(prepared_roots)
    if receipt.get("state") == "COMPLETE" and (
        delegation.get("state") == "BOUNDARY_RECORDED"
        or root_observation.get("state") != "RESIDENT_CUSTODY_ROOT_OBSERVED"
    ):
        receipt["state"] = "BLOCKED"
    return receipt


def main() -> int:
    config_path = Path(os.getenv("TARGETS_FILE", "data/orchestrator_targets.json")).resolve()
    schedule_path = Path(os.getenv("REUSABLE_TASK_SCHEDULE_FILE", str(SCHEDULE_FILE))).resolve()
    try:
        receipt = build_and_execute(config_path, schedule_path)
    except Exception as exc:
        receipt = {
            "schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1",
            "state": "FAILED",
            "credential_authority": "TV/TVC",
            "github_token_required": False,
            "reusable_task_scheduler_owner": NEUTRAL_SCHEDULER_ID,
            "healer_scheduler_role": "CONSUMER_CARRIER_ONLY",
            "resident_custody_root_observation": {
                "schema": ROOT_OBSERVATION_SCHEMA,
                "task_id": ROOT_OBSERVATION_TASK_ID,
                "cosv_task_vector": ROOT_OBSERVATION_COSV,
                "state": "RESIDENT_CUSTODY_ROOT_OBSERVATION_FAILED",
                "authority_effect": "NONE_OBSERVATION_ONLY",
                "github_runtime_authority": "NONE",
                "credential_authority": "TV/TVC",
                "runtime_completion_claimed": False,
            },
            "resident_custody_root_observation_retention": {
                "schema": "stegverse.healer.resident-custody-root-observation-retention/v1",
                "task_id": ROOT_OBSERVATION_TASK_ID,
                "cosv_task_vector": ROOT_OBSERVATION_COSV,
                "state": "NOT_RETAINED",
                "reason": "CARRIER_EXCEPTION_BEFORE_RETENTION",
                "authority_effect": "NONE_RETENTION_ONLY",
                "github_runtime_authority": "NONE",
                "credential_authority": "TV/TVC",
                "runtime_completion_claimed": False,
            },
            "error": str(exc),
        }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
