from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.actions_cost_reducer import build_report

VALID_STATES = {"COMPLETE", "BLOCKED", "RETRY", "REVIEW_REQUIRED", "FAILED"}
FORBIDDEN_CREDENTIALS = ("HEALER_GH_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "HEALER_PAT", "GH_STEGVERSE_AI_TOKEN")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def has_schedule_trigger(raw: str) -> bool:
    for line in raw.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if stripped == "schedule:" or stripped.startswith("schedule: "):
            return True
    return False


def load_targets(path: Path) -> list[dict[str, Any]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    targets = config.get("targets")
    if not isinstance(targets, list):
        raise ValueError("targets must be a list")
    return targets


def load_roots() -> dict[str, Path]:
    raw = os.getenv("STEGVERSE_REPO_ROOTS_JSON", "").strip()
    if not raw:
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON is required")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON must be an object")
    roots: dict[str, Path] = {}
    for repo, value in parsed.items():
        if isinstance(repo, str) and isinstance(value, str):
            path = Path(value).expanduser().resolve()
            if path.is_dir():
                roots[repo] = path
    return roots


def audit_repo(repo: str, root: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "repository": repo,
        "state": "COMPLETE",
        "workflow_count": 0,
        "violations": [],
        "errors": [],
        "workflows": [],
    }
    if root is None:
        result["state"] = "BLOCKED"
        result["errors"].append("local_repository_not_materialized")
        return result
    workflow_root = root / ".github" / "workflows"
    if not workflow_root.is_dir():
        return result
    for path in sorted(list(workflow_root.glob("*.yml")) + list(workflow_root.glob("*.yaml"))):
        raw = path.read_text(encoding="utf-8", errors="replace")
        scheduled = has_schedule_trigger(raw)
        rel = str(path.relative_to(root))
        record = {"path": rel, "sha256": sha256_text(raw), "schedule_present": scheduled}
        result["workflow_count"] += 1
        result["workflows"].append(record)
        if scheduled:
            result["violations"].append(rel)
    if result["violations"]:
        result["state"] = "FAILED"
    return result


def stable_projection(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": receipt["schema"],
        "state": receipt["state"],
        "manager": receipt["manager"],
        "allowed_scheduler_repository": receipt["allowed_scheduler_repository"],
        "repositories": receipt["repositories"],
        "summary": receipt["summary"],
        "cost_analysis": receipt.get("cost_analysis"),
        "next_executable_task": receipt["next_executable_task"],
    }


def load_cost_policy() -> dict[str, Any]:
    policy_path = Path(os.environ.get("ACTIONS_COST_POLICY", "data/actions_cost_policy.json"))
    value = json.loads(policy_path.read_text(encoding="utf-8"))
    if value.get("schema") != "stegverse.github-actions-cost-policy.v1":
        raise ValueError("invalid Actions cost policy schema")
    return value


def compact_cost_analysis(report: dict[str, Any]) -> dict[str, Any]:
    ranked = report.get("ranked_findings", [])
    top = []
    for row in ranked[:20]:
        top.append({
            "repository": row.get("repository"),
            "workflow": row.get("workflow"),
            "estimated_scheduled_starts_per_month": row.get("estimated_scheduled_starts_per_month"),
            "jobs": row.get("jobs"),
            "matrix_fanout": row.get("matrix_fanout"),
            "review_reasons": row.get("review_reasons"),
            "remediation_priority": row.get("remediation_priority"),
            "recommendation": row.get("recommendation"),
        })
    return {
        "schema": report.get("schema"),
        "state": report.get("state"),
        "credential_authority": report.get("credential_authority"),
        "github_token_required": report.get("github_token_required"),
        "network_required": report.get("network_required"),
        "authority_effect": report.get("authority_effect"),
        "workflow_count": report.get("workflow_count"),
        "scheduled_workflow_count": report.get("scheduled_workflow_count"),
        "review_candidate_count": report.get("review_candidate_count"),
        "estimated_scheduled_job_starts_per_month": report.get("estimated_scheduled_job_starts_per_month"),
        "top_remediation_candidates": top,
    }


def main() -> int:
    present = [name for name in FORBIDDEN_CREDENTIALS if os.getenv(name)]
    if present:
        print("Forbidden GitHub credential environment: " + ",".join(sorted(present)), file=sys.stderr)
        return 2

    targets_path = Path(os.environ.get("TARGETS_FILE", "data/orchestrator_targets.json"))
    output_path = Path(os.environ.get("QUIET_RECEIPT", "data/summary/quiet_enforcer_latest.json"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        targets = load_targets(targets_path)
        roots = load_roots()
        cost_policy = load_cost_policy()
        cost_report = build_report(list(roots.values()), cost_policy)
    except Exception as exc:
        print(f"Invalid sovereign audit configuration: {exc}", file=sys.stderr)
        return 2

    repos = sorted({str(target.get("repo", "")).strip() for target in targets if target.get("repo")})
    repositories = [audit_repo(repo, roots.get(repo)) for repo in repos]
    violations = sum(len(repo["violations"]) for repo in repositories)
    blocked = sum(repo["state"] == "BLOCKED" for repo in repositories)
    failed = sum(repo["state"] == "FAILED" for repo in repositories)

    if failed or violations:
        state = "FAILED"
        next_task = "Remove every repository-local schedule trigger, preserve cadence in the resident heartbeat/Healer target registry, and consume the ranked cost-analysis candidates in descending priority."
    elif blocked:
        state = "BLOCKED"
        next_task = "Materialize every managed repository on the sovereign carrier and rerun the local schedule and cost-pressure audit."
    else:
        state = "COMPLETE"
        next_task = "Retain heartbeat-owned cadence and migrate the highest-value non-colliding cost-analysis candidate without capability loss."

    receipt: dict[str, Any] = {
        "schema": "stegverse.healer.quiet-enforcer-receipt.v3",
        "state": state,
        "manager": "single_stegverse_heartbeat",
        "allowed_scheduler_repository": None,
        "observed_at": utc_now(),
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "github_actions_production_role": False,
        "repositories": repositories,
        "summary": {
            "repository_count": len(repositories),
            "violation_count": violations,
            "blocked_count": blocked,
            "retry_count": 0,
            "review_required_count": 0,
            "failed_count": failed,
            "cost_review_candidate_count": cost_report.get("review_candidate_count", 0),
            "estimated_scheduled_job_starts_per_month": cost_report.get("estimated_scheduled_job_starts_per_month", 0),
        },
        "cost_analysis": compact_cost_analysis(cost_report),
        "next_executable_task": next_task,
    }
    if receipt["state"] not in VALID_STATES:
        raise RuntimeError(f"invalid state {receipt['state']}")

    previous: dict[str, Any] | None = None
    if output_path.exists():
        try:
            previous = json.loads(output_path.read_text(encoding="utf-8"))
        except Exception:
            previous = None
    if previous:
        try:
            if stable_projection(previous) == stable_projection(receipt):
                receipt["observed_at"] = previous.get("observed_at", receipt["observed_at"])
        except Exception:
            pass

    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if state == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
