from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class G18GateRetirementTests(unittest.TestCase):
    def test_current_machine_continuation_uses_independent_resident_task_control(self):
        state = json.loads(
            (ROOT / "data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json").read_text()
        )
        continuation = state["canonical_machine_continuation"]
        self.assertFalse(continuation["g18_terminalization_required"])
        self.assertIn("native resident WorkerCoordinator", continuation["execution_owner"])
        self.assertIn("RESIDENT-EXEC-HEALER-SOVEREIGN-SCHEDULER-001", continuation["next_executable_action"])
        self.assertIn("Do not wait on G18 terminalization", continuation["next_executable_action"])

    def test_current_handoff_does_not_state_scheduler_depends_on_durable_runtime(self):
        handoff = (ROOT / "docs/HEALER_MIRROR_HANDOFF.md").read_text()
        self.assertIn("does not depend on G18 terminalization", handoff)
        self.assertIn("resident scheduler gate correction", handoff)
        self.assertNotIn(
            "The scheduler depends on `SHWP-DURABLE-RUNTIME-ACTIVATION`.",
            handoff,
        )

    def test_erl_handoff_uses_same_independent_scheduler_semantics(self):
        handoff = (ROOT / "docs/SITE_ERL_SOVEREIGN_SYNC_MIRROR_HANDOFF.md").read_text()
        self.assertIn("superseded as a downstream gate", handoff)
        self.assertIn("RESIDENT-EXEC-HEALER-SOVEREIGN-SCHEDULER-001", handoff)


if __name__ == "__main__":
    unittest.main()
