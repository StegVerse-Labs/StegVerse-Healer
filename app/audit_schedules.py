from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
        "next_executable_task": receipt["next_executable_task"],
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
        next_task = "Remove every repository-local schedule trigger and preserve cadence in the resident heartbeat/Healer target registry."
    elif blocked:
        state = "BLOCKED"
        next_task = "Materialize every managed repository on the sovereign carrier and rerun the local schedule audit."
    else:
        state = "COMPLETE"
        next_task = "Retain heartbeat-owned cadence and continue local schedule auditing."

    receipt: dict[str, Any] = {
        "schema": "stegverse.healer.quiet-enforcer-receipt.v2",
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
        },
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
