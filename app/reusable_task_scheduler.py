from __future__ import annotations

"""Extend the existing sovereign Healer scheduler with reusable-task schedules.

This module is not a second scheduler. It is the single Healer scheduler entrypoint
with an additional data-driven reusable-task schedule pass. Each successful schedule
slot is idempotent by invocation id + retained resident-runtime receipt. Failed or
boundary-only attempts remain retryable within the same UTC hour.
"""

import json
import os
from pathlib import Path
import sys
from typing import Any

import sovereign_scheduler as base

SCHEDULE_FILE = Path(__file__).resolve().parents[1] / "data" / "reusable_task_schedule.json"
RUNTIME_ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"
RUNTIME_REQUIRED_REL = Path("control/resident-execution-request.d/native-email-action-monitor-001.json")
KV_PATH_ENV_NAMES = ("STEGVERSE_KV_ROOT", "STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT")
SUCCESSFUL_TRIGGER_STATE = "AUTOMATABLE_STEPS_EXHAUSTED"


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


def _receipt_satisfies_slot(receipt: dict[str, Any] | None) -> bool:
    return bool(isinstance(receipt, dict) and receipt.get("state") == SUCCESSFUL_TRIGGER_STATE)


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
    base_result = {
        "reusable_task_id": reusable_task_id,
        "tracking_task_id": tracking_task_id,
        "cosv_task_vector": cosv,
        "repository": repository,
        "runtime_root_source": runtime_root_source,
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
    prior = base._load_json(receipt_path) if receipt_path.is_file() else None
    if _receipt_satisfies_slot(prior):
        return {
            **base_result,
            "state": "COMPLETE",
            "outcome": "ALREADY_RAN_THIS_SCHEDULE_SLOT",
            "invocation_id": invocation_id,
            "receipt_ref": str(receipt_path),
            "receipt_state": prior.get("state"),
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
    return {
        **base_result,
        "state": "COMPLETE" if ok else "BLOCKED",
        "outcome": "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED" if ok else "REUSABLE_TASK_SCHEDULE_SLOT_RETRYABLE",
        "invocation_id": invocation_id,
        "receipt_ref": str(receipt_path),
        "receipt_state": receipt.get("state") if isinstance(receipt, dict) else None,
        "prior_receipt_state": prior.get("state") if isinstance(prior, dict) else None,
        "same_slot_retry_permitted": not ok,
        "source_root": str(root),
        "runtime_root": str(runtime_root),
        "kv_path_env_forwarded": sorted(name for name in KV_PATH_ENV_NAMES if name in child_env),
        "execution": result,
    }


def build_and_execute(config_path: Path, schedule_path: Path = SCHEDULE_FILE) -> dict[str, Any]:
    receipt = base.build_and_execute(config_path)
    roots = base._repo_roots()
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
