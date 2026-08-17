from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "app" / "pre_carrier_assist.py"
spec = importlib.util.spec_from_file_location("pre_carrier_assist", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PreCarrierAssistTests(unittest.TestCase):
    def _canonical_root(self, base: Path) -> Path:
        root = base / ".github"
        required = [
            "heartbeat_runtime/engine_v12.py",
            "heartbeat_runtime/worker_runtime.py",
            "scripts/advance_heartbeat_transition.py",
            "control/worker-registry.json",
            "control/process-worker-adapters.json",
        ]
        for rel in required:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")

        legacy = root / "control/heartbeat-state.json"
        legacy.write_text(json.dumps({"epoch": 29, "generation": 29}) + "\n", encoding="utf-8")

        contract = root / "management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json"
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(json.dumps({
            "legacy_epoch": 29,
            "legacy_source_immutable": True,
            "first_successor_epoch": 30,
            "canonical_runtime": "heartbeat_runtime.engine_v12.HeartbeatRuntime",
            "worker_runtime": "heartbeat_runtime.worker_runtime.WorkerCoordinator",
            "transition_producer": "scripts/advance_heartbeat_transition.py",
            "another_physical_machine_required": False,
            "always_on_external_host_required": False,
            "credential_boundary": {
                "credential_authority": "TV/TVC",
                "non_tv_tvc_secret_or_token_allowed": False,
            },
        }) + "\n", encoding="utf-8")

        handoff = root / "handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json"
        handoff.parent.mkdir(parents=True, exist_ok=True)
        handoff.write_text(json.dumps({
            "task": {"claim_state": "MACHINE_OWNED_BOUND_G18", "fencing_token": 18},
            "completion": {"live_activation_claimed": False},
        }) + "\n", encoding="utf-8")
        return root

    def test_ready_does_not_execute_transition_or_mutate_hb29(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._canonical_root(Path(td))
            legacy = root / "control/heartbeat-state.json"
            before = legacy.read_bytes()
            env = {"STEGVERSE_REPO_ROOTS_JSON": json.dumps({"StegVerse-Labs/.github": str(root)})}
            with patch.dict(os.environ, env, clear=True):
                receipt = mod.inspect_pre_carrier()
            self.assertEqual(receipt["state"], "READY_FOR_G18_TRANSITION")
            self.assertFalse(receipt["heartbeat_transition_executed"])
            self.assertFalse(receipt["hb30_synthesized"])
            self.assertEqual(legacy.read_bytes(), before)
            self.assertFalse((root / "control/heartbeat-carrier-runtime-state.json").exists())
            self.assertEqual(receipt["credential_authority"], "TV/TVC")
            self.assertFalse(receipt["github_token_required"])

    def test_forbidden_github_token_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._canonical_root(Path(td))
            env = {
                "STEGVERSE_REPO_ROOTS_JSON": json.dumps({"StegVerse-Labs/.github": str(root)}),
                "GITHUB_TOKEN": "forbidden",
            }
            with patch.dict(os.environ, env, clear=True):
                receipt = mod.inspect_pre_carrier()
            self.assertEqual(receipt["state"], "FAILED")
            self.assertIn("GITHUB_TOKEN", receipt["forbidden"])
            self.assertFalse(receipt["non_tv_tvc_secret_or_token_used"])

    def test_contract_drift_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = self._canonical_root(Path(td))
            contract_path = root / "management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["always_on_external_host_required"] = True
            contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
            env = {"STEGVERSE_REPO_ROOTS_JSON": json.dumps({"StegVerse-Labs/.github": str(root)})}
            with patch.dict(os.environ, env, clear=True):
                receipt = mod.inspect_pre_carrier()
            self.assertEqual(receipt["state"], "REVIEW_REQUIRED")
            self.assertIn("contract_no_always_on_host", receipt["failed_checks"])

    def test_missing_local_source_blocks_without_remote_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / ".github"
            root.mkdir()
            env = {"STEGVERSE_REPO_ROOTS_JSON": json.dumps({"StegVerse-Labs/.github": str(root)})}
            with patch.dict(os.environ, env, clear=True):
                receipt = mod.inspect_pre_carrier()
            self.assertEqual(receipt["state"], "BLOCKED")
            self.assertEqual(receipt["reason"], "REQUIRED_LOCAL_SOURCE_MISSING")
            self.assertFalse(receipt["github_token_required"])


if __name__ == "__main__":
    unittest.main()
