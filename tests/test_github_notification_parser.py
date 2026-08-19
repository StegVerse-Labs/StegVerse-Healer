from __future__ import annotations

import unittest

from failure_mailbox.github_notification_parser import parse_github_failure_message


class GithubNotificationParserTests(unittest.TestCase):
    def test_no_jobs_run_notification(self) -> None:
        message = {
            "id": "m-nojobs",
            "thread_id": "t-nojobs",
            "email_ts": "2026-07-08T01:57:38-07:00",
            "subject": "[StegVerse-Labs/StegVerse-SCW] Run failed: .github/workflows/retrofit-setup-common-python.yml - repair-repo-alignment-check-v2 (86971ef)",
            "snippet": "workflow run: No jobs were run",
            "body": "[View workflow run](https://github.com/StegVerse-Labs/StegVerse-SCW/actions/runs/28930420419)\nNo jobs were run",
        }
        obs = parse_github_failure_message(message)
        self.assertEqual(obs["repository"], "StegVerse-Labs/StegVerse-SCW")
        self.assertEqual(obs["workflow"], ".github/workflows/retrofit-setup-common-python.yml")
        self.assertEqual(obs["branch"], "repair-repo-alignment-check-v2")
        self.assertEqual(obs["commit_sha"], "86971ef")
        self.assertEqual(obs["run_id"], "28930420419")
        self.assertEqual(obs["notification_result_class"], "NO_JOBS_RUN")
        self.assertEqual(obs["failure_class"], "NO_JOBS_RUN")
        self.assertFalse(obs["authority_effect"])
        self.assertFalse(obs["heartbeat_effect"])

    def test_generic_job_failure_does_not_become_semantic_family(self) -> None:
        message = {
            "id": "m-jobfail",
            "email_ts": "2026-08-18T20:26:20-07:00",
            "subject": "[StegVerse-Labs/StegVerse-Healer] Run failed: Test Readiness - main (e7aa69d)",
            "snippet": "Test Readiness: All jobs have failed",
            "body": "Test Readiness: All jobs have failed\nhttps://github.com/StegVerse-Labs/StegVerse-Healer/actions/runs/32212113694",
        }
        obs = parse_github_failure_message(message)
        self.assertEqual(obs["notification_result_class"], "WORKFLOW_JOB_FAILURE")
        self.assertNotIn("failure_class", obs)

    def test_budget_75_90_100_become_account_level_capacity_incidents(self) -> None:
        cases = [
            (75, "ACTIONS_BUDGET_APPROACHING", "OPERATIONAL_CAPACITY_WARNING"),
            (90, "ACTIONS_BUDGET_HIGH", "OPERATIONAL_CAPACITY_HIGH"),
            (100, "ACTIONS_BUDGET_EXHAUSTED", "OPERATIONAL_CAPACITY_EXHAUSTED"),
        ]
        for percent, failure_class, result_class in cases:
            with self.subTest(percent=percent):
                obs = parse_github_failure_message({
                    "id": f"budget-{percent}",
                    "email_ts": "2026-08-19T13:27:23-07:00",
                    "subject": f"[GitHub] You've hit {percent}% of your budget for the StegVerse-Labs account",
                    "snippet": f"You've used {percent}% of your Actions budget",
                })
                self.assertEqual(obs["repository"], "github-account:StegVerse-Labs")
                self.assertEqual(obs["workflow"], "GitHub Actions budget")
                self.assertEqual(obs["failure_class"], failure_class)
                self.assertEqual(obs["notification_result_class"], result_class)
                self.assertEqual(obs["threshold_percent"], percent)

    def test_included_minutes_90_and_100_become_account_level_capacity_incidents(self) -> None:
        ninety = parse_github_failure_message({
            "id": "minutes-90",
            "email_ts": "2026-08-07T05:45:56-07:00",
            "subject": "[GitHub] You have used 90% of the Actions minutes included for the Admissible-Existence account",
            "snippet": "1,800 min used / 2,000 min included",
        })
        hundred = parse_github_failure_message({
            "id": "minutes-100",
            "email_ts": "2026-08-07T15:09:28-07:00",
            "subject": "[GitHub] You have used 100% of the Actions minutes included for the Admissible-Existence account",
            "snippet": "2,000 min used / 2,000 min included",
        })
        self.assertEqual(ninety["failure_class"], "ACTIONS_INCLUDED_MINUTES_WARNING")
        self.assertEqual(ninety["notification_result_class"], "OPERATIONAL_CAPACITY_HIGH")
        self.assertEqual(hundred["failure_class"], "ACTIONS_INCLUDED_MINUTES_EXHAUSTED")
        self.assertEqual(hundred["notification_result_class"], "OPERATIONAL_CAPACITY_EXHAUSTED")
        self.assertEqual(hundred["repository"], "github-account:Admissible-Existence")

    def test_tvc_capacity_class_mismatch_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            parse_github_failure_message({
                "id": "budget-mismatch",
                "email_ts": "2026-08-19T13:27:23-07:00",
                "subject": "[GitHub] You've hit 100% of your budget for the StegVerse-Labs account",
                "signal_class": "ACTIONS_BUDGET_HIGH",
            })

    def test_continuation_workflow_gets_semantic_family(self) -> None:
        message = {
            "id": "m-cont",
            "email_ts": "2026-07-08T02:00:10-07:00",
            "subject": "[StegVerse-Labs/admissibility-wiki] Run failed: Validate chain continuation - main (1088baf)",
            "snippet": "Validate chain continuation: Some jobs were not successful",
            "body": "Validate chain continuation: Some jobs were not successful",
        }
        obs = parse_github_failure_message(message)
        self.assertEqual(obs["notification_result_class"], "WORKFLOW_JOB_FAILURE")
        self.assertEqual(obs["failure_class"], "CONTINUITY_FAILURE")

    def test_pr_failure_preserves_pr_context_without_inventing_semantic_family(self) -> None:
        message = {
            "id": "m-pr",
            "email_ts": "2026-07-08T09:10:43-07:00",
            "subject": "[StegVerse-Labs/Site] PR run failed: Site Bootstrap Validate - NOT READY FOR REVIEW: Fix governance observatory public path semantics (8c6edb4)",
            "snippet": "All jobs have failed",
            "body": "Site Bootstrap Validate: All jobs have failed",
        }
        obs = parse_github_failure_message(message)
        self.assertEqual(obs["branch"], "")
        self.assertEqual(obs["pr"], "NOT READY FOR REVIEW: Fix governance observatory public path semantics")
        self.assertEqual(obs["notification_result_class"], "WORKFLOW_JOB_FAILURE")
        self.assertNotIn("failure_class", obs)

    def test_rejects_non_operational_subject(self) -> None:
        with self.assertRaises(ValueError):
            parse_github_failure_message({"id": "m", "email_ts": "2026-01-01T00:00:00Z", "subject": "hello"})


if __name__ == "__main__":
    unittest.main()
