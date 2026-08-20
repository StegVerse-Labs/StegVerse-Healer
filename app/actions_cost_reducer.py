from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


CRON_RE = re.compile(r"cron\s*:\s*['\"]?([^'\"\n]+)")
JOB_RE = re.compile(r"^\s{2}([A-Za-z0-9_.-]+):\s*$")
MATRIX_INLINE_RE = re.compile(r"\[([^\]]+)\]")


@dataclass
class WorkflowFinding:
    repository: str
    workflow: str
    scheduled: bool
    cron: list[str]
    estimated_scheduled_starts_per_day: float
    estimated_scheduled_starts_per_month: float
    jobs: int
    matrix_fanout: int
    has_push: bool
    push_path_filtered: bool
    has_pull_request: bool
    pull_request_path_filtered: bool
    has_workflow_dispatch: bool
    has_concurrency: bool
    cancel_in_progress: bool
    artifact_custody: bool
    checkout_action: bool
    setup_python_action: bool
    review_reasons: list[str]
    remediation_priority: float
    recommendation: str


def _cron_field_values(field: str, minimum: int, maximum: int) -> int | None:
    field = field.strip()
    span = maximum - minimum + 1
    if field == "*":
        return span
    if field.startswith("*/"):
        try:
            step = int(field[2:])
        except ValueError:
            return None
        if step <= 0:
            return None
        return (span + step - 1) // step
    if "," in field:
        values = [part.strip() for part in field.split(",") if part.strip()]
        return len(values) if values else None
    if re.fullmatch(r"\d+", field):
        return 1
    return None


def estimate_cron_starts_per_day(expr: str) -> float:
    """Best-effort lower-complexity estimator for ordinary 5-field GitHub cron."""
    parts = expr.strip().split()
    if len(parts) != 5:
        return 0.0
    minute, hour, day_of_month, month, day_of_week = parts
    minute_count = _cron_field_values(minute, 0, 59)
    hour_count = _cron_field_values(hour, 0, 23)
    if minute_count is None or hour_count is None:
        return 0.0

    base = minute_count * hour_count
    # Monthly/day constraints reduce expected daily starts. We intentionally
    # avoid claiming precision for complex cron semantics.
    if day_of_month != "*":
        if re.fullmatch(r"\d+", day_of_month):
            base /= 30.0
        else:
            return 0.0
    if month != "*":
        month_count = _cron_field_values(month, 1, 12)
        if month_count is None:
            return 0.0
        base *= month_count / 12.0
    if day_of_week != "*":
        weekday_count = _cron_field_values(day_of_week, 0, 6)
        if weekday_count is None:
            return 0.0
        base *= weekday_count / 7.0
    return float(base)


def _section_has_paths(text: str, trigger: str) -> bool:
    lines = text.splitlines()
    trigger_re = re.compile(rf"^\s{{2}}{re.escape(trigger)}\s*:\s*(?:\{{\}})?\s*$")
    for index, line in enumerate(lines):
        if not trigger_re.match(line):
            continue
        base_indent = len(line) - len(line.lstrip())
        for child in lines[index + 1 :]:
            if not child.strip():
                continue
            indent = len(child) - len(child.lstrip())
            if indent <= base_indent:
                break
            stripped = child.strip()
            if stripped.startswith("paths:") or stripped.startswith("paths-ignore:"):
                return True
        return False
    return False


def _count_jobs(text: str) -> int:
    lines = text.splitlines()
    in_jobs = False
    count = 0
    for line in lines:
        if re.match(r"^jobs:\s*$", line):
            in_jobs = True
            continue
        if in_jobs and line and not line.startswith(" "):
            break
        if in_jobs and JOB_RE.match(line):
            count += 1
    return max(count, 1 if "runs-on:" in text else 0)


