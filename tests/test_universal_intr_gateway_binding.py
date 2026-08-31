from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app import coinbase_stegdeploy_gateway as mod


class UniversalInTrGatewayBindingTests(unittest.TestCase):
    def test_exact_canonical_upstream_enabled(self):
        with patch.dict(os.environ, {
            mod.HIL_INTR_ENABLED_ENV: "true",
            mod.HIL_INTR_UPSTREAM_ENV: mod.HIL_INTR_LOOPBACK_UPSTREAM,
        }, clear=False):
            self.assertEqual(mod.hil_intr_runtime_config(), {
                "enabled": True,
                "upstream": "http://127.0.0.1:8765/intr/materialization",
            })

    def test_remote_or_wrong_loopback_upstream_rejected(self):
        for upstream in (
            "https://remote.example/intr/materialization",
            "http://127.0.0.1:9999/intr/materialization",
            "http://127.0.0.1:8765/other",
        ):
            with patch.dict(os.environ, {
                mod.HIL_INTR_ENABLED_ENV: "true",
                mod.HIL_INTR_UPSTREAM_ENV: upstream,
            }, clear=False):
                with self.assertRaisesRegex(mod.GatewayActivationError, "HIL_INTR_UPSTREAM_NOT_CANONICAL_LOOPBACK"):
                    mod.hil_intr_runtime_config()

    def test_disabled_route_does_not_expose_upstream(self):
        with patch.dict(os.environ, {
            mod.HIL_INTR_ENABLED_ENV: "false",
            mod.HIL_INTR_UPSTREAM_ENV: "",
        }, clear=False):
            self.assertEqual(mod.hil_intr_runtime_config(), {"enabled": False, "upstream": ""})

    def test_readiness_contract_accepts_exact_non_authorizing_profile(self):
        mod.validate_hil_intr_gateway_readiness({
            "schema": "stegverse.service-gateway.hil-intr-readiness/v1",
            "enabled": True,
            "loopback_upstream_configured": True,
            "state": "READY",
            "transport": "InTr",
            "supported_origins": ["STEGOS_NODE_OUTBOX", "TVC_RELAY_EGRESS"],
            "event_triggered": True,
            "always_on_receiver_required": False,
            "second_user_device_required": False,
            "g18_completion_required": False,
            "credential_authority": "TV/TVC",
            "github_token_runtime_authority": "NONE",
            "gateway_receipt_authority": False,
            "gateway_execution_authority": False,
            "gateway_custody_authority": False,
            "authority_effect": "NONE",
            "reason": None,
        })

    def test_readiness_contract_rejects_execution_authority(self):
        payload = {
            "schema": "stegverse.service-gateway.hil-intr-readiness/v1",
            "enabled": True,
            "loopback_upstream_configured": True,
            "state": "READY",
            "transport": "InTr",
            "event_triggered": True,
            "always_on_receiver_required": False,
            "second_user_device_required": False,
            "g18_completion_required": False,
            "credential_authority": "TV/TVC",
            "github_token_runtime_authority": "NONE",
            "gateway_receipt_authority": False,
            "gateway_execution_authority": True,
            "gateway_custody_authority": False,
            "authority_effect": "NONE",
        }
        with self.assertRaisesRegex(mod.GatewayActivationError, "gateway_execution_authority"):
            mod.validate_hil_intr_gateway_readiness(payload)

    def test_clean_env_propagates_only_nonsecret_hil_intr_binding(self):
        env = mod._clean_env(
            {"decision_id": "sha256:" + "a" * 64},
            hil_intr={"enabled": True, "upstream": mod.HIL_INTR_LOOPBACK_UPSTREAM},
        )
        self.assertEqual(env[mod.HIL_INTR_ENABLED_ENV], "true")
        self.assertEqual(env[mod.HIL_INTR_UPSTREAM_ENV], mod.HIL_INTR_LOOPBACK_UPSTREAM)
        self.assertNotIn("GITHUB_TOKEN", env)

    def test_minimum_gateway_commit_is_profile_projection_merge(self):
        self.assertEqual(
            mod.MINIMUM_UNIVERSAL_INTR_GATEWAY_COMMIT,
            "49676d20cff32ee346f22cfd79726b0127d80b33",
        )


if __name__ == "__main__":
    unittest.main()
