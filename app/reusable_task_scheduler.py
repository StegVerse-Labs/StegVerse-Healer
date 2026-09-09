from __future__ import annotations

"""Extend the existing sovereign Healer scheduler with reusable-task schedules.

This module is not a second scheduler. It is the single Healer scheduler entrypoint
with an additional data-driven reusable-task schedule pass. Each schedule slot is
idempotent by invocation id + retained local receipt, so an hourly entry runs at
most once per UTC hour even if the resident scheduler is visited repeatedly.
"""

import json
import os
from pathlib import Path
import sys
from typing import Any

import sovereign_scheduler as base

SCHEDULE_FILE = Path(__file__).resolve().parents[1] / "data" / "reusable_task_schedule.json"


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


def _execute_reusable_task(task: dict[str, Any], roots: dict[str, Path], roots_json: str, now) -> dict[str, Any]:
    reusable_task_id = str(task.get("reusable_task_id") or "")
    tracking_task_id = str(task.get("tracking_task_id") or "")
    cosv = str(task.get("cosv_task_vector") or "")
    repository = str(task.get("repository") or "")
    base_result = {
        "reusable_task_id": reusable_task_id,
        "tracking_task_id": tracking_task_id,
        "cosv_task_vector": cosv,
        "repository": repository,
    }

    root = roots.get(repository)
    if root is None:
        return {**base_result, "state": "BLOCKED", "outcome": "LOCAL_REPOSITORY_NOT_MATERIALIZED"}
    trigger = root / "scripts" / "trigger_reusable_task.py"
    if not trigger.is_file():
        return {**base_result, "state": "BLOCKED", "outcome": "REUSABLE_TASK_TRIGGER_NOT_MATERIALIZED"}

    invocation_id = _slot_id(reusable_task_id, now)
    receipt_path = root / "receipts" / "reusable-task" / f"{invocation_id}.latest.json"
    if receipt_path.is_file():
        prior = base._load_json(receipt_path)
        return {
            **base_result,
            "state": "COMPLETE",
            "outcome": "ALREADY_RAN_THIS_SCHEDULE_SLOT",
            "invocation_id": invocation_id,
            "receipt_ref": str(receipt_path),
            "receipt_state": prior.get("state"),
        }

    parameters = dict(task.get("parameters") or {})
    parameters["source_root"] = str(root)
    parameters["runtime_root"] = str(root)
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
    result = base._run(
        command,
        root,
        {"STEGVERSE_REPO_ROOTS_JSON": roots_json},
        timeout=1500,
    )
    receipt = base._load_json(receipt_path) if receipt_path.is_file() else None
    ok = result["returncode"] == 0 and isinstance(receipt, dict)
    return {
        **base_result,
        "state": "COMPLETE" if ok else "BLOCKED",
        "outcome": "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED" if ok else "REUSABLE_TASK_SCHEDULE_SLOT_BLOCKED",
        "invocation_id": invocation_id,
        "receipt_ref": str(receipt_path),
        "receipt_state": receipt.get("state") if isinstance(receipt, dict) else None,
        "execution": result,
    }


def build_and_execute(config_path: Path, schedule_path: Path = SCHEDULE_FILE) -> dict[str, Any]:
    receipt = base.build_and_execute(config_path)
    roots = base._repo_roots()
    roots_json = json.dumps({repo: str(path) for repo, path in sorted(roots.items())}, sort_keys=True)
    scope = (os.getenv("RUN_SCOPE") or "all").strip().lower()
    mode = (os.getenv("DISPATCH_MODE") or "schedule").strip().lower()
    now = base._now()

    scheduled: list[dict[str, Any]] = []
    if schedule_path.is_file():
        for task in _load_schedule(schedule_path):
            if not task.get("enabled", True) or not _selected(task, scope):
                continue
            if not base._due(task, now, mode):
                continue
            scheduled.append(_execute_reusable_task(task, roots, roots_json, now))

    receipt["reusable_task_schedule_schema"] = "stegverse.healer.reusable-task-schedule/v1"
    receipt["selected_reusable_tasks"] = len(scheduled)
    receipt["reusable_task_schedule"] = scheduled
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
