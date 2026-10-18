"""Owning goal derivation: declared canonical_owner, exact registry record, or a six-field refusal."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from app import owning_goal, sovereign_scheduler  # noqa: E402
from app.disposition import DISPOSITION_FIELDS, missing_disposition_fields  # noqa: E402

FIXTURE_LABS_ROOT = ROOT / "tests" / "fixtures" / "canonical_task_registry"
DEFAULT_GOAL = "LLMA-DECLARED-PATH-CONFORMANCE-368"
UPTIME = {"repo": "StegVerse-Labs/SCW", "workflow": "uptime.yml", "aliases": ["scw-uptime", "uptime"]}
SITE_RUNNER = {"repo": "StegVerse-Labs/Site", "workflow": "site-task-runner.yml", "aliases": ["site"]}
CONTINUITY = {"repo": "StegVerse-Labs/Continuity", "workflow": "continuity.yml", "aliases": ["continuity", "continuity-guardian"]}


def fixture_records() -> list[dict]:
    records = owning_goal.load_registry_records(FIXTURE_LABS_ROOT)
    assert records is not None
    return records


class TestOwningGoalForTarget(unittest.TestCase):
    def assert_refusal(self, refusal: dict, code: str) -> None:
        self.assertEqual(tuple(refusal), DISPOSITION_FIELDS)
        self.assertTrue(all(refusal.values()), refusal)
        self.assertEqual(refusal["failure_code"], code)
        self.assertEqual(refusal["failed_predicate"], "TARGET_OWNING_GOAL_DECLARED_OR_REGISTERED")
        self.assertEqual(refusal["owning_existing_goal"], DEFAULT_GOAL)

    def test_fixture_loads_registry_index_and_record_files_but_not_session_notes(self) -> None:
        ids = sorted(record["task_id"] for record in fixture_records())
        self.assertEqual(ids, ["FIXTURE-CONTINUITY-GUARDIAN-A-001", "FIXTURE-CONTINUITY-GUARDIAN-B-001",
                               "FIXTURE-SCW-UPTIME-OBSERVATION-001", "FIXTURE-SITE-PAPERS-001"])

    def test_declared_canonical_owner_wins_over_registry(self) -> None:
        goal, refusal = owning_goal.owning_goal_for_target({**UPTIME, "canonical_owner": "StegVerse-Labs/SCW#1"}, fixture_records())
        self.assertEqual((goal, refusal), ("StegVerse-Labs/SCW#1", None))
        goal, refusal = owning_goal.owning_goal_for_target({**UPTIME, "canonical_owner": "StegVerse-Labs/SCW#1"}, None)
        self.assertEqual((goal, refusal), ("StegVerse-Labs/SCW#1", None))

    def test_exact_registry_record_maps_the_target(self) -> None:
        goal, refusal = owning_goal.owning_goal_for_target(UPTIME, fixture_records())
        self.assertEqual((goal, refusal), ("FIXTURE-SCW-UPTIME-OBSERVATION-001", None))

    def test_repository_overlap_alone_is_not_a_mapping(self) -> None:
        goal, refusal = owning_goal.owning_goal_for_target(SITE_RUNNER, fixture_records())
        self.assertIsNone(goal)
        self.assert_refusal(refusal, "TARGET_OWNING_GOAL_NOT_IN_REGISTRY")
        repair = refusal["required_evidence_or_repair"]
        self.assertIn("StegVerse-Labs/Site site-task-runner.yml", repair)
        self.assertIn("canonical_owner", repair)
        self.assertIn("data/orchestrator_targets.json", repair)
        self.assertIn("canonical task registry", repair)

    def test_component_in_another_repository_is_not_a_mapping(self) -> None:
        goal, refusal = owning_goal.owning_goal_for_target({**UPTIME, "repo": "StegVerse-Labs/Other"}, fixture_records())
        self.assertIsNone(goal)
        self.assert_refusal(refusal, "TARGET_OWNING_GOAL_NOT_IN_REGISTRY")

    def test_two_registered_owners_refuse_instead_of_picking_one(self) -> None:
        goal, refusal = owning_goal.owning_goal_for_target(CONTINUITY, fixture_records())
        self.assertIsNone(goal)
        self.assert_refusal(refusal, "TARGET_OWNING_GOAL_AMBIGUOUS_IN_REGISTRY")
        self.assertIn("FIXTURE-CONTINUITY-GUARDIAN-A-001", refusal["required_evidence_or_repair"])

    def test_absent_registry_refuses_with_its_own_code(self) -> None:
        goal, refusal = owning_goal.owning_goal_for_target(UPTIME, None)
        self.assertIsNone(goal)
        self.assert_refusal(refusal, "CANONICAL_TASK_REGISTRY_NOT_MATERIALIZED")
        self.assertIn("STEGVERSE_REPO_ROOTS_JSON", refusal["required_evidence_or_repair"])
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(owning_goal.load_registry_records(Path(td)))  # root present, registry not in it
        self.assertIsNone(owning_goal.registry_records_from_roots({}))


class TestSchedulerDispositionUsesRegistry(unittest.TestCase):
    def test_registry_mapped_owner_reaches_the_non_allow_record(self) -> None:
        roots = {"StegVerse-Labs/.github": FIXTURE_LABS_ROOT}
        result = sovereign_scheduler._execute_target(UPTIME, roots, "{}")
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "LOCAL_REPOSITORY_NOT_MATERIALIZED")
        self.assertEqual(missing_disposition_fields(result), [])
        self.assertEqual(result["owning_existing_goal"], "FIXTURE-SCW-UPTIME-OBSERVATION-001")
        self.assertEqual(result["owning_existing_goal_source"], "CANONICAL_TASK_REGISTRY")
        self.assertNotIn("owning_goal_refusal", result)

    def test_unmapped_target_keeps_its_outcome_and_attaches_the_refusal(self) -> None:
        roots = {"StegVerse-Labs/.github": FIXTURE_LABS_ROOT}
        result = sovereign_scheduler._execute_target(SITE_RUNNER, roots, "{}")
        self.assertEqual((result["state"], result["outcome"], result["failure_code"]),
                         ("BLOCKED", "LOCAL_REPOSITORY_NOT_MATERIALIZED", "LOCAL_REPOSITORY_NOT_MATERIALIZED"))
        self.assertEqual(result["owning_existing_goal"], DEFAULT_GOAL)
        self.assertNotIn("owning_existing_goal_source", result)
        self.assertEqual(result["owning_goal_refusal"]["failure_code"], "TARGET_OWNING_GOAL_NOT_IN_REGISTRY")
        self.assertEqual(missing_disposition_fields(result["owning_goal_refusal"]), [])

    def test_allow_record_and_record_naming_its_owner_are_untouched(self) -> None:
        complete = {"state": "COMPLETE", "outcome": "X"}
        self.assertIs(sovereign_scheduler._with_disposition(SITE_RUNNER, complete, None), complete)
        named = {"state": "BLOCKED", "outcome": "X", "owning_existing_goal": "OWN"}
        result = sovereign_scheduler._with_disposition(SITE_RUNNER, named, None)
        self.assertEqual(result["owning_existing_goal"], "OWN")
        self.assertNotIn("owning_goal_refusal", result)


if __name__ == "__main__":
    unittest.main()
