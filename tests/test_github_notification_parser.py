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
        self.assertEqual(obs["workflow"], "Test Readiness")
        self.assertEqual(obs["branch"], "main")
        self.assertEqual(obs["run_id"], "32212113694")
        self.assertEqual(obs["notification_result_class"], "WORKFLOW_JOB_FAILURE")
        self.assertNotIn("failure_class", obs)

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

    def test_rejects_noncanonical_subject(self) -> None:
        with self.assertRaises(ValueError):
            parse_github_failure_message({"id": "m", "email_ts": "2026-01-01T00:00:00Z", "subject": "hello"})


if __name__ == "__main__":
    unittest.main()
