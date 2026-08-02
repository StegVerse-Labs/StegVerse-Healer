from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com"
ALLOWED_SCHEDULER_REPO = "StegVerse-Labs/StegVerse-Healer"
VALID_STATES = {"COMPLETE", "BLOCKED", "RETRY", "REVIEW_REQUIRED", "FAILED"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def headers(token: str, accept: str = "application/vnd.github+json") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "User-Agent": "StegVerse-Healer-Quiet-Enforcer",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_json(url: str, token: str) -> Any:
    request = urllib.request.Request(url, headers=headers(token))
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_raw(url: str, token: str) -> str:
    request = urllib.request.Request(url, headers=headers(token, "application/vnd.github.raw"))
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def has_schedule_trigger(raw: str) -> bool:
    lines = raw.splitlines()
    for line in lines:
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


def audit_repo(repo: str, token: str) -> dict[str, Any]:
    encoded_repo = "/".join(urllib.parse.quote(part, safe="") for part in repo.split("/"))
    base = f"{API}/repos/{encoded_repo}/contents/.github/workflows"
    result: dict[str, Any] = {
        "repository": repo,
        "state": "COMPLETE",
        "workflow_count": 0,
        "violations": [],
        "errors": [],
        "workflows": [],
    }

    try:
        items = get_json(base, token)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        result["state"] = "BLOCKED" if exc.code in (401, 403, 404) else "RETRY"
        result["errors"].append(f"workflow_inventory_http_{exc.code}:{detail[:300]}")
        return result
    except Exception as exc:
        result["state"] = "RETRY"
        result["errors"].append(f"workflow_inventory_error:{exc}")
        return result

    if not isinstance(items, list):
        result["state"] = "FAILED"
        result["errors"].append("workflow_inventory_not_a_list")
        return result

    for item in items:
        name = str(item.get("name", ""))
        if not (name.endswith(".yml") or name.endswith(".yaml")):
            continue
        result["workflow_count"] += 1
        raw_url = f"{base}/{urllib.parse.quote(name, safe='')}"
        try:
            raw = get_raw(raw_url, token)
        except urllib.error.HTTPError as exc:
            result["state"] = "BLOCKED" if exc.code in (401, 403, 404) else "RETRY"
            result["errors"].append(f"{name}:http_{exc.code}")
            continue
        except Exception as exc:
            result["state"] = "RETRY"
            result["errors"].append(f"{name}:{exc}")
            continue

        scheduled = has_schedule_trigger(raw)
        workflow_record = {
            "path": f".github/workflows/{name}",
            "sha256": sha256_text(raw),
            "schedule_present": scheduled,
        }
        result["workflows"].append(workflow_record)
        if scheduled and repo != ALLOWED_SCHEDULER_REPO:
            result["violations"].append(workflow_record["path"])

    if result["errors"] and result["state"] == "COMPLETE":
        result["state"] = "REVIEW_REQUIRED"
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
    token = os.environ.get("HEALER_GH_TOKEN", "").strip()
    if not token:
        print("Missing HEALER_GH_TOKEN", file=sys.stderr)
        return 2

    targets_path = Path(os.environ.get("TARGETS_FILE", "data/orchestrator_targets.json"))
    output_path = Path(os.environ.get("QUIET_RECEIPT", "data/summary/quiet_enforcer_latest.json"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        targets = load_targets(targets_path)
    except Exception as exc:
        print(f"Invalid target configuration: {exc}", file=sys.stderr)
        return 2

    repos = sorted({str(target.get("repo", "")).strip() for target in targets if target.get("repo")})
    repositories = [audit_repo(repo, token) for repo in repos]

    violations = sum(len(repo["violations"]) for repo in repositories)
    blocked = sum(repo["state"] == "BLOCKED" for repo in repositories)
    retry = sum(repo["state"] == "RETRY" for repo in repositories)
    review = sum(repo["state"] == "REVIEW_REQUIRED" for repo in repositories)
    failed = sum(repo["state"] == "FAILED" for repo in repositories)

    if failed or violations:
        state = "FAILED"
        next_task = "Remove or centrally migrate every unauthorized schedule listed in repositories[].violations."
    elif blocked:
        state = "BLOCKED"
        next_task = "Restore HEALER_GH_TOKEN repository access and Contents read permission for blocked repositories."
    elif retry:
        state = "RETRY"
        next_task = "Retry the audit after transient GitHub API failures clear."
    elif review:
        state = "REVIEW_REQUIRED"
        next_task = "Review partial workflow-read errors before claiming zero violations."
    else:
        state = "COMPLETE"
        next_task = "Retain central scheduling authority and continue auditing configured repositories."

    receipt: dict[str, Any] = {
        "schema": "stegverse.healer.quiet-enforcer-receipt.v1",
        "state": state,
        "manager": ALLOWED_SCHEDULER_REPO,
        "allowed_scheduler_repository": ALLOWED_SCHEDULER_REPO,
        "observed_at": utc_now(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "repositories": repositories,
        "summary": {
            "repository_count": len(repositories),
            "violation_count": violations,
            "blocked_count": blocked,
            "retry_count": retry,
            "review_required_count": review,
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

    if previous and stable_projection(previous) == stable_projection(receipt):
        receipt["observed_at"] = previous.get("observed_at", receipt["observed_at"])
        receipt["github_run_id"] = previous.get("github_run_id")
        receipt["github_run_attempt"] = previous.get("github_run_attempt")

    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if state == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
