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
            "retry_interval_minutes": 15,
            "max_attempts_per_slot": 4,
            "parameters": {},
        }],
    }), encoding="utf-8")


def _github_root(base: Path) -> Path:
    root = base / ".github"
    trigger = root / "scripts" / "trigger_reusable_task.py"
    trigger.parent.mkdir(parents=True)
    trigger.write_text("print('placeholder')\n", encoding="utf-8")
    return root


def _task():
    return {
        "reusable_task_id": "RT-NATIVE-EMAIL-ACTION-MONITOR-001",
        "tracking_task_id": "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001",
        "cosv_task_vector": "10100000100000",
        "repository": "StegVerse-Labs/.github",
        "retry_interval_minutes": 15,
        "max_attempts_per_slot": 4,
        "parameters": {},
    }


def test_boundary_receipt_retries_when_backoff_is_due():
    now = dt.datetime(2026, 9, 10, 21, 15, tzinfo=dt.timezone.utc)
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        github_root = _github_root(base)
        runtime = _runtime_root(base)
        invocation = "rt-native-email-action-monitor-001-20260910T21Z"
        receipt = runtime / "receipts" / "reusable-task" / f"{invocation}.latest.json"
        retry = subject._retry_state_path(runtime, invocation)
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({"state": "BOUNDARY_RECORDED"}) + "\n", encoding="utf-8")
        subject._write_retry_state(retry, {
            "schema": subject.RETRY_STATE_SCHEMA,
            "invocation_id": invocation,
            "attempt_count": 1,
            "last_attempt_at": "2026-09-10T21:00:00Z",
            "last_receipt_state": "BOUNDARY_RECORDED",
            "last_returncode": 3,
            "slot_satisfied": False,
        })

        calls = []
        def fake_run(command, cwd, env, timeout):
            calls.append(command)
            receipt.write_text(json.dumps({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) + "\n", encoding="utf-8")
            return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

        with mock.patch.object(subject.base, "_run", side_effect=fake_run):
            row = subject._execute_reusable_task(
                _task(), {"StegVerse-Labs/.github": github_root},
                json.dumps({"StegVerse-Labs/.github": str(github_root)}),
                runtime, "EXPLICIT_NONSECRET_RUNTIME_ROOT", now,
            )

        assert len(calls) == 1
        assert row["outcome"] == "REUSABLE_TASK_SCHEDULE_SLOT_EXECUTED"
        assert row["attempt_count"] == 2
        assert row["slot_satisfied"] is True
        assert row["same_slot_retry_permitted"] is False


def test_failed_slot_is_deferred_until_15_minute_backoff_expires():
    now = dt.datetime(2026, 9, 10, 21, 10, tzinfo=dt.timezone.utc)
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        github_root = _github_root(base)
        runtime = _runtime_root(base)
        invocation = "rt-native-email-action-monitor-001-20260910T21Z"
        retry = subject._retry_state_path(runtime, invocation)
        subject._write_retry_state(retry, {
            "schema": subject.RETRY_STATE_SCHEMA,
            "invocation_id": invocation,
            "attempt_count": 1,
            "last_attempt_at": "2026-09-10T21:00:00Z",
            "last_receipt_state": "BOUNDARY_RECORDED",
            "last_returncode": 3,
            "slot_satisfied": False,
        })
        with mock.patch.object(subject.base, "_run") as run:
            row = subject._execute_reusable_task(
                _task(), {"StegVerse-Labs/.github": github_root}, "{}",
                runtime, "EXPLICIT_NONSECRET_RUNTIME_ROOT", now,
            )
        run.assert_not_called()
        assert row["outcome"] == "RETRY_BACKOFF_ACTIVE"
        assert row["attempt_count"] == 1
        assert row["next_retry_at"] == "2026-09-10T21:15:00Z"
        assert row["retry_deferred"] is True
        assert row["slot_satisfied"] is False


def test_four_failed_attempts_stop_provider_retries_until_next_hour_slot():
    now = dt.datetime(2026, 9, 10, 21, 50, tzinfo=dt.timezone.utc)
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        github_root = _github_root(base)
        runtime = _runtime_root(base)
        invocation = "rt-native-email-action-monitor-001-20260910T21Z"
        retry = subject._retry_state_path(runtime, invocation)
        subject._write_retry_state(retry, {
            "schema": subject.RETRY_STATE_SCHEMA,
            "invocation_id": invocation,
            "attempt_count": 4,
            "last_attempt_at": "2026-09-10T21:45:00Z",
            "last_receipt_state": "BOUNDARY_RECORDED",
            "last_returncode": 3,
            "slot_satisfied": False,
        })
        with mock.patch.object(subject.base, "_run") as run:
            row = subject._execute_reusable_task(
                _task(), {"StegVerse-Labs/.github": github_root}, "{}",
                runtime, "EXPLICIT_NONSECRET_RUNTIME_ROOT", now,
            )
        run.assert_not_called()
        assert row["outcome"] == "MAX_ATTEMPTS_REACHED_FOR_SLOT"
        assert row["attempt_count"] == 4
        assert row["slot_satisfied"] is False

        next_id = subject._slot_id(_task()["reusable_task_id"], dt.datetime(2026, 9, 10, 22, 0, tzinfo=dt.timezone.utc))
        assert next_id == "rt-native-email-action-monitor-001-20260910T22Z"
        assert subject._retry_state_path(runtime, next_id) != retry


def test_successful_receipt_is_the_only_slot_idempotency_terminal():
    assert subject._receipt_satisfies_slot({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) is True
    assert subject._receipt_satisfies_slot({"state": "BOUNDARY_RECORDED"}) is False
    assert subject._receipt_satisfies_slot({"state": "FAILED"}) is False
    assert subject._receipt_satisfies_slot(None) is False
