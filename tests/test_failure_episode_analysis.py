from __future__ import annotations

import unittest

from failure_mailbox.episode_analysis import build_failure_episodes, episode_summary


class FailureEpisodeAnalysisTests(unittest.TestCase):
    def test_same_commit_fanout_preserves_distinct_incidents(self) -> None:
        ledger = {
            "incidents": {
                "GF-000001": {
                    "incident_id": "GF-000001",
                    "repository": "StegVerse-Labs/StegVerse-SCW",
                    "workflow": ".github/workflows/a.yml",
                    "branch_or_pr": "repair-repo-alignment-check-v2",
                    "failure_class": "NO_JOBS_RUN",
                    "commits": ["86971ef"],
                    "observations": [
                        {"message_id": "m1", "commit_sha": "86971ef", "received_at": "2026-07-08T01:57:20-07:00"}
                    ],
                },
                "GF-000002": {
                    "incident_id": "GF-000002",
                    "repository": "StegVerse-Labs/StegVerse-SCW",
                    "workflow": ".github/workflows/b.yml",
                    "branch_or_pr": "repair-repo-alignment-check-v2",
                    "failure_class": "NO_JOBS_RUN",
                    "commits": ["86971ef"],
                    "observations": [
                        {"message_id": "m2", "commit_sha": "86971ef", "received_at": "2026-07-08T01:57:38-07:00"}
                    ],
                },
            }
        }
        episodes = build_failure_episodes(ledger)
        self.assertEqual(len(episodes), 1)
        episode = episodes[0]
        self.assertEqual(episode["incident_count"], 2)
        self.assertEqual(episode["workflow_count"], 2)
        self.assertEqual(episode["notification_count"], 2)
        self.assertEqual(episode["incident_ids"], ["GF-000001", "GF-000002"])
        self.assertTrue(episode["amplification_candidate"])
        self.assertFalse(episode["causality_claimed"])

    def test_different_failure_classes_do_not_merge(self) -> None:
        ledger = {
            "incidents": {
                "GF-1": {
                    "incident_id": "GF-1",
                    "repository": "Org/R",
                    "workflow": "one",
                    "branch_or_pr": "main",
                    "failure_class": "NO_JOBS_RUN",
                    "commits": ["abc1234"],
                    "observations": [{"message_id": "m1", "commit_sha": "abc1234", "received_at": "2026-01-01T00:00:00Z"}],
                },
                "GF-2": {
                    "incident_id": "GF-2",
                    "repository": "Org/R",
                    "workflow": "two",
                    "branch_or_pr": "main",
                    "failure_class": "WORKFLOW_JOB_FAILURE",
                    "commits": ["abc1234"],
                    "observations": [{"message_id": "m2", "commit_sha": "abc1234", "received_at": "2026-01-01T00:00:01Z"}],
                },
            }
        }
        episodes = build_failure_episodes(ledger)
        self.assertEqual(len(episodes), 2)
        self.assertEqual(episode_summary(episodes)["episode_count"], 2)


if __name__ == "__main__":
    unittest.main()
