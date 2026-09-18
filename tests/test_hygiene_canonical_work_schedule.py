from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RT_ID = "RT-CANONICAL-WORK-PORTABLE-DISPATCH-001"
GOAL = "HYGIENE-CAUSAL-ROOTS-001"
COSV = "10100000100000"


def test_hygiene_canonical_work_uses_existing_neutral_scheduler_carrier() -> None:
    schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
    assert schedule["schema"] == "stegverse.reusable-task-schedule/v1"
    rows = [row for row in schedule["tasks"] if row.get("reusable_task_id") == RT_ID]
    assert len(rows) == 1
    row = rows[0]
    assert row["tracking_task_id"] == GOAL
    assert row["cosv_task_vector"] == COSV
    assert row["repository"] == "StegVerse-Labs/.github"
    assert row["enabled"] is True
    assert row["run_hours_utc"] == list(range(24))
    assert row["retry_interval_minutes"] == 15
    assert row["max_attempts_per_slot"] == 4
    assert row["parameters"] == {
        "only_consumer": "canonical_work_coordination",
        "goal_task_id": GOAL,
    }
    assert "no-second-scheduler" in row["status"]


def test_hygiene_binding_reuses_existing_neutral_trigger_and_runtime_bootstrap() -> None:
    carrier = (ROOT / "app" / "reusable_task_scheduler.py").read_text(encoding="utf-8")
    assert 'NEUTRAL_SCHEDULER_ID = "RT-REUSABLE-TASK-SCHEDULER-001"' in carrier
    assert 'NEUTRAL_TRIGGER_REL = Path("scripts/trigger_reusable_task.py")' in carrier
    assert 'SOURCE_REFRESH_TASK_ID = "RT-SOVEREIGN-SOURCE-REFRESH-001"' in carrier
    assert 'RUNTIME_ROOT_ENV = "STEGVERSE_HEARTBEAT_ROOT"' in carrier
    assert "CONSUMER_CARRIER_ONLY" in carrier
    assert "second_scheduler_created" in carrier
    assert "second_user_operated_device_required" in carrier
