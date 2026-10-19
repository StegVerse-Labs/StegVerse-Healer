"""Owning goal derivation: declared canonical_owner, exact registry record, or a six-field refusal."""
from __future__ import annotations

import hashlib
import json
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
# Byte-for-byte copy of the proposed record at StegVerse-Labs/.github#3257 head (see PROVENANCE.json there).
LABS_3257_ROOT = ROOT / "tests" / "fixtures" / "canonical_task_registry_3257"
LABS_3257_HEAD = "d11c9cfd7362bd19a9f5c076a1b562e813865a77"
OWNERSHIP_TASK = "HEALER-ORCHESTRATOR-TARGET-OWNERSHIP-001"
OWNERSHIP_RECORD = LABS_3257_ROOT / "data" / "canonical-task-records" / f"{OWNERSHIP_TASK}.json"
OWNERSHIP_RECORD_SHA256 = "19aaaa0ce14eb76dec27b9f56b0cd34132b602e3c5a2348d6542140a77d56b83"
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


def orchestrator_targets() -> list[dict]:
    return json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))["targets"]


class TestHealerOrchestratorTargetOwnershipRecord(unittest.TestCase):
    """The 12 undeclared Healer targets against the record proposed in StegVerse-Labs/.github#3257."""

    def setUp(self) -> None:
        targets = orchestrator_targets()
        self.undeclared = [t for t in targets if not str(t.get("canonical_owner") or "").strip()]
        self.declared = [t for t in targets if str(t.get("canonical_owner") or "").strip()]
        self.assertEqual((len(targets), len(self.undeclared), len(self.declared)), (17, 12, 5))

    def test_fixture_is_the_pinned_bytes_from_the_labs_pull_request_head(self) -> None:
        self.assertEqual(hashlib.sha256(OWNERSHIP_RECORD.read_bytes()).hexdigest(), OWNERSHIP_RECORD_SHA256)
        provenance = json.loads((LABS_3257_ROOT / "PROVENANCE.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["source_pull_request_head_sha"], LABS_3257_HEAD)
        self.assertEqual(provenance["fixture_sha256"], OWNERSHIP_RECORD_SHA256)
        self.assertEqual([r["task_id"] for r in owning_goal.load_registry_records(LABS_3257_ROOT)], [OWNERSHIP_TASK])

    def test_record_absent_the_undeclared_targets_refuse(self) -> None:
        # Labs main 978b888 has no record naming these targets; a materialized registry without it refuses.
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "data" / "canonical-task-records").mkdir(parents=True)
            records = owning_goal.load_registry_records(Path(td))
        self.assertEqual(records, [])
        for target in self.undeclared:
            goal, refusal = owning_goal.owning_goal_for_target(target, records)
            self.assertIsNone(goal, target)
            self.assertEqual(refusal["failure_code"], "TARGET_OWNING_GOAL_NOT_IN_REGISTRY", target)

    def test_pinned_record_owns_exactly_the_undeclared_targets(self) -> None:
        records = owning_goal.load_registry_records(LABS_3257_ROOT)
        for target in self.undeclared:
            self.assertEqual(owning_goal.registry_matches(target, records), [OWNERSHIP_TASK], target)
            blocked = {"state": "BLOCKED", "outcome": "LOCAL_REPOSITORY_NOT_MATERIALIZED"}
            result = sovereign_scheduler._with_disposition(target, blocked, records)
            self.assertEqual(result["owning_existing_goal"], OWNERSHIP_TASK, target)
            self.assertEqual(result["owning_existing_goal_source"], "CANONICAL_TASK_REGISTRY", target)
            self.assertNotIn("owning_goal_refusal", result)
            self.assertEqual(missing_disposition_fields(result), [])
        for target in self.declared:
            self.assertEqual(owning_goal.registry_matches(target, records), [], target)
            goal, refusal = owning_goal.owning_goal_for_target(target, records)
            self.assertEqual((goal, refusal), (target["canonical_owner"], None))
            result = sovereign_scheduler._with_disposition(
                target, {"state": "BLOCKED", "outcome": "LOCAL_REPOSITORY_NOT_MATERIALIZED"}, records)
            self.assertEqual(result["owning_existing_goal"], target["canonical_owner"])
            self.assertNotIn("owning_existing_goal_source", result)

    def test_each_target_matches_only_through_a_component_of_its_own_repository(self) -> None:
        # The record lists 6 repositories x 12 components; the 12 intended (repo, component) pairs are the
        # ones named by its per-target blockers. No current target reaches it through another repo's component.
        record = json.loads(OWNERSHIP_RECORD.read_text(encoding="utf-8"))
        intended = {tuple(b["failed_predicate"].split(":", 1)[1].rsplit(":", 1)) for b in record["blockers"]}
        self.assertEqual(len(intended), 12)
        components = set(record["targets"]["components"])
        for target in orchestrator_targets():
            hits = owning_goal._target_keys(target) & components
            if target["repo"] in record["targets"]["repositories"] and hits:
                self.assertLessEqual({(target["repo"], hit) for hit in hits}, intended, target)


if __name__ == "__main__":
    unittest.main()
