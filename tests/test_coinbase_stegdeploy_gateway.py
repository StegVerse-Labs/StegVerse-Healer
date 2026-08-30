from __future__ import annotations

import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from app import coinbase_stegdeploy_gateway as mod


class CoinbaseStegDeployGatewayTests(unittest.TestCase):
    def decision(self) -> dict:
        body = {
            "schema": "stegverse.tvc.coinbase_service_gateway_no_value_decision/v1",
            "role": "service_gateway_coinbase_skap_ciphertext_intake",
            "admissible": True,
            "binding_matched": True,
            "allowed_keys": [],
            "denied_keys": [],
            "credential_values_available": False,
            "decision_id": "sha256:" + "d" * 64,
            "policy_hash": "sha256:" + "a" * 64,
        }
        return {**body, "receipt_digest": mod.digest(body)}

    def redigest(self, receipt: dict) -> None:
        body = {k: v for k, v in receipt.items() if k != "receipt_digest"}
        receipt["receipt_digest"] = mod.digest(body)

    def test_decision_requires_no_value_tvc_scope(self) -> None:
        mod.validate_decision(self.decision())
        bad = self.decision()
        bad["credential_values_available"] = True
        self.redigest(bad)
        with self.assertRaisesRegex(mod.GatewayActivationError, "CREDENTIAL_VALUE_SCOPE"):
            mod.validate_decision(bad)

    def test_decision_tamper_is_rejected_before_runtime(self) -> None:
        bad = self.decision()
        bad["admissible"] = False
        with self.assertRaisesRegex(mod.GatewayActivationError, "RECEIPT_DIGEST_INVALID"):
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


    def test_tls_locators_are_path_only_and_must_be_paired(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cert = root / "cert.pem"
            key = root / "key.pem"
            cert.write_text("cert", encoding="utf-8")
            key.write_text("key", encoding="utf-8")

            old = dict(os.environ)
            try:
                os.environ[mod.TLS_CERT_ENV] = str(cert)
                os.environ.pop(mod.TLS_KEY_ENV, None)
                with self.assertRaisesRegex(mod.GatewayActivationError, "MUST_BE_PAIRED"):
                    mod.resolve_tls_request()

                os.environ[mod.TLS_KEY_ENV] = str(key)
                os.environ[mod.TLS_BIND_ENV] = "0.0.0.0"
                os.environ[mod.TLS_PORT_ENV] = "443"
                with mock.patch.object(mod, "TVC_TLS_CREDENTIAL_ROOT", root):
                    request = mod.resolve_tls_request()
                self.assertIsNotNone(request)
                self.assertEqual(request["cert_file"], cert.resolve())
                self.assertEqual(request["key_file"], key.resolve())
                self.assertEqual(request["bind_address"], "0.0.0.0")
                self.assertEqual(request["port"], 443)
            finally:
                os.environ.clear()
                os.environ.update(old)

    def tls_adoption_receipt(self, cert: Path, key: Path) -> dict:
        body = {
            "schema": mod.TLS_ADOPTION_SCHEMA,
            "state": "READY_FOR_STEGDEPLOY_TLS",
            "hostname": "gateway.stegverse.org",
            "certificate_sha256": "sha256:" + "c" * 64,
            "certificate_not_before": "Aug 27 00:00:00 2026 GMT",
            "certificate_not_after": "Aug 27 00:00:00 2027 GMT",
            "certificate_hostname": "gateway.stegverse.org",
            "certificate_file_locator": str(cert),
            "private_key_file_locator": str(key),
            "certificate_material_present": True,
            "private_key_material_present": True,
            "private_key_bytes_recorded": False,
            "private_key_exported": False,
            "credential_material_exported": False,
            "certificate_pair_verified": True,
            "certificate_hostname_verified": True,
            "certificate_time_valid": True,
            "certificate_acquisition_performed": False,
            "certificate_issuance_performed": False,
            "certificate_renewal_performed": False,
            "certificate_revocation_performed": False,
            "generalized_certificate_manager_created": False,
            "credential_authority": "TV/TVC",
            "gateway_credential_authority": "NONE",
            "provider_operation_authority": "NONE",
            "github_token_required": False,
            "production_public_route_observed": False,
            "ready_for_owner_ingress": False,
            "authority_effect": "TVC_RESIDENT_TLS_MATERIAL_ADOPTION_ONLY",
        }
        return {**body, "receipt_sha256": mod.digest(body)}

    def test_tls_auto_discovers_valid_tvc_adoption_receipt(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            credential_root = root / "credentials"
            credential_root.mkdir()
            cert = credential_root / "cert.pem"
            key = credential_root / "key.pem"
            cert.write_text("cert", encoding="utf-8")
            key.write_text("key", encoding="utf-8")
            receipt_path = root / "adoption.json"
            receipt = self.tls_adoption_receipt(cert, key)
            receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")

            old = dict(os.environ)
            try:
                os.environ.pop(mod.TLS_CERT_ENV, None)
                os.environ.pop(mod.TLS_KEY_ENV, None)
                os.environ[mod.TLS_ADOPTION_RECEIPT_ENV] = str(receipt_path)
                with mock.patch.object(mod, "TVC_TLS_CREDENTIAL_ROOT", credential_root):
                    request = mod.resolve_tls_request()
            finally:
                os.environ.clear()
                os.environ.update(old)

            self.assertIsNotNone(request)
            self.assertEqual(request["cert_file"], cert.resolve())
            self.assertEqual(request["key_file"], key.resolve())
            self.assertEqual(request["locator_source"], "TVC_TLS_ADOPTION_RECEIPT")
            self.assertEqual(request["adoption_receipt_sha256"], receipt["receipt_sha256"])
            self.assertEqual(request["port"], 443)

    def test_tls_adoption_receipt_tamper_or_issuance_claim_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            credential_root = root / "credentials"
            credential_root.mkdir()
            cert = credential_root / "cert.pem"
            key = credential_root / "key.pem"
            cert.write_text("cert", encoding="utf-8")
            key.write_text("key", encoding="utf-8")
            with mock.patch.object(mod, "TVC_TLS_CREDENTIAL_ROOT", credential_root):
                tampered = self.tls_adoption_receipt(cert, key)
                tampered["hostname"] = "evil.example"
                with self.assertRaisesRegex(mod.GatewayActivationError, "DIGEST_INVALID"):
                    mod.validate_tls_adoption_receipt(tampered)

                issuance = self.tls_adoption_receipt(cert, key)
                issuance["certificate_issuance_performed"] = True
                body = {k: v for k, v in issuance.items() if k != "receipt_sha256"}
                issuance["receipt_sha256"] = mod.digest(body)
                with self.assertRaisesRegex(mod.GatewayActivationError, "BOUNDARY_INVALID"):
                    mod.validate_tls_adoption_receipt(issuance)

    def test_tls_adoption_locator_must_remain_inside_tvc_credential_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            credential_root = root / "credentials"
            credential_root.mkdir()
            cert = credential_root / "cert.pem"
            cert.write_text("cert", encoding="utf-8")
            outside = root / "outside-key.pem"
            outside.write_text("key", encoding="utf-8")
            receipt = self.tls_adoption_receipt(cert, outside)
            with mock.patch.object(mod, "TVC_TLS_CREDENTIAL_ROOT", credential_root):
                with self.assertRaisesRegex(mod.GatewayActivationError, "OUTSIDE_TVC_ROOT"):
                    mod.validate_tls_adoption_receipt(receipt)

    def test_explicit_tls_locators_override_adoption_receipt_discovery(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cert = root / "explicit-cert.pem"
            key = root / "explicit-key.pem"
            cert.write_text("cert", encoding="utf-8")
            key.write_text("key", encoding="utf-8")
            old = dict(os.environ)
            try:
                os.environ[mod.TLS_CERT_ENV] = str(cert)
                os.environ[mod.TLS_KEY_ENV] = str(key)
                os.environ[mod.TLS_ADOPTION_RECEIPT_ENV] = str(root / "missing-adoption.json")
                with mock.patch.object(mod, "TVC_TLS_CREDENTIAL_ROOT", root):
                    request = mod.resolve_tls_request()
            finally:
                os.environ.clear()
                os.environ.update(old)

            self.assertEqual(request["locator_source"], "EXPLICIT_TV_TVC_RUNTIME_FILE_PATHS")
            self.assertIsNone(request["adoption_receipt_sha256"])

    def test_explicit_tls_locator_outside_tvc_root_is_rejected(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            credential_root = root / "credentials"
            credential_root.mkdir()
            cert = root / "outside-cert.pem"
            key = root / "outside-key.pem"
            cert.write_text("cert", encoding="utf-8")
            key.write_text("key", encoding="utf-8")
            old = dict(os.environ)
            try:
                os.environ[mod.TLS_CERT_ENV] = str(cert)
                os.environ[mod.TLS_KEY_ENV] = str(key)
                with mock.patch.object(mod, "TVC_TLS_CREDENTIAL_ROOT", credential_root):
                    with self.assertRaisesRegex(mod.GatewayActivationError, "OUTSIDE_TVC_ROOT"):
                        mod.resolve_tls_request()
            finally:
                os.environ.clear()
                os.environ.update(old)

    def test_tls_deploy_command_uses_native_gateway_without_secret_values(self) -> None:
        request = {
            "cert_file": Path("/runtime/tvc/gateway-cert.pem"),
            "key_file": Path("/runtime/tvc/gateway-key.pem"),
            "bind_address": "0.0.0.0",
            "port": 443,
        }
        command, readiness_url, tls_enabled = mod.build_deploy_command(request)
        self.assertTrue(tls_enabled)
        self.assertIn("scripts/stegdeploy_native_gateway.py", command)
        self.assertIn("start", command)
        self.assertNotIn("/runtime/tvc/gateway-cert.pem", command)
        self.assertNotIn("/runtime/tvc/gateway-key.pem", command)
        self.assertIn("0.0.0.0", command)
        self.assertIn("443", command)
        self.assertEqual(readiness_url, "https://127.0.0.1:443/api/coinbase/skap/readiness")
        self.assertNotIn("PRIVATE KEY", " ".join(command))
        self.assertNotIn("BEGIN CERTIFICATE", " ".join(command))

    def test_http_mode_remains_local_and_non_public(self) -> None:
        command, readiness_url, tls_enabled = mod.build_deploy_command(None)
        self.assertFalse(tls_enabled)
        self.assertIn("scripts/stegdeploy_native_gateway.py", command)
        self.assertIn("start", command)
        self.assertEqual(readiness_url, mod.READINESS_URL)
        self.assertTrue(readiness_url.startswith("http://127.0.0.1:"))


    def test_evaluator_runtime_config_is_fail_closed_and_loopback_only(self) -> None:
        import os
        old = dict(os.environ)
        try:
            os.environ.pop(mod.EVALUATOR_ENABLED_ENV, None)
            os.environ.pop(mod.EVALUATOR_UPSTREAM_ENV, None)
            disabled = mod.evaluator_runtime_config()
            self.assertFalse(disabled["enabled"])

            os.environ[mod.EVALUATOR_ENABLED_ENV] = "true"
            os.environ[mod.EVALUATOR_UPSTREAM_ENV] = mod.EVALUATOR_LOOPBACK_UPSTREAM
            enabled = mod.evaluator_runtime_config()
            self.assertTrue(enabled["enabled"])
            self.assertEqual(enabled["upstream"], mod.EVALUATOR_LOOPBACK_UPSTREAM)

            os.environ[mod.EVALUATOR_UPSTREAM_ENV] = "http://192.0.2.9:8765/intr/evaluator"
            with self.assertRaisesRegex(mod.GatewayActivationError, "NOT_CANONICAL_LOOPBACK"):
                mod.evaluator_runtime_config()
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_clean_env_carries_tls_paths_and_evaluator_only_as_runtime_config(self) -> None:
        request = {
            "cert_file": Path("/run/stegverse/tv-tvc-credentials/cert.pem"),
            "key_file": Path("/run/stegverse/tv-tvc-credentials/key.pem"),
        }
        env = mod._clean_env(
            self.decision(),
            tls_request=request,
            evaluator={"enabled": True, "upstream": mod.EVALUATOR_LOOPBACK_UPSTREAM},
        )
        self.assertEqual(env["STEGDEPLOY_NATIVE_TLS_CERT_FILE"], str(request["cert_file"]))
        self.assertEqual(env["STEGDEPLOY_NATIVE_TLS_KEY_FILE"], str(request["key_file"]))
        self.assertEqual(env[mod.EVALUATOR_ENABLED_ENV], "true")
        self.assertEqual(env[mod.EVALUATOR_UPSTREAM_ENV], mod.EVALUATOR_LOOPBACK_UPSTREAM)
        self.assertNotIn("GITHUB_TOKEN", env)

    def test_sv002_observation_runtime_config_is_fail_closed_and_loopback_only(self) -> None:
        import os
        old = dict(os.environ)
        try:
            os.environ.pop(mod.SV002_OBSERVE_ENABLED_ENV, None)
            os.environ.pop(mod.SV002_OBSERVE_UPSTREAM_ENV, None)
            disabled = mod.sv002_observation_runtime_config()
            self.assertFalse(disabled["enabled"])

            os.environ[mod.SV002_OBSERVE_ENABLED_ENV] = "true"
            os.environ[mod.SV002_OBSERVE_UPSTREAM_ENV] = mod.SV002_OBSERVE_LOOPBACK_UPSTREAM
            enabled = mod.sv002_observation_runtime_config()
            self.assertTrue(enabled["enabled"])
            self.assertEqual(enabled["upstream"], mod.SV002_OBSERVE_LOOPBACK_UPSTREAM)

            os.environ[mod.SV002_OBSERVE_UPSTREAM_ENV] = "http://192.0.2.9:8766/intr/sv002-observe"
            with self.assertRaisesRegex(mod.GatewayActivationError, "NOT_CANONICAL_LOOPBACK"):
                mod.sv002_observation_runtime_config()
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_clean_env_carries_sv002_observation_only_as_runtime_config(self) -> None:
        env = mod._clean_env(
            self.decision(),
            evaluator={"enabled": False, "upstream": ""},
            sv002_observe={"enabled": True, "upstream": mod.SV002_OBSERVE_LOOPBACK_UPSTREAM},
        )
        self.assertEqual(env[mod.SV002_OBSERVE_ENABLED_ENV], "true")
        self.assertEqual(env[mod.SV002_OBSERVE_UPSTREAM_ENV], mod.SV002_OBSERVE_LOOPBACK_UPSTREAM)
        self.assertNotIn("GITHUB_TOKEN", env)


    def test_sv002_gateway_readiness_requires_exact_authority_neutral_projection(self) -> None:
        payload = {
            "schema": "stegverse.service-gateway.sv002-observation-readiness/v1",
            "enabled": True,
            "loopback_upstream_configured": True,
            "state": "READY",
            "transport": "InTr",
            "credential_authority": "TV/TVC",
            "gateway_receipt_authority": False,
            "gateway_experiment_authority": False,
            "authority_effect": "NONE",
        }
        mod.validate_sv002_gateway_readiness(payload)
        bad = dict(payload)
        bad["gateway_experiment_authority"] = True
        with self.assertRaisesRegex(
            mod.GatewayActivationError,
            "SV002_OBSERVATION_GATEWAY_READINESS_INVALID",
        ):
            mod.validate_sv002_gateway_readiness(bad)

    def test_sv002_gateway_readiness_url_tracks_existing_native_gateway_mode(self) -> None:
        self.assertEqual(
            mod._sv002_gateway_readiness_url(tls_enabled=False, tls_request=None),
            "http://127.0.0.1:8000/intr/sv002-observe/readiness",
        )
        self.assertEqual(
            mod._sv002_gateway_readiness_url(
                tls_enabled=True,
                tls_request={"port": 443},
            ),
            "https://127.0.0.1:443/intr/sv002-observe/readiness",
        )

    def test_sv002_readiness_is_required_only_when_observation_route_enabled(self) -> None:
        source = Path(mod.__file__).read_text(encoding="utf-8")
        self.assertIn('if sv002_observe["enabled"]:', source)
        self.assertIn("validate_sv002_gateway_readiness(sv002_readiness)", source)
        self.assertIn("LOCAL_SV002_OBSERVATION_GATEWAY_READINESS_UNAVAILABLE", source)


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
