import json
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


def test_cron_estimator_common_forms():
    assert estimate_cron_starts_per_day("23 * * * *") == 24.0
    assert estimate_cron_starts_per_day("0 */6 * * *") == 4.0
    assert estimate_cron_starts_per_day("0 6 * * *") == 1.0
    assert round(estimate_cron_starts_per_day("0 6 * * 1"), 6) == round(1 / 7, 6)


def test_hourly_workflow_is_ranked_for_healer_migration(tmp_path):
    root = tmp_path / "Site"
    workflow = write_workflow(
        root,
        "hourly.yml",
        """name: Hourly\non:\n  schedule:\n    - cron: '23 * * * *'\n  workflow_dispatch: {}\njobs:\n  verify:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n""",
    )
    finding = analyze_workflow(root, workflow, POLICY)
    assert finding.scheduled is True
    assert finding.estimated_scheduled_starts_per_month == 744.0
    assert "HIGH_SCHEDULED_START_PRESSURE" in finding.review_reasons
    assert finding.recommendation == "REVIEW_FOR_EXISTING_HEALER_SCHEDULER_MIGRATION"


def test_path_filtered_concurrent_validation_avoids_broad_trigger_findings(tmp_path):
    root = tmp_path / "Repo"
    workflow = write_workflow(
        root,
        "validate.yml",
        """name: Validate\non:\n  push:\n    paths:\n      - 'src/**'\n  pull_request:\n    paths:\n      - 'src/**'\nconcurrency:\n  group: validate-${{ github.ref }}\n  cancel-in-progress: true\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: python -m pytest\n""",
    )
    finding = analyze_workflow(root, workflow, POLICY)
    assert finding.push_path_filtered is True
    assert finding.pull_request_path_filtered is True
    assert finding.has_concurrency is True
    assert finding.cancel_in_progress is True
    assert "UNFILTERED_PUSH" not in finding.review_reasons
    assert "UNFILTERED_PULL_REQUEST" not in finding.review_reasons
    assert "MISSING_CONCURRENCY" not in finding.review_reasons


def test_matrix_and_artifact_pressure_are_detected(tmp_path):
    root = tmp_path / "Repo"
    workflow = write_workflow(
        root,
        "matrix.yml",
        """name: Matrix\non:\n  push: {}\njobs:\n  test:\n    strategy:\n      matrix:\n        python: [3.10, 3.11]\n        os: [ubuntu, windows]\n    runs-on: ${{ matrix.os }}\n    steps:\n      - uses: actions/upload-artifact@v4\n""",
    )
    finding = analyze_workflow(root, workflow, POLICY)
    assert finding.matrix_fanout == 4
    assert finding.artifact_custody is True
    assert "MATRIX_FANOUT" in finding.review_reasons
    assert "ARTIFACT_CUSTODY" in finding.review_reasons
    assert "UNFILTERED_PUSH" in finding.review_reasons


def test_manual_only_diagnostic_is_low_recurring_cost(tmp_path):
    root = tmp_path / "Repo"
    workflow = write_workflow(
        root,
        "manual.yml",
        """name: Manual\non:\n  workflow_dispatch: {}\njobs:\n  inspect:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ok\n""",
    )
    finding = analyze_workflow(root, workflow, POLICY)
    assert finding.estimated_scheduled_starts_per_month == 0
    assert finding.recommendation == "KEEP_MANUAL_DIAGNOSTIC"


def test_report_ranks_hourly_before_manual_and_enforcement_fails_hourly(tmp_path):
    root = tmp_path / "Repo"
    write_workflow(
        root,
        "hourly.yml",
        """name: Hourly\non:\n  schedule:\n    - cron: '0 * * * *'\njobs:\n  one:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo one\n""",
    )
    write_workflow(
        root,
        "manual.yml",
        """name: Manual\non:\n  workflow_dispatch: {}\njobs:\n  one:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo one\n""",
    )
    report = build_report([root], POLICY)
    assert report["state"] == "PASS"
    assert report["workflow_count"] == 2
    assert report["ranked_findings"][0]["workflow"].endswith("hourly.yml")
    failures = enforce(report, POLICY)
    assert len(failures) == 1
    assert "hourly.yml" in failures[0]


def test_missing_root_blocks_report(tmp_path):
    report = build_report([tmp_path / "missing"], POLICY)
    assert report["state"] == "BLOCKED"
    assert report["missing_repository_roots"]
