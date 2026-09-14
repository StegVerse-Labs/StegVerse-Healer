from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stegos_ai_preexecution_runtime_proof_uses_existing_neutral_scheduler_carrier():
    schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
    assert schedule["schema"] == "stegverse.reusable-task-schedule/v1"
    rows = [row for row in schedule["tasks"] if row.get("reusable_task_id") == "RT-STEGOS-AI-PREEXECUTION-RUNTIME-PROOF-001"]
    assert len(rows) == 1
    row = rows[0]
    assert row["tracking_task_id"] == "STEGOS-AI-PREEXECUTION-RUNTIME-PROOF-001"
    assert row["cosv_task_vector"] == "40000100100000"
    assert row["repository"] == "StegVerse-Labs/.github"
    assert row["enabled"] is True
    assert row["run_hours_utc"] == list(range(24))
    assert row["retry_interval_minutes"] == 15
    assert row["max_attempts_per_slot"] == 4
    assert row["parameters"]["selected_execution_substrate"] == "ADMITTED-EPHEMERAL-STEGOS-NODE"
    assert row["parameters"]["automatic_advancement_required"] is True
    assert row["parameters"]["network_source_fetch_allowed"] is False
    assert row["parameters"]["remote_desktop_required"] is False
    assert row["parameters"]["second_user_operated_device_required"] is False
    assert "no-second-scheduler" in row["status"]


def test_stegos_ai_binding_reuses_existing_neutral_scheduler_trigger_surface():
    carrier = (ROOT / "app" / "reusable_task_scheduler.py").read_text(encoding="utf-8")
    assert 'NEUTRAL_SCHEDULER_ID = "RT-REUSABLE-TASK-SCHEDULER-001"' in carrier
    assert 'NEUTRAL_TRIGGER_REL = Path("scripts/trigger_reusable_task.py")' in carrier
    assert 'RUNTIME_ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"' in carrier
    assert "CONSUMER_CARRIER_ONLY" in carrier
