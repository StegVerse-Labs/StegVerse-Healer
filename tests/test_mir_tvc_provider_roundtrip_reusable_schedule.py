from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "MIR-TVC-PROVIDER-ROUNDTRIP-001"
COSV = "50000000100000"
RT_ID = "RT-TVC-RUNTIME-BOUNDARY-OBSERVATION-001"


def test_mir_tvc_roundtrip_uses_existing_neutral_reusable_scheduler() -> None:
    schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
    assert schedule["schema"] == "stegverse.reusable-task-schedule/v1"
    rows = [row for row in schedule["tasks"] if row.get("tracking_task_id") == TASK_ID]
    assert len(rows) == 1
    row = rows[0]
    assert row["reusable_task_id"] == RT_ID
    assert row["cosv_task_vector"] == COSV
    assert row["repository"] == "StegVerse-Labs/.github"
    assert row["enabled"] is True
    assert row["invocation_key"] == TASK_ID
    assert row["run_hours_utc"] == list(range(24))
    assert row["retry_interval_minutes"] == 15
    assert row["max_attempts_per_slot"] == 4
    params = row["parameters"]
    assert params["provider_operation_receipt_ref"] == "receipts/mir-tvc-provider-roundtrip/MIR-RUN2-EVENT-001.latest.json"
    assert params["expected_ready_state"] == "READY_PRIMARY_RUNTIME_PROVIDER_OPERATION_BOUND"
    assert params["automatic_advancement_required"] is True
    assert params["require_vault_backed_provider_binding"] is True
    assert params["network_source_fetch_allowed"] is False
    assert params["remote_desktop_required"] is False
    assert params["persistent_runner_required"] is False
    assert params["second_scheduler_required"] is False
    assert params["second_user_operated_device_required"] is False
