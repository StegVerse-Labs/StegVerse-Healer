from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import reusable_task_scheduler as subject  # noqa: E402


def _runtime_root(base: Path) -> Path:
    root = base / "heartbeat-runtime"
    request = root / subject.RUNTIME_REQUIRED_REL
    request.parent.mkdir(parents=True, exist_ok=True)
    request.write_text("{}\n", encoding="utf-8")
    return root


def _schedule(path: Path) -> None:
    path.write_text(json.dumps({
        "schema": "stegverse.healer.reusable-task-schedule/v1",
        "tasks": [{
            "reusable_task_id": "RT-NATIVE-EMAIL-ACTION-MONITOR-001",
            "tracking_task_id": "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001",
            "cosv_task_vector": "10100000100000",
            "repository": "StegVerse-Labs/.github",
            "enabled": True,
            "run_hours_utc": list(range(24)),
            "parameters": {},
        }],
    }), encoding="utf-8")


def test_boundary_receipt_does_not_poison_hourly_slot_and_is_retried():
    now = dt.datetime(2026, 9, 10, 21, 15, tzinfo=dt.timezone.utc)
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        github_root = base / ".github"
        trigger = github_root / "scripts" / "trigger_reusable_task.py"
        trigger.parent.mkdir(parents=True)
        trigger.write_text("print('placeholder')\n", encoding="utf-8")
        runtime = _runtime_root(base)
        schedule = base / "schedule.json"
        _schedule(schedule)
        invocation = "rt-native-email-action-monitor-001-20260910T21Z"
        receipt = runtime / "receipts" / "reusable-task" / f"{invocation}.latest.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({
            "schema": "stegverse.reusable-task-trigger-receipt/v1",
            "state": "BOUNDARY_RECORDED",
            "boundary": {"kind": "DECLARED_RUNNER_STOPPED_BEFORE_COMPLETION"},
        }) + "\n", encoding="utf-8")

        calls = []
        def fake_run(command, cwd, env, timeout):
            calls.append(command)
            receipt.write_text(json.dumps({
                "schema": "stegverse.reusable-task-trigger-receipt/v1",
                "state": "AUTOMATABLE_STEPS_EXHAUSTED",
                "invocation_id": invocation,
            }) + "\n", encoding="utf-8")
            return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

        with mock.patch.object(subject.base, "build_and_execute", return_value={"schema":"stegverse.healer.sovereign_scheduler_receipt/v0.1","state":"COMPLETE"}), \
             mock.patch.object(subject.base, "_repo_roots", return_value={"StegVerse-Labs/.github": github_root}), \
             mock.patch.object(subject.base, "_now", return_value=now), \
             mock.patch.object(subject.base, "_run", side_effect=fake_run), \
             mock.patch.dict("os.environ", {"RUN_SCOPE":"all","DISPATCH_MODE":"schedule","STEGVERSE_HEARTBEAT_ROOT":str(runtime)}, clear=False):
            result = subject.build_and_execute(base / "targets.json", schedule)

        assert len(calls) == 1
        row = result["reusable_task_schedule"][0]
        assert row["prior_receipt_state"] == "BOUNDARY_RECORDED"
        assert row["receipt_state"] == "AUTOMATABLE_STEPS_EXHAUSTED"
        assert row["outcome"] == "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED"
        assert row["same_slot_retry_permitted"] is False


def test_successful_receipt_is_the_only_slot_idempotency_terminal():
    assert subject._receipt_satisfies_slot({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) is True
    assert subject._receipt_satisfies_slot({"state": "BOUNDARY_RECORDED"}) is False
    assert subject._receipt_satisfies_slot({"state": "FAILED"}) is False
    assert subject._receipt_satisfies_slot(None) is False
