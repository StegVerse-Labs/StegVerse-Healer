from __future__ import annotations

"""Extend the existing sovereign Healer scheduler with reusable-task schedules.

This module is not a second scheduler. It is the single Healer scheduler entrypoint
with an additional data-driven reusable-task schedule pass. Each successful schedule
slot is idempotent by invocation id + retained resident-runtime receipt. Failed or
boundary-only attempts remain retryable within the same UTC hour, but only through a
bounded schedule-local retry cadence so a transient dependency cannot create a tight
provider loop.
"""

from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import sovereign_scheduler as base

SCHEDULE_FILE = Path(__file__).resolve().parents[1] / "data" / "reusable_task_schedule.json"
RUNTIME_ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"
RUNTIME_REQUIRED_REL = Path("control/resident-execution-request.d/native-email-action-monitor-001.json")
KV_PATH_ENV_NAMES = ("STEGVERSE_KV_ROOT", "STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT")
SUCCESSFUL_TRIGGER_STATE = "AUTOMATABLE_STEPS_EXHAUSTED"
RETRY_STATE_SCHEMA = "stegverse.healer.reusable-task-slot-attempt-state/v1"
SOURCE_PREP_SCHEMA = "stegverse.sv-dn1.production-source-prep-receipt/v2"
SOURCE_PREP_RECEIPT_ENV = "STEGVERSE_SV_DN1_SOURCE_PREP_RECEIPT"
SOURCE_PREP_DEFAULT = Path.home() / ".stegverse" / "state" / "sv-dn1-production-source-prep" / "receipts" / "latest.json"
SOURCE_PREP_COMPONENTS = {
    "stegverse.sdk": ("StegVerse-org/StegVerse-SDK", Path("stegverse/sovereign_validation_runtime.py")),
    "stegverse.stegcore": ("StegVerse-Labs/StegCore", Path("src/stegcore/steggate_runtime.py")),
    "stegverse.core-lite": ("Data-Continuation/core-lite", Path("core_lite/transaction_route.py")),
    "stegverse.master-records": ("master-records/orchestration", Path("services/manifest_receipt_custody.py")),
}
SHA256_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


def _load_schedule(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != "stegverse.healer.reusable-task-schedule/v1":
        raise ValueError("reusable task schedule schema mismatch")
    tasks = value.get("tasks")
    if not isinstance(tasks, list) or not all(isinstance(row, dict) for row in tasks):
        raise ValueError("reusable task schedule tasks must be objects")
    return tasks


def _selected(task: dict[str, Any], scope: str) -> bool:
    if scope == "all":
        return True
    identity = str(task.get("reusable_task_id") or "").lower()
    repo = str(task.get("repository") or "").split("/")[-1].lower()
    aliases = {str(value).lower() for value in task.get("aliases", [])}
    return scope in {identity, repo} or scope in aliases


def _slot_id(task_id: str, now) -> str:
    compact = task_id.replace("RT-", "rt-").lower()
    return f"{compact}-{now.strftime('%Y%m%dT%H')}Z"


def _valid_runtime_root(root: Path) -> bool:
    return root.is_dir() and (root / RUNTIME_REQUIRED_REL).is_file()


def _resident_runtime_root() -> tuple[Path | None, str]:
    raw = str(os.getenv(RUNTIME_ROOT_ENV) or "").strip()
    if raw:
        root = Path(raw).expanduser().resolve()
        return (root, "EXPLICIT_NONSECRET_RUNTIME_ROOT") if _valid_runtime_root(root) else (None, "EXPLICIT_RUNTIME_ROOT_INVALID")

    home = Path.home()
    candidates = [
        home / ".local" / "state" / "stegverse" / "heartbeat-runtime",
        home / "Library" / "Application Support" / "stegverse" / "heartbeat-runtime",
        home / ".stegverse" / "heartbeat-runtime",
        Path("/var/lib/stegverse/heartbeat-runtime"),
        Path("/srv/stegverse/heartbeat-runtime"),
    ]
    valid = []
    for candidate in candidates:
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
    """Resolve only roots already verified by the existing SV-DN1 source-prep lane."""
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
        "migration_anchors_verified": True,
        "network_source_fetch_performed": False,
        "github_platform_required": False,
        "credential_used": False,
        "github_token_used": False,
        "repository_writeback_performed": False,
    }
    if any(value.get(key) != expected for key, expected in required.items()):
        return {}, "SV_DN1_SOURCE_PREP_RECEIPT_NOT_ADMISSIBLE"
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


def _receipt_satisfies_slot(receipt: dict[str, Any] | None) -> bool:
    return bool(isinstance(receipt, dict) and receipt.get("state") == SUCCESSFUL_TRIGGER_STATE)


