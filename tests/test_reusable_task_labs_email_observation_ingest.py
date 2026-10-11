"""Labs outstanding email-failure observations -> existing failure ledger (Labs #3039 P3).

The hourly reusable-task carrier reads
``data/native-email-action-monitor/healer-observations.latest.json`` from the
materialized StegVerse-Labs/.github root and feeds each record to
``failure_mailbox.incident_engine.ingest_observation``. Missing or malformed
input fails closed; ingestion is idempotent on message_id; nothing is ever
transitioned to RESOLVED here.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import reusable_task_scheduler as subject  # noqa: E402

LABS_REPO = "StegVerse-Labs/.github"


def observation(message_id: str, *, repo: str = "StegVerse-Labs/Site", workflow: str = "Site Node Continuity",
                received_at: str = "2026-10-05T00:00:00Z", **extra) -> dict:
    row = {
        "message_id": message_id,
        "repository": repo,
        "workflow": workflow,
        "received_at": received_at,
        "commit_sha": "b" * 40,
        "run_id": "123",
        "subject": f"[{repo}] Run failed: {workflow} (bbbbbbb)",
        "failure_message": f"Run failed: {workflow} (bbbbbbb)",
        "annotation": "STILL_FAILING: latest completed main run concluded failure",
        "source": "stegverse-labs-native-email-continuation",
        "authority_effect": False,
        "heartbeat_effect": False,
        "lineage_id": "LIN-" + message_id,
        "classification": "STILL_FAILING",
        "incident_ids": ["INC-EMAIL-1"],
        "related_message_ids": [message_id],
    }
    row.update(extra)
    return row


def projection(rows: list[dict], **overrides) -> dict:
    payload = {
        "schema": subject.LABS_HEALER_OBSERVATIONS_SCHEMA,
        "observation_schema": subject.HEALER_OBSERVATION_RECORD_SCHEMA,
        "task_id": "STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001",
        "projection_source": {"cycle_seq": 3, "transition_seq": 240, "state_sha256": "0" * 64},
        "source_correlation": {"schema": "stegverse.email-incident-github-correlation/v1", "correlation_sha256": "1" * 64},
        "observation_count": len(rows),
        "observations": rows,
        "resolved_transition_claimed": False,
        "projection_only": True,
        "authority_effect": "NONE_PROJECTION_ONLY",
    }
    payload.update(overrides)
    return payload


class LabsEmailObservationIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.github_root = self.root / "dotgithub"
        self.github_root.mkdir()
        self.state_dir = self.root / "state"
        self.schedule = self.root / "schedule.json"
        self._write_schedule(enabled=True)
        self._env = mock.patch.dict("os.environ", {"HEALER_FAILURE_MAILBOX_STATE_DIR": str(self.state_dir)}, clear=False)
        self._env.start()

    def tearDown(self) -> None:
        self._env.stop()
        self._tmp.cleanup()

    def _write_schedule(self, *, enabled: bool) -> None:
        self.schedule.write_text(json.dumps({
            "schema": "stegverse.reusable-task-schedule/v1",
            "tasks": [{"reusable_task_id": subject.NATIVE_EMAIL_TASK_ID, "repository": LABS_REPO, "enabled": enabled,
                       "run_hours_utc": list(range(24)), "retry_interval_minutes": 15, "max_attempts_per_slot": 4}],
        }), encoding="utf-8")

    def _write_projection(self, payload) -> Path:
        path = self.github_root / subject.LABS_HEALER_OBSERVATIONS_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload, encoding="utf-8")
        return path

    def _ingest(self):
        return subject._ingest_labs_outstanding_email_observations({LABS_REPO: self.github_root}, self.schedule)

    def _ledger(self) -> dict:
        return json.loads((self.state_dir / "github-operational-failure-ledger.json").read_text(encoding="utf-8"))

    def test_ingests_into_existing_ledger_idempotently_without_resolving(self) -> None:
        self._write_projection(projection([observation("m1"), observation("m2", workflow="Site Handoff Orchestrator")]))
        first = self._ingest()
        self.assertEqual(first["state"], "INGESTED", first)
        self.assertEqual(first["observation_count"], 2)
        self.assertEqual(first["ingested_count"], 2)
        self.assertEqual(first["result_counts"], {"incident_created": 2, "incident_updated": 0, "duplicate_noop": 0})
        self.assertEqual(first["authority_effect"], "NONE_OBSERVATION_INGEST_ONLY")
        self.assertFalse(first["resolved_transition_claimed"])
        self.assertFalse(first["new_scheduler_created"])
        self.assertFalse(first["new_process_created"])
        self.assertEqual(first["disposition_path"], "failure_mailbox/incident_engine.py#ingest_observation")
        ledger = self._ledger()
        self.assertEqual(ledger["schema"], "stegverse.healer.github-failure-ledger/v0.1")
        self.assertEqual(len(ledger["incidents"]), 2)
        self.assertEqual({i["state"] for i in ledger["incidents"].values()}, {"OPEN"})
        self.assertEqual(set(ledger["message_index"]), {"m1", "m2"})
        self.assertTrue((self.state_dir / "github-operational-failure-summary.json").is_file())
        # The hourly re-read is a no-op on the ledger.
        second = self._ingest()
        self.assertEqual(second["state"], "INGESTED")
        self.assertEqual(second["ingested_count"], 0)
        self.assertEqual(second["result_counts"]["duplicate_noop"], 2)
        self.assertEqual(len(self._ledger()["incidents"]), 2)
        self.assertEqual(self._ledger()["incidents"][first["incident_ids"][0]]["occurrence_count"], 1)

    def test_summary_construction_failure_does_not_persist_ledger(self) -> None:
        self._write_projection(projection([observation("m-summary-failure")]))
        engine, _ = subject._failure_mailbox_modules()
        with mock.patch.object(engine, "summary", side_effect=ValueError("summary unavailable")):
            result = self._ingest()
        self.assertEqual(result["state"], "BOUNDARY_RECORDED")
        self.assertEqual(result["boundary"], "LABS_HEALER_OBSERVATIONS_REJECTED")
        self.assertFalse((self.state_dir / "github-operational-failure-ledger.json").exists())
        self.assertFalse((self.state_dir / "github-operational-failure-summary.json").exists())


    def test_summary_write_failure_does_not_advance_incident_ledger(self) -> None:
        self._write_projection(projection([observation("m-summary-io-failure")]))
        engine, _ = subject._failure_mailbox_modules()
        original_save = engine.save_json

        def fail_summary_write(path, payload):
            if Path(path).name == "github-operational-failure-summary.json":
                raise OSError("simulated summary persistence failure")
            return original_save(path, payload)

        with mock.patch.object(engine, "save_json", side_effect=fail_summary_write):
            result = self._ingest()
        self.assertEqual(result["state"], "BOUNDARY_RECORDED")
        self.assertEqual(result["boundary"], "LABS_HEALER_OBSERVATIONS_REJECTED")
        self.assertFalse((self.state_dir / "github-operational-failure-ledger.json").exists())
        self.assertFalse((self.state_dir / "github-operational-failure-summary.json").exists())

    def test_new_representative_message_updates_the_same_incident(self) -> None:
        self._write_projection(projection([observation("m1")]))
        first = self._ingest()
        self._write_projection(projection([observation("m9", received_at="2026-10-06T00:00:00Z")]))
        second = self._ingest()
        self.assertEqual(second["result_counts"]["incident_updated"], 1)
        self.assertEqual(second["incident_ids"], first["incident_ids"])
        self.assertEqual(self._ledger()["incidents"][first["incident_ids"][0]]["occurrence_count"], 2)

    def test_duplicate_message_ids_within_the_file_are_deduped_before_ingest(self) -> None:
        self._write_projection(projection([observation("m1"), observation("m1")]))
        result = self._ingest()
        self.assertEqual(result["state"], "INGESTED")
        self.assertEqual(result["observation_count"], 1)
        self.assertEqual(result["result_counts"]["incident_created"], 1)

    def test_missing_projection_fails_closed(self) -> None:
        result = self._ingest()
        self.assertEqual(result["state"], "BOUNDARY_RECORDED")
        self.assertEqual(result["boundary"], "LABS_HEALER_OBSERVATIONS_NOT_MATERIALIZED")
        self.assertEqual(result["ingested_count"], 0)
        self.assertFalse(self.state_dir.exists())

    def test_missing_labs_root_fails_closed(self) -> None:
        result = subject._ingest_labs_outstanding_email_observations({}, self.schedule)
        self.assertEqual(result["state"], "BOUNDARY_RECORDED")
        self.assertEqual(result["boundary"], "LOCAL_DOTGITHUB_SOURCE_NOT_MATERIALIZED")

    def test_malformed_projection_ingests_nothing(self) -> None:
        cases = {
            "not json": "{not json",
            "wrong schema": projection([observation("m1")], schema="other/v9"),
            "claims authority": projection([observation("m1")], authority_effect="ALLOW"),
            "claims resolution": projection([observation("m1")], resolved_transition_claimed=True),
            "record schema": projection([observation("m1")], observation_schema="stegverse.healer.github-failure-observation/v0.1"),
            "count mismatch": projection([observation("m1")], observation_count=2),
            "row missing repository": projection([observation("m1"), observation("m2", repo="")]),
            "row claims authority": projection([observation("m1"), observation("m2", authority_effect=True)]),
        }
        for label, payload in cases.items():
            with self.subTest(label):
                self._write_projection(payload)
                result = self._ingest()
                self.assertEqual(result["state"], "BOUNDARY_RECORDED", label)
                self.assertEqual(result["boundary"], "LABS_HEALER_OBSERVATIONS_REJECTED", label)
                self.assertEqual(result["ingested_count"], 0)
                self.assertFalse((self.state_dir / "github-operational-failure-ledger.json").exists(), label)

    def test_not_enabled_in_schedule_is_skipped(self) -> None:
        self._write_schedule(enabled=False)
        self._write_projection(projection([observation("m1")]))
        result = self._ingest()
        self.assertEqual(result["state"], "NOT_ENABLED")
        self.assertFalse(self.state_dir.exists())

    def test_carrier_pass_carries_the_ingest_receipt(self) -> None:
        now = dt.datetime(2026, 10, 11, 20, 0, tzinfo=dt.timezone.utc)
        trigger = self.github_root / "scripts" / "trigger_reusable_task.py"
        trigger.parent.mkdir(parents=True)
        trigger.write_text("# neutral reusable trigger\n", encoding="utf-8")
        runtime_root = self.root / "heartbeat-runtime"
        marker = runtime_root / subject.RUNTIME_REQUIRED_REL
        marker.parent.mkdir(parents=True)
        marker.write_text("{}\n", encoding="utf-8")
        self._write_projection(projection([observation("m1")]))

        def fake_run(command, cwd, env, timeout):
            receipt = Path(command[command.index("--receipt") + 1])
            invocation = command[command.index("--invocation-id") + 1]
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps({"state": "AUTOMATABLE_STEPS_EXHAUSTED"}) + "\n")
            receipt.with_name(f"{invocation}.runner-result.json").write_text(json.dumps({
                "schema": "stegverse.reusable-task-runner-result/v1", "due_task_count": 1,
                "outcomes": [{"reusable_task_id": subject.NATIVE_EMAIL_TASK_ID, "state": "BOUNDARY_RECORDED"}],
            }) + "\n")
            return {"returncode": 0, "stdout_tail": "", "stderr_tail": ""}

        with mock.patch.object(subject.base, "build_and_execute", return_value={"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "COMPLETE"}), \
             mock.patch.object(subject.base, "_repo_roots", return_value={LABS_REPO: self.github_root}), \
             mock.patch.object(subject.base, "_now", return_value=now), \
             mock.patch.object(subject.base, "_run", side_effect=fake_run), \
             mock.patch.dict("os.environ", {"RUN_SCOPE": "all", "STEGVERSE_HEARTBEAT_ROOT": str(runtime_root)}, clear=False):
            result = subject.build_and_execute(self.root / "targets.json", self.schedule)

        self.assertEqual(result["state"], "COMPLETE")
        ingest = result["labs_outstanding_email_observation_ingest"]
        self.assertEqual(ingest["state"], "INGESTED")
        self.assertEqual(ingest["ingested_count"], 1)
        self.assertEqual(len(self._ledger()["incidents"]), 1)


if __name__ == "__main__":
    unittest.main()
