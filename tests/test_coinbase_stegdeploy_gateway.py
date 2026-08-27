from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import coinbase_stegdeploy_gateway as mod


class CoinbaseStegDeployGatewayTests(unittest.TestCase):
    def decision(self) -> dict:
        return {
            "role": "service_gateway_coinbase_skap_ciphertext_intake",
            "admissible": True,
            "binding_matched": True,
            "allowed_keys": [],
            "denied_keys": [],
            "credential_values_available": False,
            "decision_id": "sha256:test-decision",
            "policy_hash": "sha256:test-policy",
        }

    def test_decision_requires_no_value_tvc_scope(self) -> None:
        mod.validate_decision(self.decision())
        bad = self.decision()
        bad["credential_values_available"] = True
        with self.assertRaisesRegex(mod.GatewayActivationError, "CREDENTIAL_VALUE_SCOPE"):
            mod.validate_decision(bad)

    def test_readiness_preserves_gateway_authority_boundary(self) -> None:
        decision = self.decision()
        payload = {
            "state": "READY",
            "service_id": "stegverse-service-gateway",
            "adapter": "coinbase-skap-ciphertext-staging",
            "transport_protocol": "InTr",
            "completed_boundary": "DEVICE_TO_KV",
            "credential_authority": "TV/TVC",
            "gateway_credential_value_access": False,
            "gateway_decryption_authority": False,
            "gateway_execution_authority": "NONE",
            "tvc_admission_completed": False,
            "skap_vault_admission_completed": False,
            "next_required_transition": "KV_SKAP_VAULT_INTERLOCK_ADMISSION",
            "tvc_decision_id": decision["decision_id"],
        }
        mod.validate_readiness(payload, decision)
        payload["gateway_execution_authority"] = "ORDER"
        with self.assertRaisesRegex(mod.GatewayActivationError, "READINESS_BOUNDARY_INVALID"):
            mod.validate_readiness(payload, decision)

    def test_missing_decision_fails_closed_without_fabrication(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(mod.GatewayActivationError, "NOT_MATERIALIZED"):
                mod.locate_decision(root)

    def test_scheduler_target_is_registered_and_bounded(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / "data/orchestrator_targets.json").read_text(encoding="utf-8"))
        targets = [
            row for row in config["targets"]
            if row.get("repo") == "StegVerse-org/LLM-adapter"
            and row.get("workflow") == "coinbase-stegdeploy-sovereign-gateway"
        ]
        self.assertEqual(len(targets), 1)
        target = targets[0]
        self.assertTrue(target["enabled"])
        self.assertEqual(target["canonical_owner"], "StegVerse-Labs/TVC#119")
        self.assertIn("no-provider-authority", target["status"])
        scheduler = (root / "app/sovereign_scheduler.py").read_text(encoding="utf-8")
        self.assertIn('workflow == "coinbase-stegdeploy-sovereign-gateway"', scheduler)
        self.assertIn("execute_coinbase_gateway(all_roots_json)", scheduler)


if __name__ == "__main__":
    unittest.main()