def _retry_policy(task: dict[str, Any]) -> tuple[int, int]:
    interval = task.get("retry_interval_minutes", 15)
    maximum = task.get("max_attempts_per_slot", 4)
    if not isinstance(interval, int) or interval < 1 or interval > 60:
        raise ValueError("retry_interval_minutes must be integer 1..60")
    if not isinstance(maximum, int) or maximum < 1 or maximum > 12:
        raise ValueError("max_attempts_per_slot must be integer 1..12")
    return interval, maximum


def _retry_state_path(runtime_root: Path, invocation_id: str) -> Path:
    return runtime_root / "receipts" / "reusable-task" / f"{invocation_id}.attempt-state.json"


def _load_retry_state(path: Path, invocation_id: str) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema": RETRY_STATE_SCHEMA,
            "invocation_id": invocation_id,
            "attempt_count": 0,
            "last_attempt_at": None,
        }
    value = base._load_json(path)
    if value.get("schema") != RETRY_STATE_SCHEMA or value.get("invocation_id") != invocation_id:
        raise ValueError("reusable task retry state identity mismatch")
    count = value.get("attempt_count")
    if not isinstance(count, int) or count < 0:
        raise ValueError("reusable task retry attempt_count invalid")
    last = value.get("last_attempt_at")
    if last is not None and not isinstance(last, str):
        raise ValueError("reusable task retry last_attempt_at invalid")
    return value


