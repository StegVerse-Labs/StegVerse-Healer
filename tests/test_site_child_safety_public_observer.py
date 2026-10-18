from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from app import sovereign_scheduler
from app.disposition import NOT_AUTHENTICALLY_OBSERVED, missing_disposition_fields

ROOT = Path(__file__).resolve().parents[1]


class TestSiteChildSafetyPublicObserver(unittest.TestCase):
    def target(self) -> dict:
        config = json.loads((ROOT / "data" / "orchestrator_targets.json").read_text(encoding="utf-8"))
        matches = [
            target for target in config["targets"]
            if target.get("repo") == "StegVerse-Labs/Site"
            and target.get("workflow") == "child-safety-public-deployment-observer"
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_target_is_hourly_and_uses_existing_scheduler(self):
        target = self.target()
        self.assertEqual(target["run_hours_utc"], list(range(24)))
        self.assertIn("child-safety-public-observer", target["aliases"])
        self.assertNotIn("token", json.dumps(target).lower().replace("no-github-token", ""))

    def test_missing_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            site.mkdir()
            roots = {"StegVerse-Labs/Site": site}
            result = sovereign_scheduler._execute_target(
                {"repo": "StegVerse-Labs/Site", "workflow": "child-safety-public-deployment-observer"},
                roots,
                json.dumps({key: str(value) for key, value in roots.items()}),
            )
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["outcome"], "SITE_CHILD_SAFETY_OBSERVER_MISSING")

    def run_observer(self, body: str, run_side_effect=None) -> tuple[dict, mock.Mock]:
        with tempfile.TemporaryDirectory() as temp_dir:
            site = Path(temp_dir) / "Site"
            scripts = site / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "check_child_safety_public_deployment.py").write_text(
                "import json, os\nfrom pathlib import Path\np=Path(os.environ['STEGVERSE_CHILD_SAFETY_REPORT'])\n" + body,
                encoding="utf-8",
            )
            roots = {"StegVerse-Labs/Site": site}
            counting_run = mock.Mock(side_effect=run_side_effect or sovereign_scheduler._run)
            # Any wait, sleep or poll for public reachability on this path is a defect.
            with mock.patch.object(sovereign_scheduler, "_run", counting_run), \
                    mock.patch("time.sleep", side_effect=AssertionError("waited for reachability")):
                result = sovereign_scheduler._execute_target(
                    {"repo": "StegVerse-Labs/Site", "workflow": "child-safety-public-deployment-observer",
                     "aliases": ["site-child-safety"]},
                    roots,
                    json.dumps({key: str(value) for key, value in roots.items()}),
                )
            return result, counting_run

    def test_reachable_destination_completes_with_observation_recorded(self):
        result, run = self.run_observer(
            "p.write_text(json.dumps({'state':'VERIFIED_PUBLICLY_REACHABLE','url':'https://example.invalid/child-safety','http_status':200,'authority_effect':False,'github_token_required':False,'artifact_custody_required':False}))\n"
        )
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result["state"], "COMPLETE")
        self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_CHILD_SAFETY_PUBLIC_OBSERVATION")
        observation = result["reachability_observation"]
        self.assertEqual(observation["consequence_observation"], "OBSERVED")
        self.assertEqual(observation["state"], "VERIFIED_PUBLICLY_REACHABLE")
        self.assertEqual(observation["evidence"]["http_status"], 200)
        self.assertNotIn("receiver_unavailable_disposition", result)
        self.assertNotIn("failure_code", result)
        self.assertIs(result["receipt"]["authority_effect"], False)
        self.assertIs(result["receipt"]["github_token_required"], False)
        self.assertIs(result["receipt"]["artifact_custody_required"], False)

    def test_unreachable_destination_completes_without_waiting(self):
        result, run = self.run_observer(
            "p.write_text(json.dumps({'state':'BLOCKED','authority_effect':False,'github_token_required':False,'artifact_custody_required':False}))\n"
            "raise SystemExit(1)\n"
        )
        self.assertEqual(run.call_count, 1)  # one-shot: no retry or poll for reachability
        self.assertEqual(result["state"], "COMPLETE")
        self.assertEqual(result["outcome"], "SOVEREIGN_LOCAL_SITE_CHILD_SAFETY_PUBLIC_OBSERVATION")
        observation = result["reachability_observation"]
        self.assertEqual(observation["consequence_observation"], NOT_AUTHENTICALLY_OBSERVED)
        self.assertEqual(observation["reconciliation_entrypoint"], sovereign_scheduler.CHILD_SAFETY_RECONCILIATION_ENTRYPOINT)
        self.assertIn("scripts/check_child_safety_public_deployment.py", observation["reconciliation_entrypoint"])
        self.assertEqual(observation["observer_reported_state"], "BLOCKED")
        self.assertEqual(observation["observer_returncode"], 1)
        self.assertEqual(result["receiver_unavailable_disposition"], "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION")
        self.assertNotIn("failure_code", result)

    def test_failed_controlled_step_is_non_allow_with_six_fields(self):
        result, _ = self.run_observer("raise SystemExit('observer crashed before writing its report')\n")
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "SITE_CHILD_SAFETY_REPORT_NOT_MATERIALIZED")
        self.assertEqual(missing_disposition_fields(result), [])
        self.assertEqual(result["failure_code"], "SITE_CHILD_SAFETY_REPORT_NOT_MATERIALIZED")
        self.assertEqual(result["retry_entrypoint"], "RUN_SCOPE=site-child-safety DISPATCH_MODE=manual python -m app.sovereign_scheduler")

    def test_boundary_violation_is_non_allow_with_six_fields(self):
        result, _ = self.run_observer(
            "p.write_text(json.dumps({'state':'VERIFIED_PUBLICLY_REACHABLE','authority_effect':True,'github_token_required':False,'artifact_custody_required':False}))\n"
        )
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "SITE_CHILD_SAFETY_REPORT_BOUNDARY_VIOLATED")
        self.assertEqual(missing_disposition_fields(result), [])

    def test_observer_timeout_is_non_allow_and_not_retried(self):
        def timeout(command, *args, **kwargs):
            raise subprocess.TimeoutExpired(command, 60)

        result, run = self.run_observer("", run_side_effect=timeout)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["outcome"], "SITE_CHILD_SAFETY_OBSERVER_TIMEOUT")
        self.assertEqual(missing_disposition_fields(result), [])
        self.assertEqual(result["receiver_unavailable_disposition"], "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION")
        self.assertEqual(result["reachability_observation"]["consequence_observation"], NOT_AUTHENTICALLY_OBSERVED)

    def test_handler_has_no_wait_for_reachability(self):
        source = (ROOT / "app" / "sovereign_scheduler.py").read_text(encoding="utf-8")
        self.assertNotIn("time.sleep", source)


if __name__ == "__main__":
    unittest.main()
