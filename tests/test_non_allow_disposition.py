"""Every non-ALLOW record Healer produces carries the six disposition fields.

Task Registry ECOSYSTEM_STATE_TRANSITION_DISPOSITION_INVARIANT (LLM-adapter#368 Q8/Q7):
no bare BLOCKED. Each producer's blocked path is exercised where it can run
without external machines; an AST scan covers the producer dict literals.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from app import actions_cost_reducer, audit_schedules, pre_carrier_assist, sovereign_scheduler  # noqa: E402
from app import run_ece_periodic_evaluation, site_erl_sync  # noqa: E402
from app.disposition import DISPOSITION_FIELDS, NOT_AUTHENTICALLY_OBSERVED, missing_disposition_fields, non_allow  # noqa: E402
from app.ece_periodic_evaluation import execute_periodic_ece  # noqa: E402
import reusable_task_scheduler  # noqa: E402

NON_ALLOW_STATES = {"BLOCKED", "FAILED", "FAIL_CLOSED", "DENY", "REVIEW_REQUIRED"}
CLEAN_ENV = {name: "" for name in sovereign_scheduler.FORBIDDEN_CREDENTIALS + pre_carrier_assist.FORBIDDEN_CREDENTIALS}


class DispositionAssertions(unittest.TestCase):
    def assert_six_fields(self, record: dict) -> None:
        self.assertIn(record.get("state"), NON_ALLOW_STATES, record)
        self.assertEqual(missing_disposition_fields(record), [], record)


class TestDispositionHelper(DispositionAssertions):
    def test_helper_returns_exactly_the_six_non_empty_fields(self) -> None:
        fields = non_allow("CODE", "predicate", "repair", retry_entrypoint="python -m app.x")
        self.assertEqual(tuple(fields), DISPOSITION_FIELDS)
        self.assertTrue(all(fields.values()))
        self.assertEqual(fields["owning_existing_goal"], "LLMA-DECLARED-PATH-CONFORMANCE-368")


class TestSovereignScheduler(DispositionAssertions):
    def test_every_non_allow_outcome_has_a_specific_disposition(self) -> None:
        tree = ast.parse((APP / "sovereign_scheduler.py").read_text(encoding="utf-8"))
        handler = next(node for node in ast.walk(tree)
                       if isinstance(node, ast.FunctionDef) and node.name == "_execute_target_handler")
        outcomes = set()
        for node in ast.walk(handler):
            if not isinstance(node, ast.Dict):
                continue
            pairs = {key.value: value for key, value in zip(node.keys, node.values)
                     if isinstance(key, ast.Constant)}
            state, outcome = pairs.get("state"), pairs.get("outcome")
            if outcome is None or not isinstance(outcome, ast.Constant):
                continue
            if isinstance(state, ast.Constant) and state.value == "COMPLETE":
                continue
            outcomes.add(outcome.value)
        self.assertGreater(len(outcomes), 30)
        self.assertEqual(sorted(outcomes - set(sovereign_scheduler.OUTCOME_DISPOSITIONS)), [])
        codes = [entry[0] for entry in sovereign_scheduler.OUTCOME_DISPOSITIONS.values()]
        self.assertTrue(all(all(entry) for entry in sovereign_scheduler.OUTCOME_DISPOSITIONS.values()))
        self.assertEqual(len(codes), len(set(codes)))

    def test_unmaterialized_repository_block_carries_the_six_fields(self) -> None:
        target = {"repo": "StegVerse-Labs/SCW", "workflow": "scw_orchestrator.yml", "aliases": ["scw"]}
        result = sovereign_scheduler._execute_target(target, {}, "{}")
        self.assert_six_fields(result)
        self.assertEqual(result["failure_code"], "LOCAL_REPOSITORY_NOT_MATERIALIZED")
        self.assertEqual(result["retry_entrypoint"], "RUN_SCOPE=scw DISPATCH_MODE=manual python -m app.sovereign_scheduler")

    def test_canonical_owner_is_the_owning_existing_goal(self) -> None:
        target = {"repo": "StegVerse-Labs/Site", "workflow": "heartbeat-response-sovereign-carrier",
                  "canonical_owner": "StegVerse-Labs/Site#234"}
        result = sovereign_scheduler._execute_target(target, {}, "{}")
        self.assert_six_fields(result)
        self.assertEqual(result["owning_existing_goal"], "StegVerse-Labs/Site#234")

    def test_unbound_handler_review_required_carries_the_six_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            result = sovereign_scheduler._execute_target(
                {"repo": "Example/Repo", "workflow": "x.yml"}, {"Example/Repo": Path(td)}, "{}")
        self.assertEqual(result["state"], "REVIEW_REQUIRED")
        self.assert_six_fields(result)
        self.assertEqual(result["failure_code"], "NO_SOVEREIGN_HANDLER_BOUND")

    def test_mixed_outcome_site_names_the_non_allow_condition(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(sovereign_scheduler, "_run", return_value={"returncode": 1, "stdout_tail": "", "stderr_tail": "x"}):
                result = sovereign_scheduler._execute_target(
                    {"repo": "StegVerse-Labs/Continuity", "workflow": "continuity.yml"},
                    {"StegVerse-Labs/Continuity": Path(td)}, "{}")
        self.assert_six_fields(result)
        self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_CONTINUITY_GUARDIAN")
        self.assertEqual(result["failure_code"], "CONTINUITY_GUARDIAN_NONZERO_EXIT")

    def test_terminal_receipt_and_exception_receipt_carry_the_six_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "targets.json"
            config.write_text(json.dumps({"targets": [{"repo": "StegVerse-Labs/SCW", "workflow": "scw_orchestrator.yml"}]}), encoding="utf-8")
            with mock.patch.dict(os.environ, {**CLEAN_ENV, "STEGVERSE_REPO_ROOTS_JSON": "{}", "DISPATCH_MODE": "manual", "RUN_SCOPE": "all"}):
                receipt = sovereign_scheduler.build_and_execute(config)
        self.assert_six_fields(receipt)
        self.assertTrue(receipt["failure_code"].startswith("SCHEDULER_TARGET_BLOCKED:LOCAL_REPOSITORY_NOT_MATERIALIZED"))
        with mock.patch.dict(os.environ, {**CLEAN_ENV, "TARGETS_FILE": "/nonexistent/targets.json"}), \
                mock.patch("builtins.print") as printed:
            self.assertEqual(sovereign_scheduler.main(), 3)
        self.assert_six_fields(json.loads(printed.call_args[0][0]))


class TestSiteErlSync(DispositionAssertions):
    def test_blocked_paths_carry_the_six_fields(self) -> None:
        with mock.patch.dict(os.environ, CLEAN_ENV):
            result = site_erl_sync.execute_site_erl_sync({}, {}, {"repo": "StegVerse-Labs/Site"})
        self.assert_six_fields(result)
        self.assertEqual(result["failure_code"], "SITE_ERL_SYNC_SITE_ROOT_NOT_MATERIALIZED")
        self.assertEqual(result["owning_existing_goal"], "StegVerse-Labs/StegVerse-Healer#39")
        with mock.patch.dict(os.environ, {**CLEAN_ENV, "GH_TOKEN": "x"}):
            result = site_erl_sync.execute_site_erl_sync({}, {}, {})
        self.assert_six_fields(result)
        self.assertEqual(result["failed_predicate"], "site_erl_sync_forbidden_credential_env_absent")


class TestRelay(DispositionAssertions):
    def test_blocked_relay_state_carries_the_six_fields_when_run_as_a_script(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state = Path(td) / "relay.json"
            env = {"PATH": os.environ.get("PATH", ""), "STEGVERSE_REPO_ROOTS_JSON": "{}", "HEALER_RELAY_STATE": str(state)}
            proc = subprocess.run([sys.executable, "app/relay_stegdeploy_publication.py"], cwd=ROOT, env=env,
                                  text=True, capture_output=True, check=False)
            self.assertEqual(proc.returncode, 3, proc.stderr)
            body = json.loads(state.read_text(encoding="utf-8"))
        self.assert_six_fields(body)
        self.assertEqual(body["failure_code"], "STEGDEPLOY_RELAY_BLOCKED:source_repository_not_materialized")


class TestPreCarrierAssist(DispositionAssertions):
    def test_failed_and_blocked_paths_carry_the_six_fields(self) -> None:
        with mock.patch.dict(os.environ, {**CLEAN_ENV, "GH_TOKEN": "x"}):
            self.assert_six_fields(pre_carrier_assist.inspect_pre_carrier())
        with mock.patch.dict(os.environ, {**CLEAN_ENV, "STEGVERSE_REPO_ROOTS_JSON": "{}"}):
            result = pre_carrier_assist.inspect_pre_carrier()
        self.assert_six_fields(result)
        self.assertEqual(result["owning_existing_goal"], "HEALER-G18-PRE-CARRIER-ASSIST-001")
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.dict(os.environ, {**CLEAN_ENV, "STEGVERSE_REPO_ROOTS_JSON": json.dumps({"StegVerse-Labs/.github": td})}):
            result = pre_carrier_assist.inspect_pre_carrier()
        self.assert_six_fields(result)
        self.assertEqual(result["failure_code"], "REQUIRED_LOCAL_SOURCE_MISSING")


class TestEce(DispositionAssertions):
    def test_ece_blocked_paths_carry_the_six_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            result = execute_periodic_ece({}, Path(td))
            self.assert_six_fields(result)
            self.assertEqual(result["owning_existing_goal"], "ECOSYSTEM-CONTINUITY-EVALUATOR-001")
            result = run_ece_periodic_evaluation.bind_site_materialization({"state": "COMPLETE"}, {}, Path(td))
            self.assert_six_fields(result)
            self.assertEqual(result["failure_code"], "ECE_CYCLE_RECEIPT_MISSING_BEFORE_SITE_MATERIALIZATION")
        with mock.patch.dict(os.environ, {"STEGVERSE_REPO_ROOTS_JSON": "", "STEGVERSE_HEARTBEAT_ROOT": ""}), \
                mock.patch("builtins.print") as printed:
            self.assertEqual(run_ece_periodic_evaluation.main(), 3)
        self.assert_six_fields(json.loads(printed.call_args[0][0]))

    def test_unobserved_publication_is_recorded_not_awaited(self) -> None:
        source = (APP / "run_ece_periodic_evaluation.py").read_text(encoding="utf-8")
        self.assertIn("unobserved_consequence(RETRY_ENTRYPOINT)", source)
        self.assertNotIn("time.sleep", source)


class TestAuditAndCost(DispositionAssertions):
    def test_quiet_enforcer_repository_block_carries_the_six_fields(self) -> None:
        self.assert_six_fields(audit_schedules.audit_repo("StegVerse-Labs/Example", None))

    def test_cost_analyzer_block_carries_the_six_fields(self) -> None:
        report = actions_cost_reducer.build_report([Path("/nonexistent/repo-root")], {})
        self.assert_six_fields(report)
        self.assertEqual(report["failure_code"], "REPOSITORY_ROOTS_MISSING")


class TestReusableTaskCarrier(DispositionAssertions):
    def test_carrier_block_dispositions(self) -> None:
        fields = reusable_task_scheduler._carrier_block_disposition(
            {"state": "BOUNDARY_RECORDED", "boundary": "LOCAL_DOTGITHUB_SOURCE_NOT_MATERIALIZED"}, {})
        self.assert_six_fields({"state": "BLOCKED", **fields})
        unobserved = reusable_task_scheduler._carrier_block_disposition({"state": "BOUNDARY_RECORDED"}, {})
        self.assert_six_fields({"state": "BLOCKED", **unobserved})
        self.assertEqual(unobserved["consequence_observation"], NOT_AUTHENTICALLY_OBSERVED)
        self.assertTrue(unobserved["reconciliation_entrypoint"])
        root = reusable_task_scheduler._carrier_block_disposition({"state": "DELEGATED"}, {"state": "RESIDENT_CUSTODY_ROOT_INVALID"})
        self.assertEqual(root["owning_existing_goal"], reusable_task_scheduler.ROOT_OBSERVATION_TASK_ID)


class TestProducerLiterals(unittest.TestCase):
    """AST scan: a dict literal with a constant non-ALLOW state spreads or names the six fields."""

    def test_non_allow_dict_literals_carry_disposition(self) -> None:
        offenders = []
        scanned = 0
        for path in sorted(APP.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            wrapped: set[int] = set()
            for func in ast.walk(tree):
                # Every record _execute_target_handler returns passes through _with_disposition.
                if isinstance(func, ast.FunctionDef) and func.name == "_execute_target_handler":
                    wrapped.update(id(node) for node in ast.walk(func))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Dict) or id(node) in wrapped:
                    continue
                keys = {key.value: value for key, value in zip(node.keys, node.values) if isinstance(key, ast.Constant)}
                state = keys.get("state")
                if not (isinstance(state, ast.Constant) and state.value in {"BLOCKED", "FAILED", "FAIL_CLOSED", "DENY"}):
                    continue
                scanned += 1
                spreads_disposition = any(
                    key is None and ("non_allow" in ast.dump(value) or "disposition" in ast.dump(value))
                    for key, value in zip(node.keys, node.values)
                )
                if not spreads_disposition and "failure_code" not in keys:
                    offenders.append(f"{path.name}:{node.lineno}")
        self.assertGreater(scanned, 20)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
