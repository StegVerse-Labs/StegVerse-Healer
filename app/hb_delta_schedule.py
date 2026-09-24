"""Resident HB(Δ) eligibility for the existing ST-018 fixed Healer target.

This module only selects work and retains non-authorizing scheduling evidence.
The enclosing resident WorkerCoordinator, never HB or this module, owns claim/fence.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

TASK = "HEALER-RSTD-ST018-LOCAL-TASK-MANAGER-001"
SCHEMA = "stegverse.healer.st018-hb-delta-checkpoint/v1"
HB_SCHEMA = "stegverse.heartbeat-carrier-runtime-state/v1"
HB_FREQUENCY = "INDEPENDENT_OSCILLATOR_10MS_PHASE_TRAVEL"
HB_SOURCE = Path("control/heartbeat-carrier-runtime-state.json")
CHECKPOINT = Path("receipts/healer-sovereign-scheduler/st018-hb-delta-checkpoint.json")
PERIOD_REFS = 2_160_000  # six hours of canonical 100 Hz reference progression
RETRY_REFS = 90_000      # 15 minutes of canonical reference progression
MAX_ATTEMPTS = 4


def _digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _read(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("JSON object required")
    return result


def _resident_root() -> Path:
    raw = os.environ.get("STEGVERSE_HEARTBEAT_ROOT", "").strip()
    if not raw or not Path(raw).is_absolute():
        raise ValueError("RESIDENT_HEARTBEAT_ROOT_REQUIRED")
    root = Path(raw).resolve()
    if not root.is_dir():
        raise ValueError("RESIDENT_HEARTBEAT_ROOT_NOT_MATERIALIZED")
    return root


def _hb(root: Path) -> tuple[int, str]:
    path = root / HB_SOURCE
    if not path.is_file():
        raise ValueError("AUTHENTIC_HB_CARRIER_STATE_MISSING")
    data = _read(path)
    epoch, generation = data.get("epoch"), data.get("generation")
    osc = data.get("oscillator")
    cutover = data.get("legacy_cutover")
    if (
        data.get("schema") != HB_SCHEMA
        or data.get("role") != "REGULATORY_CARRIER_REFERENCE_FRAME"
        or data.get("frequency_rule") != HB_FREQUENCY
        or data.get("authority_effect") != "NONE"
        or data.get("activation_state") != "ACTIVE"
        or not _integer(epoch) or epoch < 30
        or not _integer(generation) or generation != epoch
        or data.get("reference_frame") != f"heartbeat_epoch:{epoch}"
        or not isinstance(cutover, dict) or cutover.get("closed") is not True
        or cutover.get("legacy_epoch") != 29
        or not isinstance(osc, dict) or osc.get("period_ns") != 10_000_000
        or osc.get("mechanism") != "INDEPENDENT_PHASE_OSCILLATOR"
        or osc.get("progression_dependency") != "OSCILLATOR_ONLY"
        or osc.get("sampled_reference_epoch") != epoch
        or osc.get("snapshot_is_observation_only") is not True
    ):
        raise ValueError("AUTHENTIC_HB_CARRIER_STATE_INVALID")
    return epoch, hashlib.sha256(path.read_bytes()).hexdigest()


def _checkpoint(root: Path) -> dict[str, Any] | None:
    path = root / CHECKPOINT
    if not path.exists():
        return None
    data = _read(path)
    digest = data.pop("checkpoint_sha256", None)
    if (
        data.get("schema") != SCHEMA or data.get("task_id") != TASK
        or data.get("period_hb_refs") != PERIOD_REFS
        or data.get("retry_hb_refs") != RETRY_REFS
        or data.get("max_attempts") != MAX_ATTEMPTS
        or not _integer(data.get("last_attempt_epoch"))
        or not _integer(data.get("first_attempt_epoch"))
        or not _integer(data.get("attempts"))
        or data["attempts"] > MAX_ATTEMPTS
        or not (data.get("last_complete_epoch") is None or _integer(data["last_complete_epoch"]))
        or data.get("authority_effect") != "NONE_SCHEDULING_ONLY"
        or digest != _digest(data)
    ):
        raise ValueError("HB_DELTA_CHECKPOINT_INVALID")
    return data


def plan() -> dict[str, Any]:
    """Fail closed on missing/invalid resident observations and checkpoints."""
    try:
        root = _resident_root()
        epoch, hb_hash = _hb(root)
        prior = _checkpoint(root)
        base = {"hb_epoch": epoch, "hb_source_sha256": hb_hash,
                "hb_source_ref": str(HB_SOURCE), "checkpoint_ref": str(CHECKPOINT),
                "authority_effect": "NONE_SCHEDULING_ONLY"}
        if prior is None:
            return {**base, "state": "DUE", "reason": "FIRST_AUTHENTIC_HB_OBSERVATION"}
        if epoch < prior["last_attempt_epoch"] or epoch < prior["first_attempt_epoch"]:
            raise ValueError("HB_EPOCH_REGRESSION")
        complete = prior["last_complete_epoch"]
        if complete is not None:
            if epoch < complete:
                raise ValueError("HB_COMPLETION_EPOCH_REGRESSION")
            if epoch - complete < PERIOD_REFS:
                return {**base, "state": "NOT_DUE", "reason": "HB_DELTA_BELOW_PERIOD",
                        "remaining_hb_refs": PERIOD_REFS - (epoch - complete)}
            # New period: the previous successful cycle is no longer a retry window.
            return {**base, "state": "DUE", "reason": "HB_DELTA_PERIOD_ELAPSED"}
        # A failed first attempt or a retryable failed prior cycle.
        if prior["attempts"] >= MAX_ATTEMPTS:
            if epoch - prior["first_attempt_epoch"] < PERIOD_REFS:
                return {**base, "state": "NOT_DUE", "reason": "RETRY_WINDOW_EXHAUSTED"}
            return {**base, "state": "DUE", "reason": "RETRY_WINDOW_RECOVERED"}
        if epoch - prior["last_attempt_epoch"] < RETRY_REFS:
            return {**base, "state": "NOT_DUE", "reason": "RETRY_HB_DELTA_BELOW_MINIMUM"}
        return {**base, "state": "DUE", "reason": "RETRY_HB_DELTA_ELAPSED"}
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"state": "BLOCKED", "reason": str(exc),
                "authority_effect": "NONE_SCHEDULING_ONLY"}


def record(plan_result: dict[str, Any], outcome: dict[str, Any]) -> dict[str, Any]:
    """Retain only a real selected target outcome after its parent worker invocation."""
    if plan_result.get("state") != "DUE":
        raise ValueError("HB_DELTA_NOT_DUE")
    root = _resident_root()
    epoch, current_hash = _hb(root)
    if epoch < plan_result["hb_epoch"] or current_hash != plan_result["hb_source_sha256"]:
        # A changed carrier observation requires a fresh eligibility decision.
        raise ValueError("HB_OBSERVATION_CHANGED_DURING_EXECUTION")
    prior = _checkpoint(root)
    if prior and epoch < prior["last_attempt_epoch"]:
        raise ValueError("HB_EPOCH_REGRESSION")
    complete = outcome.get("state") == "COMPLETE" and outcome.get("receipt", {}).get("status") == "PASS"
    if complete:
        last_complete, first, attempts = epoch, epoch, 0
    else:
        last_complete = None
        if prior and prior["last_complete_epoch"] is None and epoch - prior["first_attempt_epoch"] < PERIOD_REFS:
            first, attempts = prior["first_attempt_epoch"], min(MAX_ATTEMPTS, prior["attempts"] + 1)
        else:
            first, attempts = epoch, 1
    payload = {
        "schema": SCHEMA, "task_id": TASK, "period_hb_refs": PERIOD_REFS,
        "retry_hb_refs": RETRY_REFS, "max_attempts": MAX_ATTEMPTS,
        "last_complete_epoch": last_complete, "first_attempt_epoch": first,
        "last_attempt_epoch": epoch, "attempts": attempts,
        "hb_source_ref": str(HB_SOURCE), "hb_source_sha256": current_hash,
        "outcome_sha256": _digest(outcome), "outcome_state": outcome.get("state"),
        "authority_effect": "NONE_SCHEDULING_ONLY",
        "master_records_closure_claimed": False,
        "workercoordinator_claim_fence_claimed": False,
    }
    payload["checkpoint_sha256"] = _digest(payload)
    path = root / CHECKPOINT
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as f:
        json.dump(payload, f, sort_keys=True)
        f.write("\n")
        name = f.name
    os.replace(name, path)
    return {"state": "RECORDED", "checkpoint_ref": str(CHECKPOINT),
            "checkpoint_sha256": payload["checkpoint_sha256"],
            "completion": complete, "authority_effect": "NONE_SCHEDULING_ONLY"}