def _write_retry_state(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _retry_gate(task: dict[str, Any], state: dict[str, Any], now) -> tuple[bool, str | None, str | None]:
    interval_minutes, max_attempts = _retry_policy(task)
    count = int(state.get("attempt_count") or 0)
    if count >= max_attempts:
        return False, "MAX_ATTEMPTS_REACHED_FOR_SLOT", None
    last = state.get("last_attempt_at")
    if not last:
        return True, None, None
    parsed = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
    retry_at = parsed + timedelta(minutes=interval_minutes)
    if now < retry_at:
        return False, "RETRY_BACKOFF_ACTIVE", retry_at.isoformat().replace("+00:00", "Z")
    return True, None, retry_at.isoformat().replace("+00:00", "Z")


def _execute_reusable_task(
    task: dict[str, Any],
    roots: dict[str, Path],
    roots_json: str,
    runtime_root: Path | None,
    runtime_root_source: str,
    now,
) -> dict[str, Any]:
    reusable_task_id = str(task.get("reusable_task_id") or "")
    tracking_task_id = str(task.get("tracking_task_id") or "")
    cosv = str(task.get("cosv_task_vector") or "")
    repository = str(task.get("repository") or "")
    retry_interval_minutes, max_attempts_per_slot = _retry_policy(task)
    base_result = {
        "reusable_task_id": reusable_task_id,
        "tracking_task_id": tracking_task_id,
        "cosv_task_vector": cosv,
        "repository": repository,
        "runtime_root_source": runtime_root_source,
        "retry_interval_minutes": retry_interval_minutes,
        "max_attempts_per_slot": max_attempts_per_slot,
    }

    root = roots.get(repository)
    if root is None:
        return {**base_result, "state": "BLOCKED", "outcome": "LOCAL_REPOSITORY_NOT_MATERIALIZED"}
    if runtime_root is None:
        return {**base_result, "state": "BLOCKED", "outcome": "RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED"}
    trigger = root / "scripts" / "trigger_reusable_task.py"
    if not trigger.is_file():
        return {**base_result, "state": "BLOCKED", "outcome": "REUSABLE_TASK_TRIGGER_NOT_MATERIALIZED"}

    invocation_id = _slot_id(reusable_task_id, now)
    receipt_path = runtime_root / "receipts" / "reusable-task" / f"{invocation_id}.latest.json"
    retry_path = _retry_state_path(runtime_root, invocation_id)
    prior = base._load_json(receipt_path) if receipt_path.is_file() else None
    if _receipt_satisfies_slot(prior):
        return {
            **base_result,
            "state": "COMPLETE",
            "outcome": "ALREADY_RAN_THIS_SCHEDULE_SLOT",
            "invocation_id": invocation_id,
            "receipt_ref": str(receipt_path),
            "receipt_state": prior.get("state"),
            "slot_satisfied": True,
            "source_root": str(root),
            "runtime_root": str(runtime_root),
        }

    retry_state = _load_retry_state(retry_path, invocation_id)
    may_attempt, deferred_reason, retry_at = _retry_gate(task, retry_state, now)
    if not may_attempt:
        return {
            **base_result,
            "state": "COMPLETE",
            "outcome": deferred_reason,
            "invocation_id": invocation_id,
            "receipt_ref": str(receipt_path),
            "receipt_state": prior.get("state") if isinstance(prior, dict) else None,
            "retry_state_ref": str(retry_path),
            "attempt_count": retry_state["attempt_count"],
            "next_retry_at": retry_at,
            "slot_satisfied": False,
            "retry_deferred": True,
            "source_root": str(root),
            "runtime_root": str(runtime_root),
        }

    parameters = dict(task.get("parameters") or {})
    parameters["source_root"] = str(root)
    parameters["runtime_root"] = str(runtime_root)
    command = [
        sys.executable,
        str(trigger),
        "--reusable-task-id",
        reusable_task_id,
        "--invocation-id",
        invocation_id,
        "--parameters-json",
        json.dumps(parameters, sort_keys=True, separators=(",", ":")),
        "--task-id",
        tracking_task_id,
        "--cosv-task-vector",
        cosv,
        "--receipt",
        str(receipt_path),
    ]
    child_env = {
        "STEGVERSE_REPO_ROOTS_JSON": roots_json,
        RUNTIME_ROOT_ENV: str(runtime_root),
        **_kv_path_env(),
    }
    result = base._run(command, root, child_env, timeout=1500)
    receipt = base._load_json(receipt_path) if receipt_path.is_file() else None
    ok = result["returncode"] == 0 and _receipt_satisfies_slot(receipt)
    attempt_count = int(retry_state.get("attempt_count") or 0) + 1
    attempt_state = {
        "schema": RETRY_STATE_SCHEMA,
        "invocation_id": invocation_id,
        "attempt_count": attempt_count,
        "last_attempt_at": now.isoformat().replace("+00:00", "Z"),
        "last_receipt_state": receipt.get("state") if isinstance(receipt, dict) else None,
        "last_returncode": result["returncode"],
        "slot_satisfied": ok,
    }
    _write_retry_state(retry_path, attempt_state)
    return {
        **base_result,
        "state": "COMPLETE" if ok else "BLOCKED",
        "outcome": "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED" if ok else "REUSABLE_TASK_SCHEDULE_SLOT_RETRYABLE",
        "invocation_id": invocation_id,
        "receipt_ref": str(receipt_path),
        "receipt_state": receipt.get("state") if isinstance(receipt, dict) else None,
        "prior_receipt_state": prior.get("state") if isinstance(prior, dict) else None,
        "retry_state_ref": str(retry_path),
        "attempt_count": attempt_count,
        "slot_satisfied": ok,
        "same_slot_retry_permitted": not ok and attempt_count < max_attempts_per_slot,
        "next_retry_at": None if ok or attempt_count >= max_attempts_per_slot else (now + timedelta(minutes=retry_interval_minutes)).isoformat().replace("+00:00", "Z"),
        "source_root": str(root),
        "runtime_root": str(runtime_root),
        "kv_path_env_forwarded": sorted(name for name in KV_PATH_ENV_NAMES if name in child_env),
        "execution": result,
    }


def build_and_execute(config_path: Path, schedule_path: Path = SCHEDULE_FILE) -> dict[str, Any]:
    receipt = base.build_and_execute(config_path)
    roots = base._repo_roots()
    prepared_roots, source_prep_state = _verified_governance_component_roots()
    for repository, path in prepared_roots.items():
        roots.setdefault(repository, path)
    roots_json = json.dumps({repo: str(path) for repo, path in sorted(roots.items())}, sort_keys=True)
    scope = (os.getenv("RUN_SCOPE") or "all").strip().lower()
    mode = (os.getenv("DISPATCH_MODE") or "schedule").strip().lower()
    now = base._now()
    runtime_root, runtime_root_source = _resident_runtime_root()

    scheduled: list[dict[str, Any]] = []
    if schedule_path.is_file():
        for task in _load_schedule(schedule_path):
            if not task.get("enabled", True) or not _selected(task, scope):
                continue
            if not base._due(task, now, mode):
                continue
            scheduled.append(_execute_reusable_task(task, roots, roots_json, runtime_root, runtime_root_source, now))

    receipt["reusable_task_schedule_schema"] = "stegverse.healer.reusable-task-schedule/v1"
    receipt["selected_reusable_tasks"] = len(scheduled)
    receipt["reusable_task_schedule"] = scheduled
    receipt["resident_runtime_root"] = str(runtime_root) if runtime_root is not None else None
    receipt["resident_runtime_root_source"] = runtime_root_source
    receipt["kv_path_env_available"] = sorted(_kv_path_env())
    receipt["sv_dn1_source_prep_state"] = source_prep_state
    receipt["sv_dn1_governance_component_roots_added"] = sorted(prepared_roots)
    if receipt.get("state") == "COMPLETE" and any(row.get("state") == "BLOCKED" for row in scheduled):
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
            "error": str(exc),
        }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