def _literal_matrix_fanout(text: str) -> int:
    lines = text.splitlines()
    in_matrix = False
    matrix_indent = None
    fanout = 1
    found_dimension = False
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped == "matrix:":
            in_matrix = True
            matrix_indent = indent
            continue
        if not in_matrix:
            continue
        if stripped and indent <= (matrix_indent or 0):
            in_matrix = False
            matrix_indent = None
            continue
        if ":" not in stripped:
            continue
        _, value = stripped.split(":", 1)
        match = MATRIX_INLINE_RE.search(value)
        if not match:
            continue
        entries = [item.strip() for item in match.group(1).split(",") if item.strip()]
        if entries:
            fanout *= len(entries)
            found_dimension = True
    return fanout if found_dimension else 1


def analyze_workflow(repo_root: Path, workflow_path: Path, policy: dict) -> WorkflowFinding:
    text = workflow_path.read_text(encoding="utf-8")
    cron = [match.group(1).strip() for match in CRON_RE.finditer(text)]
    starts_per_day = sum(estimate_cron_starts_per_day(expr) for expr in cron)
    starts_per_month = starts_per_day * 31.0
    has_push = bool(re.search(r"^\s{2}push\s*:", text, re.MULTILINE))
    has_pull_request = bool(re.search(r"^\s{2}pull_request\s*:", text, re.MULTILINE))
    has_dispatch = bool(re.search(r"^\s{2}workflow_dispatch\s*:", text, re.MULTILINE))
    has_concurrency = bool(re.search(r"^concurrency\s*:", text, re.MULTILINE))
    cancel_in_progress = "cancel-in-progress: true" in text.lower()
    artifact_custody = "actions/upload-artifact@" in text or "actions/download-artifact@" in text
    checkout_action = "actions/checkout@" in text
    setup_python_action = "actions/setup-python@" in text
    jobs = _count_jobs(text)
    fanout = _literal_matrix_fanout(text)

    reasons: list[str] = []
    p = policy["policy"]
    if starts_per_month >= p["scheduled_workflow_monthly_start_review_threshold"]:
        reasons.append("HIGH_SCHEDULED_START_PRESSURE")
    if has_push and p["review_unfiltered_push"] and not _section_has_paths(text, "push"):
        reasons.append("UNFILTERED_PUSH")
    if has_pull_request and p["review_unfiltered_pull_request"] and not _section_has_paths(text, "pull_request"):
        reasons.append("UNFILTERED_PULL_REQUEST")
    if (has_push or has_pull_request) and p["require_concurrency_for_push_or_pull_request"] and not has_concurrency:
        reasons.append("MISSING_CONCURRENCY")
    if has_concurrency and p["require_cancel_in_progress_when_concurrency_present"] and not cancel_in_progress:
        reasons.append("CONCURRENCY_WITHOUT_CANCEL")
    if fanout >= p["matrix_fanout_review_threshold"]:
        reasons.append("MATRIX_FANOUT")
    if artifact_custody and p["review_artifact_custody_for_validation"]:
        reasons.append("ARTIFACT_CUSTODY")

    # Weight recurring runner starts most heavily, then fanout and broad event triggers.
    priority = starts_per_month * max(jobs, 1) * max(fanout, 1)
    priority += 40.0 * max(fanout - 1, 0)
    priority += 25.0 * int(has_push and not _section_has_paths(text, "push"))
    priority += 25.0 * int(has_pull_request and not _section_has_paths(text, "pull_request"))
    priority += 15.0 * int((has_push or has_pull_request) and not has_concurrency)
    priority += 10.0 * int(artifact_custody)

    if cron and p["prefer_existing_healer_scheduler_for_recurring_non_authoritative_work"]:
        recommendation = "REVIEW_FOR_EXISTING_HEALER_SCHEDULER_MIGRATION"
    elif reasons:
        recommendation = "CONSOLIDATE_OR_FILTER_HOSTED_VALIDATION"
    elif has_dispatch and not (cron or has_push or has_pull_request):
        recommendation = "KEEP_MANUAL_DIAGNOSTIC"
    else:
        recommendation = "KEEP_REVIEWED_SURFACE"

    return WorkflowFinding(
        repository=repo_root.name,
        workflow=str(workflow_path.relative_to(repo_root)),
        scheduled=bool(cron),
        cron=cron,
        estimated_scheduled_starts_per_day=round(starts_per_day, 6),
        estimated_scheduled_starts_per_month=round(starts_per_month, 3),
        jobs=jobs,
        matrix_fanout=fanout,
        has_push=has_push,
        push_path_filtered=_section_has_paths(text, "push"),
        has_pull_request=has_pull_request,
        pull_request_path_filtered=_section_has_paths(text, "pull_request"),
        has_workflow_dispatch=has_dispatch,
        has_concurrency=has_concurrency,
        cancel_in_progress=cancel_in_progress,
        artifact_custody=artifact_custody,
        checkout_action=checkout_action,
        setup_python_action=setup_python_action,
        review_reasons=reasons,
        remediation_priority=round(priority, 3),
        recommendation=recommendation,
    )


