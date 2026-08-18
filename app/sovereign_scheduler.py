from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

FORBIDDEN_CREDENTIALS = (
    "HEALER_GH_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "HEALER_PAT",
    "GH_STEGVERSE_AI_TOKEN",
    "MARKETPLACE_COINBASE_EVIDENCE_TOKEN",
    "STEGVERSE_CROSS_REPO_READ_TOKEN",
)


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
    return {"command": command, "returncode": proc.returncode, "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}


def _json_tail(result: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return json.loads(str(result.get("stdout_tail", "")).strip().splitlines()[-1])
    except Exception:
        return None


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
        result = _run([sys.executable, "-m", "scw.scw_core"], root, {
            "SCW_CMD": str(inputs.get("cmd", "org-scan")),
            "SCW_ORGS": str(inputs.get("orgs", "StegVerse-Labs")),
            "SCW_ROOT": str(root),
            "STEGVERSE_REPO_ROOTS_JSON": all_roots_json,
        })
        return {**base, "state": "COMPLETE" if result["returncode"] == 0 else "BLOCKED", "outcome": "SOVEREIGN_LOCAL_SCW", "execution": result}

    if repo == "StegVerse-Labs/SCW" and workflow == "uptime.yml":
        first = _run([sys.executable, "scripts/status/uptime_probe.py"], root, timeout=60)
        if first["returncode"] != 0:
            return {**base, "state": "FAILED", "outcome": "SCW_UPTIME_PROBE_FAILED", "execution": [first]}
        second = _run(["bash", "scripts/status/publish_status.sh"], root, timeout=60)
        return {**base, "state": "COMPLETE" if second["returncode"] == 0 else "FAILED", "outcome": "SOVEREIGN_LOCAL_SCW_UPTIME", "execution": [first, second]}

    if repo == "StegVerse-Labs/Site" and workflow == "site-task-runner.yml":
        results = []
        for command in ([sys.executable, "scripts/site_handoff_orchestrator.py"], [sys.executable, "scripts/check_ecosystem_heartbeat_orchestration.py"]):
            result = _run(command, root)
            results.append(result)
            if result["returncode"] != 0:
                return {**base, "state": "BLOCKED", "outcome": "SITE_LOCAL_ORCHESTRATION_BLOCKED", "execution": results}
        return {**base, "state": "COMPLETE", "outcome": "SOVEREIGN_LOCAL_SITE_ORCHESTRATION", "execution": results}

    if repo == "StegVerse-Labs/Site" and workflow == "site-b27-native-validation":
        local_forbidden = (
            "GITHUB_TOKEN",
            "GH_TOKEN",
            "GITHUB_PAT",
            "TVC_EPHEMERAL_GITHUB_TOKEN",
            "STEGVERSE_PROVIDER_TOKEN",
            "STEGVERSE_MASTER_RECORDS_TOKEN",
            "STEGVERSE_HIL_REVIEW_TOKEN",
            "STEGVERSE_HIL_PUBLICATION_TOKEN",
            "CLOUDFLARE_API_TOKEN",
            "CLOUDFLARE_ACCOUNT_ID",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        )
        present = [name for name in local_forbidden if os.getenv(name)]
        if present:
            return {**base, "state": "BLOCKED", "outcome": "SITE_B27_FORBIDDEN_CREDENTIAL_ENV", "forbidden": sorted(present)}

        commands = [
            "scripts/check_thought_experiments_publication.py",
            "scripts/write_site_workflow_inventory.py",
            "scripts/check_site_workflow_inventory.py",
            "scripts/check_session_work_claims.py",
            "scripts/site_handoff_orchestrator.py",
            "scripts/check_ecosystem_heartbeat_orchestration.py",
            "scripts/check_ecosystem_chat_application.py",
            "scripts/check_iphone_heartbeat_transition_projection.py",
            "scripts/run_sandbox_validation.py",
            "scripts/check_stegfin_phone_projection.py",
        ]
        missing = [name for name in commands if not (root / name).is_file()]
        if missing:
            return {**base, "state": "BLOCKED", "outcome": "SITE_B27_VALIDATOR_MISSING", "missing": missing}

        head_result = _run(["git", "rev-parse", "HEAD"], root, timeout=30)
        source_head = str(head_result.get("stdout_tail", "")).strip().splitlines()[-1] if head_result["returncode"] == 0 and str(head_result.get("stdout_tail", "")).strip() else ""
        if head_result["returncode"] != 0 or len(source_head) != 40:
            return {**base, "state": "BLOCKED", "outcome": "SITE_B27_SOURCE_HEAD_UNPROVEN", "execution": head_result}

        executions = []
        for script in commands:
            result = _run([sys.executable, script], root, timeout=240)
            executions.append(result)
            if result["returncode"] != 0:
                return {
                    **base,
                    "state": "BLOCKED",
                    "outcome": "SITE_B27_VALIDATION_BLOCKED",
                    "source_head": source_head,
                    "failed_script": script,
                    "execution": executions,
                }

        thought_path = root / "thought-experiments-publication.report.json"
        inventory_path = root / "data" / "site-workflow-inventory.json"
        task_path = root / "data" / "tasks" / "SITE-ACTIONS-COST-CONTAINMENT-001-B27.json"
        if not thought_path.is_file() or not inventory_path.is_file() or not task_path.is_file():
            return {
                **base,
                "state": "BLOCKED",
                "outcome": "SITE_B27_REQUIRED_RECEIPT_MISSING",
                "source_head": source_head,
                "execution": executions,
            }

        thought = _load_json(thought_path)
        inventory = _load_json(inventory_path)
        task = _load_json(task_path)
        standalone = root / ".github" / "workflows" / "verify-thought-experiments-publication.yml"
        complete = (
            thought.get("state") == "PASS"
            and thought.get("authority_effect") is False
            and thought.get("activation_effect") is False
            and not standalone.exists()
            and inventory.get("canonical_count") == 3
            and inventory.get("placeholder_count") == 0
            and task.get("credential_authority") == "TV/TVC"
            and task.get("non_tv_tvc_secret_or_token_allowed") is False
            and task.get("github_actions_runtime_authority") == "NONE"
            and task.get("render_required") is False
        )
        receipt = {
            "schema": "stegverse.healer.site_b27_validation_receipt/v0.1",
            "state": "PASS" if complete else "BLOCKED",
            "source_head": source_head,
            "credential_authority": "TV/TVC",
            "github_token_required": False,
            "remote_checkout_required": False,
            "artifact_custody_required": False,
            "repository_writeback_authority": False,
            "runtime_authority": False,
            "wallet_signing_broadcast_authority": False,
            "publication_authority": False,
            "settlement_authority": False,
            "thought_experiments_publication": thought.get("state"),
            "thought_experiments_authority_effect": thought.get("authority_effect"),
            "thought_experiments_activation_effect": thought.get("activation_effect"),
            "standalone_workflow_retired": not standalone.exists(),
            "workflow_file_count": inventory.get("workflow_file_count"),
            "canonical_count": inventory.get("canonical_count"),
            "migration_required_operational_count": inventory.get("migration_required_operational_count"),
            "placeholder_count": inventory.get("placeholder_count"),
            "validated_scripts": commands,
        }
        return {
            **base,
            "state": "COMPLETE" if complete else "BLOCKED",
            "outcome": "SOVEREIGN_LOCAL_SITE_B27_VALIDATION",
            "source_head": source_head,
            "execution": executions,
            "receipt": receipt,
        }

    if repo == "StegVerse-Labs/Site" and workflow == "marketplace-coinbase-local-observer":
        script = root / "scripts" / "advance_marketplace_coinbase_activation.py"
        if not script.is_file():
            return {**base, "state": "BLOCKED", "outcome": "SITE_MARKETPLACE_OBSERVER_MISSING"}
        result = _run([sys.executable, str(script.relative_to(root))], root, {"STEGVERSE_REPO_ROOTS_JSON": all_roots_json}, timeout=90)
        payload = _json_tail(result)
        if result["returncode"] != 0 or not payload:
            return {**base, "state": "BLOCKED", "outcome": "SITE_MARKETPLACE_OBSERVER_FAILED", "execution": result, "receipt": payload}
        observed_state = str(payload.get("state", ""))
        state = "COMPLETE" if observed_state in {"COMPLETE", "ACTIVE_STEGVERSE_CONTINUATION"} else "BLOCKED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_SITE_MARKETPLACE_OBSERVATION", "execution": result, "receipt": payload}

    if repo == "StegVerse-Labs/Site" and workflow == "marketplace-coinbase-local-projection-import":
        script = root / "scripts" / "import_marketplace_coinbase_accessibility.py"
        if not script.is_file():
            return {**base, "state": "BLOCKED", "outcome": "SITE_MARKETPLACE_PROJECTION_IMPORTER_MISSING"}
        if roots.get("GCAT-BCAT-Engine/Publisher") is None:
            return {**base, "state": "BLOCKED", "outcome": "PUBLISHER_LOCAL_REPOSITORY_NOT_MATERIALIZED"}
        result = _run([sys.executable, str(script.relative_to(root))], root, {"STEGVERSE_REPO_ROOTS_JSON": all_roots_json}, timeout=90)
        status_path = root / "data" / "marketplace-coinbase-accessibility-status.json"
        payload = json.loads(status_path.read_text(encoding="utf-8")) if status_path.is_file() else None
        if result["returncode"] != 0 or not payload:
            return {**base, "state": "BLOCKED", "outcome": "SITE_MARKETPLACE_PROJECTION_IMPORT_FAILED", "execution": result, "receipt": payload}
        projected_state = str(payload.get("state", ""))
        state = "COMPLETE" if projected_state in {"PAPER_ACCESSIBLE", "PENDING_UPSTREAM"} else "BLOCKED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_SITE_MARKETPLACE_PROJECTION_IMPORT", "execution": result, "receipt": payload}

    if repo == "StegVerse-Labs/Site" and workflow == "child-safety-public-deployment-observer":
        script = root / "scripts" / "check_child_safety_public_deployment.py"
        if not script.is_file():
            return {**base, "state": "BLOCKED", "outcome": "SITE_CHILD_SAFETY_OBSERVER_MISSING"}
        with tempfile.TemporaryDirectory(prefix="stegverse-child-safety-") as temp_dir:
            receipt_path = Path(temp_dir) / "child-safety-public-deployment.report.json"
            result = _run(
                [sys.executable, str(script.relative_to(root))],
                root,
                {"STEGVERSE_CHILD_SAFETY_REPORT": str(receipt_path)},
                timeout=60,
            )
            payload = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else None
        if result["returncode"] != 0 or not payload:
            return {**base, "state": "BLOCKED", "outcome": "SITE_CHILD_SAFETY_PUBLIC_ROUTE_BLOCKED", "execution": result, "receipt": payload}
        complete = (
            payload.get("state") == "VERIFIED_PUBLICLY_REACHABLE"
            and payload.get("authority_effect") is False
            and payload.get("github_token_required") is False
            and payload.get("artifact_custody_required") is False
        )
        return {
            **base,
            "state": "COMPLETE" if complete else "BLOCKED",
            "outcome": "SOVEREIGN_LOCAL_SITE_CHILD_SAFETY_PUBLIC_OBSERVATION",
            "execution": result,
            "receipt": payload,
        }

    if repo == "StegVerse-Labs/repo-standards" and workflow == "st018-local-task-manager":
        script = root / "tools" / "run_st018_task_manager.py"
        registry = root / "orchestration" / "st018-task-registry.json"
        if not script.is_file():
            return {**base, "state": "BLOCKED", "outcome": "RSTD_ST018_TASK_MANAGER_MISSING"}
        if not registry.is_file():
            return {**base, "state": "BLOCKED", "outcome": "RSTD_ST018_TASK_REGISTRY_MISSING"}
        result = _run([sys.executable, str(script.relative_to(root))], root, timeout=240)
        report_path = root / "reports" / "st018-task-execution.report.json"
        payload = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
        if result["returncode"] != 0 or not payload:
            return {**base, "state": "BLOCKED", "outcome": "RSTD_ST018_TASK_MANAGER_FAILED", "execution": result, "receipt": payload}
        state = "COMPLETE" if payload.get("status") == "PASS" else "BLOCKED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_RSTD_ST018_TASK_MANAGER", "execution": result, "receipt": payload}

    if repo == "StegVerse-Labs/TV" and workflow == "tv_self_heal.yml":
        tvc_root = roots.get("StegVerse-Labs/TVC")
        if tvc_root is None:
            return {**base, "state": "BLOCKED", "outcome": "TVC_LOCAL_REPOSITORY_NOT_MATERIALIZED"}
        with tempfile.TemporaryDirectory(prefix="stegverse-tv-heal-") as temp_dir:
            receipt_path = Path(temp_dir) / "tv-self-heal.json"
            result = _run([sys.executable, "scripts/sovereign_self_heal.py"], root, {
                "STEGVERSE_TV_ROOT": str(root),
                "STEGVERSE_TVC_ROOT": str(tvc_root),
                "TV_SELF_HEAL_RECEIPT": str(receipt_path),
            }, timeout=180)
            payload = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else _json_tail(result)
        state = "COMPLETE" if result["returncode"] == 0 and payload and payload.get("state") == "COMPLETE" else "BLOCKED"
        return {**base, "state": state, "outcome": "TVC_GRANTED_LOCAL_TV_SELF_HEAL", "receipt": payload, "execution": result}

    if repo == "StegVerse-Labs/Continuity" and workflow == "continuity.yml":
        result = _run([sys.executable, "scripts/guardian.py"], root, {"STEGVERSE_REPO_ROOTS_JSON": all_roots_json, "GUARDIAN_DAYS_NO_ACK": "3"}, timeout=90)
        return {**base, "state": "COMPLETE" if result["returncode"] == 0 else "BLOCKED", "outcome": "SOVEREIGN_LOCAL_CONTINUITY_GUARDIAN", "execution": result}

    if repo == "StegVerse-Labs/StegVerse-Healer" and workflow == "quiet_enforcer.yml":
        with tempfile.TemporaryDirectory(prefix="stegverse-quiet-") as temp_dir:
            receipt = Path(temp_dir) / "quiet.json"
            result = _run([sys.executable, "app/audit_schedules.py"], root, {
                "TARGETS_FILE": str(root / "data/orchestrator_targets.json"),
                "QUIET_RECEIPT": str(receipt),
                "STEGVERSE_REPO_ROOTS_JSON": all_roots_json,
            }, timeout=90)
            payload = json.loads(receipt.read_text(encoding="utf-8")) if receipt.is_file() else None
        state = "COMPLETE" if result["returncode"] == 0 and payload and payload.get("state") == "COMPLETE" else "BLOCKED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_QUIET_ENFORCER", "receipt": payload, "execution": result}

    if repo == "StegVerse-Labs/StegVerse-Healer" and workflow == "stegdeploy-publication-relay.yml":
        with tempfile.TemporaryDirectory(prefix="stegverse-relay-") as temp_dir:
            state_path = Path(temp_dir) / "relay.json"
            intake_path = Path(temp_dir) / "intake.json"
            result = _run([sys.executable, "app/relay_stegdeploy_publication.py"], root, {
                "STEGVERSE_REPO_ROOTS_JSON": all_roots_json,
                "HEALER_RELAY_STATE": str(state_path),
                "STEGDEPLOY_RUNTIME_INTAKE_RECEIPT": str(intake_path),
                "HEALER_LAST_PUBLICATION_RECEIPT_SHA256": os.getenv("HEALER_LAST_PUBLICATION_RECEIPT_SHA256", ""),
            }, timeout=210)
            payload = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else _json_tail(result)
        state = "COMPLETE" if result["returncode"] == 0 and payload and payload.get("state") in {"COMPLETE", "NOOP_ALREADY_VERIFIED"} else "BLOCKED"
        return {**base, "state": state, "outcome": "SOVEREIGN_LOCAL_STEGDEPLOY_RELAY", "receipt": payload, "execution": result}

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
    if any(item["state"] == "FAILED" for item in outcomes): terminal = "FAILED"
    elif any(item["state"] == "BLOCKED" for item in outcomes): terminal = "BLOCKED"
    elif any(item["state"] == "REVIEW_REQUIRED" for item in outcomes): terminal = "REVIEW_REQUIRED"
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
        receipt = {"schema": "stegverse.healer.sovereign_scheduler_receipt/v0.1", "state": "FAILED", "credential_authority": "TV/TVC", "github_token_required": False, "error": str(exc)}
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
