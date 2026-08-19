from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "failure_mailbox" / "sovereign_tvc_intake.py"
spec = importlib.util.spec_from_file_location("sovereign_tvc_intake", MODULE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def response() -> dict:
    return {
        "decision": "ALLOW_OPERATION_RESULT",
        "batch": [
            {
                "id": "a" * 64,
                "thread_id": "b" * 64,
                "internet_message_id": "c" * 64,
                "email_ts": "2026-08-19T13:27:23Z",
                "subject": "[GitHub] You've hit 100% of your budget for the StegVerse-Labs account",
                "snippet": "Budget exhausted",
                "signal_class": "ACTIONS_BUDGET_EXHAUSTED",
                "severity": "FAILURE",
                "account": "StegVerse-Labs",
                "threshold_percent": 100,
            }
        ],
        "manifest": {
            "schema": "stegverse.tvc.mailbox-failure-observation-manifest/v3",
            "source_count": 1,
            "materialized_count": 1,
            "scanned_message_count": 3,
            "signal_counts": {"ACTIONS_BUDGET_EXHAUSTED": 1},
            "mailbox_mutated": False,
            "credential_authority": "TV/TVC",
            "credential_value_exposed": False,
            "credential_value_persisted": False,
            "consumer_credential_exported": False,
            "provider_message_ids_exported": False,
            "partial_materialization": False,
            "authority_effect": False,
        },
        "grant_receipt": {
            "schema": "stegverse.tvc.mailbox_failure_observation_grant/v1",
            "decision": "ALLOW_CAPABILITY_LEASE",
            "credential_authority": "TV/TVC",
            "credential_value_recorded": False,
            "protected_values_recorded": False,
        },
        "use_receipt": {
            "secret_material_returned": False,
            "secret_material_logged": False,
            "secret_material_retained": False,
            "mailbox_mutated": False,
            "consumer_credential_exported": False,
            "authority_effect": False,
        },
    }


class SovereignTvcMailboxIntakeTests(unittest.TestCase):
    def test_endpoint_must_be_loopback(self) -> None:
        self.assertEqual(module.validate_endpoint(module.DEFAULT_ENDPOINT), module.DEFAULT_ENDPOINT)
        with self.assertRaises(ValueError):
            module.validate_endpoint("https://example.com/v1/mailbox-failure-observation")

    def test_request_contains_no_credential_values(self) -> None:
        req = module.build_request(
            dt.datetime(2026, 8, 19, 14, 0, tzinfo=dt.timezone.utc),
            window_minutes=20,
            lag_minutes=2,
            maximum_messages=1000,
        )
        text = str(req).lower()
        self.assertNotIn("secret", text)
        self.assertNotIn("token", text)
        self.assertEqual(req["caller_repository"], "StegVerse-Labs/StegVerse-Healer")

    def test_capacity_exhaustion_enters_incident_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = module.consume_response(response(), Path(temp))
            self.assertEqual(result["state"], "COMPLETE")
            self.assertEqual(result["materialized_count"], 1)
            self.assertEqual(result["signal_counts"]["ACTIONS_BUDGET_EXHAUSTED"], 1)
            ledger = module.incident_engine.load_ledger(Path(temp) / "github-operational-failure-ledger.json")
            incidents = list(ledger["incidents"].values())
            self.assertEqual(len(incidents), 1)
            self.assertEqual(incidents[0]["repository"], "github-account:StegVerse-Labs")
            self.assertEqual(incidents[0]["failure_class"], "ACTIONS_BUDGET_EXHAUSTED")
            self.assertEqual(incidents[0]["state"], "OPEN")

    def test_protected_response_material_is_rejected(self) -> None:
        bad = response()
        bad["access_token"] = "forbidden"
        with self.assertRaises(ValueError):
            module.validate_response(bad)


if __name__ == "__main__":
    unittest.main()
