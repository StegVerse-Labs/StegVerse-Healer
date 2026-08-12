from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_CREDENTIALS = ("HEALER_GH_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "HEALER_PAT", "GH_STEGVERSE_AI_TOKEN")


def _forbid_github_credentials() -> None:
    present = [name for name in FORBIDDEN_CREDENTIALS if os.getenv(name)]
    if present:
        raise RuntimeError("FORBIDDEN_GITHUB_CREDENTIAL_ENV:" + ",".join(sorted(present)))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _repo_roots() -> dict[str, Path]:
    raw = os.getenv("STEGVERSE_REPO_ROOTS_JSON", "")
    if not raw.strip():
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON is required")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("STEGVERSE_REPO_ROOTS_JSON must be an object")
    roots: dict[str, Path] = {}
    for repo, value in parsed.items():
        if not isinstance(repo, str) or not isinstance(value, str):
            raise ValueError("repository root entries must be strings")
        root = Path(value).expanduser().resolve()
        if root.is_dir():
            roots[repo] = root
    return roots


def _now() -> dt.datetime:
    raw = os.getenv("HEALER_NOW_UTC", "").strip()
    if raw:
        value = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)


def _due(target: dict[str, Any], now: dt.datetime, mode: str) -> bool:
    if mode != "schedule":
        return True
    hours = target.get("run_hours_utc")
    if hours is not None and now.hour not in hours:
        return False
    weekdays = target.get("run_weekdays_utc")
    if weekdays is not None and now.weekday() not in weekdays:
        return False
    return True


def _run(command: list[str], cwd: Path, env_extra: dict[str, str] | None = None, timeout: int = 180) -> dict[str, Any]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
    }
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False, timeout=timeout)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def _execute_target(target: dict[str, Any], roots: dict[str, Path], all_roots_json: str) -> dict[str, Any]:
    repo = str(target.get("repo", ""))
    workflow = str(target.get("workflow", ""))
    root = roots.get(repo)
    base = {"repo": repo, "workflow": workflow}
    if target.get("audit_only"):
        return {**base, "state": "COMPLETE", "outcome": "AUDIT_ONLY_NO_EXECUTION"}
    if root is None:
        return {**base, "state": "BLOCKED", "outcome": "LOCAL_REPOSITORY_NOT_MATERIALIZED"}

    if repo == "StegVerse-Labs/SCW" and workflow == "scw_orchestrator.yml":
        inputs = target.get("inputs", {}) if isinstance(target.get("inputs"), dict) else {}
        result = _run(
            [sys.executable, "-m", "scw.scw_core"],
            root,
            {
                "SCW_CMD": str(inputs.get("cmd", "org-scan")),
                "SCW_ORGS": str(inputs.get("orgs", "StegVerse-Labs")),
                "SCW_ROOT": str(root),
                "STEGVERSE_REPO_ROOTS_JSON": all_roots_json,
            },
        )
        state = "COMPLETE" if result["returncode"] == 0 else "BLOCKED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_SCW", "execution": result}

    if repo == "StegVerse-Labs/SCW" and workflow == "uptime.yml":
        first = _run([sys.executable, "scripts/status/uptime_probe.py"], root, timeout=60)
        if first["returncode"] != 0:
            return {**base, "state": "FAILED", "outcome": "SCW_UPTIME_PROBE_FAILED", "execution": [first]}
        second = _run(["bash", "scripts/status/publish_status.sh"], root, timeout=60)
        state = "COMPLETE" if second["returncode"] == 0 else "FAILED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_SCW_UPTIME", "execution": [first, second]}

    if repo == "StegVerse-Labs/Site" and workflow == "site-task-runner.yml":
        commands = [
            [sys.executable, "scripts/site_handoff_orchestrator.py"],
            [sys.executable, "scripts/check_ecosystem_heartbeat_orchestration.py"],
        ]
        results = []
        for command in commands:
            result = _run(command, root)
            results.append(result)
            if result["returncode"] != 0:
                return {**base, "state": "BLOCKED", "outcome": "SITE_LOCAL_ORCHESTRATION_BLOCKED", "execution": results}
        return {**base, "state": "COMPLETE", "outcome": "SOVEREIGN_LOCAL_SITE_ORCHESTRATION", "execution": results}

    if repo == "StegVerse-Labs/TV" and workflow == "tv_self_heal.yml":
        return {
            **base,
            "state": "BLOCKED",
            "outcome": "TV_TVC_MUTATION_EXECUTOR_REQUIRED",
            "release_condition": "A TV/TVC-governed bounded local mutation executor applies or rejects the YAML repair set and emits a no-secret receipt.",
        }

    if repo == "StegVerse-Labs/Continuity" and workflow == "continuity.yml":
        return {
            **base,
            "state": "BLOCKED",
            "outcome": "CONTINUITY_NO_TOKEN_GUARDIAN_ADAPTER_REQUIRED",
            "release_condition": "Continuity guardian no longer resolves repositories or acknowledgement state through GitHub credentials/API and is admitted as a fixed heartbeat process adapter.",
        }

    return {**base, "state": "REVIEW_REQUIRED", "outcome": "NO_SOVEREIGN_HANDLER_BOUND"}


def build_and_execute(config_path: Path) -> dict[str, Any]:
    _forbid_github_credentials()
    config = _load_json(config_path)
    targets = config.get("targets")
    if not isinstance(targets, list):
        raise ValueError("targets must be a list")
    roots = _repo_roots()
    roots_json = json.dumps({repo: str(path) for repo, path in sorted(roots.items())}, sort_keys=True)
    scope = (os.getenv("RUN_SCOPE") or "all").strip().lower()
    mode = (os.getenv("DISPATCH_MODE") or "schedule").strip().lower()
    now = _now()

    selected = []
    for target in targets:
        if not isinstance(target, dict) or not target.get("enabled", True):
            continue
        short = str(target.get("repo", "")).split("/")[-1].lower()
        aliases = {str(value).lower() for value in target.get("aliases", [])}
        if scope != "all" and scope != short and scope not in aliases:
            continue
        if _due(target, now, mode):
            selected.append(target)

    outcomes = [_execute_target(target, roots, roots_json) for target in selected]
    terminal = "COMPLETE"
    if any(item["state"] == "FAILED" for item in outcomes):
        terminal = "FAILED"
    elif any(item["state"] == "BLOCKED" for item in outcomes):
        terminal = "BLOCKED"
    elif any(item["state"] == "REVIEW_REQUIRED" for item in outcomes):
        terminal = "REVIEW_REQUIRED"

    return {
        "schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1",
        "state": terminal,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "scope": scope,
        "mode": mode,
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "github_actions_production_role": False,
        "selected_targets": len(selected),
        "outcomes": outcomes,
    }


def main() -> int:
    config_path = Path(os.getenv("TARGETS_FILE", "data/orchestrator_targets.json")).resolve()
    try:
        receipt = build_and_execute(config_path)
    except Exception as exc:
        receipt = {
            "schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1",
            "state": "FAILED",
            "credential_authority": "TV/TVC",
            "github_token_required": False,
            "error": str(exc),
        }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
