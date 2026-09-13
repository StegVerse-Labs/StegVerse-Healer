from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import reusable_task_scheduler as subject  # noqa: E402


def test_healer_no_longer_owns_reusable_child_retry_engine():
    source = (ROOT / "app" / "reusable_task_scheduler.py").read_text(encoding="utf-8")
    assert "def _execute_reusable_task" not in source
    assert "def _retry_gate" not in source
    assert "def _retry_state_path" not in source
    assert subject.NEUTRAL_SCHEDULER_ID == "RT-REUSABLE-TASK-SCHEDULER-001"
    assert "CONSUMER_CARRIER_ONLY" in source


def test_healer_schedule_preserves_retry_policy_for_neutral_scheduler():
    schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
    assert schedule["schema"] == "stegverse.reusable-task-schedule/v1"
    assert schedule["tasks"]
    for row in schedule["tasks"]:
        assert row["retry_interval_minutes"] == 15
        assert row["max_attempts_per_slot"] == 4
        assert row["repository"] == "StegVerse-Labs/.github"


def test_healer_neutral_scheduler_invocation_identity_is_carrier_scoped():
    from datetime import datetime, timezone
    value = subject._neutral_scheduler_invocation_id(datetime(2026, 9, 13, 20, 25, 30, tzinfo=timezone.utc))
    assert value == "healer-neutral-reusable-scheduler-20260913T202530Z"
