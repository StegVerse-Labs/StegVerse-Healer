from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "failure_mailbox" / "incident_engine.py"
spec = importlib.util.spec_from_file_location("failure_incident_engine", ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(engine)


class FailureMailboxIncidentEngineTests(unittest.TestCase):
    def observation(self, *, message_id: str, repo: str = "StegVerse-Labs/example", workflow: str = "validate", received_at: str = "2026-08-18T20:00:00+00:00", failure_message: str = "ModuleNotFoundError: No module named 'scripts'", commit: str = "abcdef1234567") -> dict:
        return {
            "message_id": message_id,
            "repository": repo,
            "workflow": workflow,
            "job": "consume",
            "branch": "main",
            "commit_sha": commit,
            "received_at": received_at,
            "subject": f"[{repo}] Run failed: {workflow}",
            "failure_message": failure_message,
        }

    def test_repeated_notifications_update_one_incident(self) -> None:
        ledger = engine.default_ledger()
        first = engine.ingest_observation(ledger, self.observation(message_id="m1", commit="abcdef1"))
        second = engine.ingest_observation(ledger, self.observation(message_id="m2", commit="abcdef2", received_at="2026-08-18T20:05:00+00:00"))
        self.assertEqual(first["result"], "incident_created")
        self.assertEqual(second["result"], "incident_updated")
        self.assertEqual(first["incident_id"], second["incident_id"])
        incident = ledger["incidents"][first["incident_id"]]
        self.assertEqual(incident["occurrence_count"], 2)
        self.assertEqual(incident["failure_class"], "MODULE_NOT_FOUND")
        self.assertEqual(set(incident["message_ids"]), {"m1", "m2"})

    def test_identical_message_is_duplicate_noop(self) -> None:
        ledger = engine.default_ledger()
        first = engine.ingest_observation(ledger, self.observation(message_id="m1"))
        duplicate = engine.ingest_observation(ledger, self.observation(message_id="m1"))
        self.assertEqual(duplicate["result"], "duplicate_noop")
        self.assertEqual(duplicate["incident_id"], first["incident_id"])
        self.assertEqual(ledger["incidents"][first["incident_id"]]["occurrence_count"], 1)

    def test_unable_to_repair_requires_sandbox(self) -> None:
        ledger = engine.default_ledger()
        result = engine.ingest_observation(ledger, self.observation(message_id="m1"))
        transitioned = engine.transition_incident(
            ledger,
            result["incident_id"],
            "UNABLE_TO_REPAIR",
            evidence_ref="worker-receipt:unable",
        )
        self.assertEqual(transitioned["state"], "SANDBOX_REQUIRED")
        self.assertEqual(ledger["incidents"][result["incident_id"]]["state"], "SANDBOX_REQUIRED")

    def test_resolved_requires_evidence_and_emits_archive_plan(self) -> None:
        ledger = engine.default_ledger()
        result = engine.ingest_observation(ledger, self.observation(message_id="m1"))
        engine.ingest_observation(ledger, self.observation(message_id="m2", commit="abcdef2"))
        with self.assertRaises(ValueError):
            engine.transition_incident(ledger, result["incident_id"], "RESOLVED")
        engine.transition_incident(ledger, result["incident_id"], "RESOLVED", evidence_ref="run:123:success")
        incident = ledger["incidents"][result["incident_id"]]
        self.assertEqual(set(incident["archive_eligible_message_ids"]), {"m1", "m2"})
        self.assertEqual(set(engine.summary(ledger)["archive_eligible_message_ids"]), {"m1", "m2"})

    def test_neighbor_candidate_detects_cross_repo_temporal_cluster(self) -> None:
        ledger = engine.default_ledger()
        a = engine.ingest_observation(
            ledger,
            self.observation(message_id="a", repo="StegVerse-Labs/A", received_at="2026-08-18T20:00:00+00:00", failure_message="route_unreachable"),
        )
        b = engine.ingest_observation(
            ledger,
            self.observation(message_id="b", repo="StegVerse-Labs/B", received_at="2026-08-18T20:02:00+00:00", failure_message="blocked_route_unreachable"),
        )
        engine.build_neighbor_candidates(ledger, 300)
        neighbors = ledger["incidents"][a["incident_id"]]["neighbor_candidates"]
        self.assertEqual(neighbors[0]["incident_id"], b["incident_id"])
        self.assertIn("same_failure_class", neighbors[0]["reasons"])
        self.assertFalse(engine.summary(ledger)["authority_effect"])
        self.assertFalse(engine.summary(ledger)["heartbeat_effect"])

    def test_ledger_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.json"
            ledger = engine.default_ledger()
            engine.ingest_observation(ledger, self.observation(message_id="m1"))
            engine.save_json(path, ledger)
            loaded = engine.load_ledger(path)
            self.assertEqual(loaded["message_index"]["m1"], "GF-000001")


if __name__ == "__main__":
    unittest.main()