def iter_workflows(repo_root: Path) -> Iterable[Path]:
    workflow_dir = repo_root / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return []
    return sorted([*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")])


def load_roots(cli_roots: list[str]) -> list[Path]:
    if cli_roots:
        return [Path(root).resolve() for root in cli_roots]
    raw = os.environ.get("STEGVERSE_REPO_ROOTS_JSON", "")
    if not raw:
        return []
    value = json.loads(raw)
    if isinstance(value, dict):
        return [Path(path).resolve() for path in value.values()]
    if isinstance(value, list):
        return [Path(path).resolve() for path in value]
    raise ValueError("STEGVERSE_REPO_ROOTS_JSON must be an object or list")


def build_report(roots: list[Path], policy: dict) -> dict:
    findings: list[WorkflowFinding] = []
    missing_roots: list[str] = []
    for root in roots:
        if not root.is_dir():
            missing_roots.append(str(root))
            continue
        for workflow in iter_workflows(root):
            findings.append(analyze_workflow(root, workflow, policy))
    findings.sort(key=lambda row: (-row.remediation_priority, row.repository, row.workflow))
    scheduled_monthly = sum(row.estimated_scheduled_starts_per_month * max(row.jobs, 1) * max(row.matrix_fanout, 1) for row in findings)
    report = {
        "schema": "stegverse.github-actions-cost-analysis.v1",
        "state": "PASS" if roots and not missing_roots else "BLOCKED",
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "network_required": False,
        "authority_effect": "NONE",
        "repository_roots_requested": len(roots),
        "missing_repository_roots": missing_roots,
        "workflow_count": len(findings),
        "scheduled_workflow_count": sum(1 for row in findings if row.scheduled),
        "review_candidate_count": sum(1 for row in findings if row.review_reasons),
        "estimated_scheduled_job_starts_per_month": round(scheduled_monthly, 3),
        "ranked_findings": [asdict(row) for row in findings],
    }
    return report


def enforce(report: dict, policy: dict) -> list[str]:
    failures: list[str] = []
    threshold = policy["policy"]["scheduled_workflow_monthly_start_enforce_threshold"]
    for row in report["ranked_findings"]:
        starts = row["estimated_scheduled_starts_per_month"] * max(row["jobs"], 1) * max(row["matrix_fanout"], 1)
        if starts >= threshold:
            failures.append(f"{row['repository']}:{row['workflow']}: scheduled starts {starts:.1f}/month >= {threshold}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic GitHub Actions cost-pressure analyzer")
    parser.add_argument("roots", nargs="*", help="Repository roots; defaults to STEGVERSE_REPO_ROOTS_JSON")
    parser.add_argument("--policy", default="data/actions_cost_policy.json")
    parser.add_argument("--output", default="actions-cost-analysis.report.json")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    roots = load_roots(args.roots)
    report = build_report(roots, policy)
    failures = enforce(report, policy) if args.enforce else []
    report["enforcement_failures"] = failures
    if failures:
        report["state"] = "FAIL_CLOSED"
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": report["state"],
        "workflow_count": report["workflow_count"],
        "scheduled_workflow_count": report["scheduled_workflow_count"],
        "review_candidate_count": report["review_candidate_count"],
        "estimated_scheduled_job_starts_per_month": report["estimated_scheduled_job_starts_per_month"],
        "output": args.output,
    }, sort_keys=True))
    return 1 if report["state"] in {"BLOCKED", "FAIL_CLOSED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
