import json
import tempfile
import unittest
from pathlib import Path

from app.actions_cost_reducer import (
    analyze_workflow,
    build_report,
    enforce,
    estimate_cron_starts_per_day,
)


POLICY = {
    "schema": "stegverse.github-actions-cost-policy.v1",
    "policy": {
        "scheduled_workflow_monthly_start_review_threshold": 120,
        "scheduled_workflow_monthly_start_enforce_threshold": 744,
        "matrix_fanout_review_threshold": 4,
        "require_concurrency_for_push_or_pull_request": True,
        "require_cancel_in_progress_when_concurrency_present": True,
        "review_unfiltered_push": True,
        "review_unfiltered_pull_request": True,
        "review_artifact_custody_for_validation": True,
        "prefer_existing_healer_scheduler_for_recurring_non_authoritative_work": True,
    },
}


def write_workflow(root: Path, name: str, body: str) -> Path:
    path = root / ".github" / "workflows" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class ActionsCostReducerTests(unittest.TestCase):
    def test_cron_estimator_common_forms(self):
        self.assertEqual(estimate_cron_starts_per_day("23 * * * *"), 24.0)
        self.assertEqual(estimate_cron_starts_per_day("0 */6 * * *"), 4.0)
        self.assertEqual(estimate_cron_starts_per_day("0 6 * * *"), 1.0)
        self.assertEqual(round(estimate_cron_starts_per_day("0 6 * * 1"), 6), round(1 / 7, 6))

    def test_hourly_workflow_is_ranked_for_healer_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Site"
            workflow = write_workflow(
                root,
                "hourly.yml",
                """name: Hourly\non:\n  schedule:\n    - cron: '23 * * * *'\n  workflow_dispatch: {}\njobs:\n  verify:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n""",
            )
            finding = analyze_workflow(root, workflow, POLICY)
            self.assertTrue(finding.scheduled)
            self.assertEqual(finding.estimated_scheduled_starts_per_month, 744.0)
            self.assertIn("HIGH_SCHEDULED_START_PRESSURE", finding.review_reasons)
            self.assertEqual(finding.recommendation, "REVIEW_FOR_EXISTING_HEALER_SCHEDULER_MIGRATION")

    def test_path_filtered_concurrent_validation_avoids_broad_trigger_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Repo"
            workflow = write_workflow(
                root,
                "validate.yml",
                """name: Validate\non:\n  push:\n    paths:\n      - 'src/**'\n  pull_request:\n    paths:\n      - 'src/**'\nconcurrency:\n  group: validate-${{ github.ref }}\n  cancel-in-progress: true\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: python -m pytest\n""",
            )
            finding = analyze_workflow(root, workflow, POLICY)
            self.assertTrue(finding.push_path_filtered)
            self.assertTrue(finding.pull_request_path_filtered)
            self.assertTrue(finding.has_concurrency)
            self.assertTrue(finding.cancel_in_progress)
            self.assertNotIn("UNFILTERED_PUSH", finding.review_reasons)
            self.assertNotIn("UNFILTERED_PULL_REQUEST", finding.review_reasons)
            self.assertNotIn("MISSING_CONCURRENCY", finding.review_reasons)

    def test_matrix_and_artifact_pressure_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Repo"
            workflow = write_workflow(
                root,
                "matrix.yml",
                """name: Matrix\non:\n  push: {}\njobs:\n  test:\n    strategy:\n      matrix:\n        python: [3.10, 3.11]\n        os: [ubuntu, windows]\n    runs-on: ${{ matrix.os }}\n    steps:\n      - uses: actions/upload-artifact@v4\n""",
            )
            finding = analyze_workflow(root, workflow, POLICY)
            self.assertEqual(finding.matrix_fanout, 4)
            self.assertTrue(finding.artifact_custody)
            self.assertIn("MATRIX_FANOUT", finding.review_reasons)
            self.assertIn("ARTIFACT_CUSTODY", finding.review_reasons)
            self.assertIn("UNFILTERED_PUSH", finding.review_reasons)

    def test_manual_only_diagnostic_is_low_recurring_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Repo"
            workflow = write_workflow(
                root,
                "manual.yml",
                """name: Manual\non:\n  workflow_dispatch: {}\njobs:\n  inspect:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ok\n""",
            )
            finding = analyze_workflow(root, workflow, POLICY)
            self.assertEqual(finding.estimated_scheduled_starts_per_month, 0)
            self.assertEqual(finding.recommendation, "KEEP_MANUAL_DIAGNOSTIC")

    def test_report_ranks_hourly_before_manual_and_enforcement_fails_hourly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Repo"
            write_workflow(root, "hourly.yml", """name: Hourly\non:\n  schedule:\n    - cron: '0 * * * *'\njobs:\n  one:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo one\n""")
            write_workflow(root, "manual.yml", """name: Manual\non:\n  workflow_dispatch: {}\njobs:\n  one:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo one\n""")
            report = build_report([root], POLICY)
            self.assertEqual(report["state"], "PASS")
            self.assertEqual(report["workflow_count"], 2)
            self.assertTrue(report["ranked_findings"][0]["workflow"].endswith("hourly.yml"))
            failures = enforce(report, POLICY)
            self.assertEqual(len(failures), 1)
            self.assertIn("hourly.yml", failures[0])

    def test_missing_root_blocks_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = build_report([Path(tmp) / "missing"], POLICY)
            self.assertEqual(report["state"], "BLOCKED")
            self.assertTrue(report["missing_repository_roots"])


if __name__ == "__main__":
    unittest.main()
