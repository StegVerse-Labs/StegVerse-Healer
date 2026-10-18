from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from app.disposition import DISPOSITION_FIELDS, exception_failure_code, non_allow, unobserved_consequence
    from app.owning_goal import REGISTRY_SOURCE, owning_goal_for_target, registry_records_from_roots
except ImportError:  # executed as app/sovereign_scheduler.py or imported as a top-level module
    from disposition import DISPOSITION_FIELDS, exception_failure_code, non_allow, unobserved_consequence
    from owning_goal import REGISTRY_SOURCE, owning_goal_for_target, registry_records_from_roots

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


ALLOW_STATES = frozenset({"COMPLETE"})
RETRY_ENTRYPOINT = "python -m app.sovereign_scheduler"

# Per-site disposition for every non-ALLOW outcome _execute_target produces,
# keyed by the outcome code each site returns: (failure_code, failed_predicate,
# required_evidence_or_repair). Where a site returns one outcome for both ALLOW
# and non-ALLOW, failure_code names the non-ALLOW condition that site checks.
OUTCOME_DISPOSITIONS: dict[str, tuple[str, str, str]] = {
    "LOCAL_REPOSITORY_NOT_MATERIALIZED": ("LOCAL_REPOSITORY_NOT_MATERIALIZED", "target_repository_root_listed_in_STEGVERSE_REPO_ROOTS_JSON_and_is_dir", "materialize the target repository on the sovereign carrier and list its root in STEGVERSE_REPO_ROOTS_JSON"),
    "SOVEREIGN_LOCAL_SCW": ("SCW_CORE_NONZERO_EXIT", "scw_core_returncode_zero", "repair the scw.scw_core failure named in execution.stderr_tail"),
    "SCW_UPTIME_PROBE_FAILED": ("SCW_UPTIME_PROBE_FAILED", "scw_uptime_probe_returncode_zero", "repair the scripts/status/uptime_probe.py failure named in execution[0].stderr_tail"),
    "SOVEREIGN_LOCAL_SCW_UPTIME": ("SCW_STATUS_PUBLISH_NONZERO_EXIT", "scw_publish_status_returncode_zero", "repair the scripts/status/publish_status.sh failure named in execution[1].stderr_tail"),
    "SITE_LOCAL_ORCHESTRATION_BLOCKED": ("SITE_LOCAL_ORCHESTRATION_BLOCKED", "site_orchestration_scripts_returncode_zero", "repair the Site orchestration script named by the last execution entry"),
    "SITE_B27_FORBIDDEN_CREDENTIAL_ENV": ("SITE_B27_FORBIDDEN_CREDENTIAL_ENV", "site_b27_forbidden_credential_env_absent", "unset the variables named in forbidden; credentials come only from TV/TVC"),
    "SITE_B27_VALIDATOR_MISSING": ("SITE_B27_VALIDATOR_MISSING", "site_b27_validator_scripts_present", "materialize a Site source containing every script named in missing"),
    "SITE_B27_SOURCE_HEAD_UNPROVEN": ("SITE_B27_SOURCE_HEAD_UNPROVEN", "site_git_head_resolves_to_40_hex_commit", "materialize Site as a git checkout whose HEAD resolves"),
    "SITE_B27_VALIDATION_BLOCKED": ("SITE_B27_VALIDATION_BLOCKED", "site_b27_validator_scripts_returncode_zero", "repair the validator named in failed_script"),
    "SITE_B27_REQUIRED_RECEIPT_MISSING": ("SITE_B27_REQUIRED_RECEIPT_MISSING", "site_b27_required_receipts_written", "repair the validators so the thought-experiments report, workflow inventory and B27 task record are written"),
    "SOVEREIGN_LOCAL_SITE_B27_VALIDATION": ("SITE_B27_RECEIPT_PREDICATES_UNMET", "site_b27_receipt_predicates_hold", "bring the Site receipts named in receipt to the required values (PASS, no authority/activation effect, standalone workflow retired, 3 canonical, 0 placeholders, TV/TVC-only credentials)"),
    "SITE_MARKETPLACE_OBSERVER_MISSING": ("SITE_MARKETPLACE_OBSERVER_MISSING", "site_marketplace_observer_script_present", "materialize scripts/advance_marketplace_coinbase_activation.py in Site"),
    "SITE_MARKETPLACE_OBSERVER_FAILED": ("SITE_MARKETPLACE_OBSERVER_FAILED", "site_marketplace_observer_returncode_zero_with_json_receipt", "repair the observer failure named in execution.stderr_tail"),
    "SOVEREIGN_LOCAL_SITE_MARKETPLACE_OBSERVATION": ("SITE_MARKETPLACE_OBSERVATION_STATE_NOT_ADMITTED", "site_marketplace_observer_state_in_COMPLETE_or_ACTIVE_STEGVERSE_CONTINUATION", "resolve the blocker named by receipt.state in the Site marketplace activation"),
    "SITE_MARKETPLACE_PROJECTION_IMPORTER_MISSING": ("SITE_MARKETPLACE_PROJECTION_IMPORTER_MISSING", "site_marketplace_projection_importer_script_present", "materialize scripts/import_marketplace_coinbase_accessibility.py in Site"),
    "PUBLISHER_LOCAL_REPOSITORY_NOT_MATERIALIZED": ("PUBLISHER_LOCAL_REPOSITORY_NOT_MATERIALIZED", "publisher_repository_root_materialized", "materialize GCAT-BCAT-Engine/Publisher and list its root in STEGVERSE_REPO_ROOTS_JSON"),
    "SITE_MARKETPLACE_PROJECTION_IMPORT_FAILED": ("SITE_MARKETPLACE_PROJECTION_IMPORT_FAILED", "site_marketplace_projection_import_returncode_zero_with_status_file", "repair the importer failure named in execution.stderr_tail"),
    "SOVEREIGN_LOCAL_SITE_MARKETPLACE_PROJECTION_IMPORT": ("SITE_MARKETPLACE_PROJECTION_STATE_NOT_ADMITTED", "site_marketplace_projection_state_in_PAPER_ACCESSIBLE_or_PENDING_UPSTREAM", "resolve the projection state named by receipt.state"),
    "SITE_CHILD_SAFETY_OBSERVER_MISSING": ("SITE_CHILD_SAFETY_OBSERVER_MISSING", "site_child_safety_observer_script_present", "materialize scripts/check_child_safety_public_deployment.py in Site"),
    "SITE_CHILD_SAFETY_OBSERVER_TIMEOUT": ("SITE_CHILD_SAFETY_OBSERVER_TIMEOUT", "site_child_safety_observer_exits_within_bound", "repair the observer so its one-shot run exits within the bound; it must not wait on the public destination"),
    "SITE_CHILD_SAFETY_REPORT_NOT_MATERIALIZED": ("SITE_CHILD_SAFETY_REPORT_NOT_MATERIALIZED", "site_child_safety_observer_materializes_json_object_report", "repair the observer failure named in execution.stderr_tail so it writes its report to STEGVERSE_CHILD_SAFETY_REPORT"),
    "SITE_CHILD_SAFETY_REPORT_BOUNDARY_VIOLATED": ("SITE_CHILD_SAFETY_REPORT_BOUNDARY_VIOLATED", "site_child_safety_report_without_authority_token_or_artifact_custody", "resolve the report fields named in receipt (authority_effect, github_token_required, artifact_custody_required must be false)"),
    "SITE_HEARTBEAT_RESPONSE_FORBIDDEN_CREDENTIAL_ENV": ("SITE_HEARTBEAT_RESPONSE_FORBIDDEN_CREDENTIAL_ENV", "site_heartbeat_response_forbidden_credential_env_absent", "unset the variables named in forbidden; credentials come only from TV/TVC"),
    "SITE_HEARTBEAT_RESPONSE_CARRIER_SOURCE_MISSING": ("SITE_HEARTBEAT_RESPONSE_CARRIER_SOURCE_MISSING", "site_heartbeat_response_carrier_scripts_present", "materialize a Site source containing every script named in missing"),
    "SITE_HEARTBEAT_RESPONSE_SOURCE_HEAD_UNPROVEN": ("SITE_HEARTBEAT_RESPONSE_SOURCE_HEAD_UNPROVEN", "site_git_head_resolves_to_40_hex_commit", "materialize Site as a git checkout whose HEAD resolves"),
    "SITE_HEARTBEAT_RESPONSE_SOVEREIGN_EXECUTION_BLOCKED": ("SITE_HEARTBEAT_RESPONSE_SOVEREIGN_EXECUTION_BLOCKED", "site_heartbeat_response_steps_returncode_zero", "repair the step named in failed_step"),
    "SITE_STEGFIN_PUBLICATION_FORBIDDEN_CREDENTIAL_ENV": ("SITE_STEGFIN_PUBLICATION_FORBIDDEN_CREDENTIAL_ENV", "site_stegfin_publication_forbidden_credential_env_absent", "unset the variables named in forbidden; credentials come only from TV/TVC"),
    "SITE_STEGFIN_PUBLICATION_OBSERVER_MISSING": ("SITE_STEGFIN_PUBLICATION_OBSERVER_MISSING", "site_stegfin_publication_observer_script_present", "materialize scripts/check_stegfin_public_wallet_transport.py in Site"),
    "SITE_STEGFIN_PUBLICATION_OBSERVATION_BLOCKED": ("SITE_STEGFIN_PUBLICATION_OBSERVATION_BLOCKED", "site_stegfin_publication_observer_returncode_zero_with_report", "repair the observer failure named in execution.stderr_tail"),
    "SOVEREIGN_LOCAL_SITE_STEGFIN_PUBLICATION_OBSERVATION": ("SITE_STEGFIN_PUBLICATION_PREDICATES_UNMET", "site_stegfin_publication_report_verified_with_pinned_ui_blob_and_tv_tvc_only_credentials", "resolve the report fields named in receipt"),
    "RSTD_ST018_TASK_MANAGER_MISSING": ("RSTD_ST018_TASK_MANAGER_MISSING", "rstd_st018_task_manager_script_present", "materialize tools/run_st018_task_manager.py in repo-standards"),
    "RSTD_ST018_TASK_REGISTRY_MISSING": ("RSTD_ST018_TASK_REGISTRY_MISSING", "rstd_st018_task_registry_present", "materialize orchestration/st018-task-registry.json in repo-standards"),
    "RSTD_ST018_TASK_MANAGER_FAILED": ("RSTD_ST018_TASK_MANAGER_FAILED", "rstd_st018_task_manager_returncode_zero_with_report", "repair the task-manager failure named in execution.stderr_tail"),
    "SOVEREIGN_LOCAL_RSTD_ST018_TASK_MANAGER": ("RSTD_ST018_REPORT_STATUS_NOT_PASS", "rstd_st018_report_status_PASS", "resolve the failing ST-018 tasks named in receipt"),
    "TVC_LOCAL_REPOSITORY_NOT_MATERIALIZED": ("TVC_LOCAL_REPOSITORY_NOT_MATERIALIZED", "tvc_repository_root_materialized", "materialize StegVerse-Labs/TVC and list its root in STEGVERSE_REPO_ROOTS_JSON"),
    "TVC_GRANTED_LOCAL_TV_SELF_HEAL": ("TV_SELF_HEAL_NOT_COMPLETE", "tv_self_heal_returncode_zero_and_receipt_state_COMPLETE", "resolve the TV self-heal blocker named in receipt or execution.stderr_tail"),
    "SOVEREIGN_LOCAL_CONTINUITY_GUARDIAN": ("CONTINUITY_GUARDIAN_NONZERO_EXIT", "continuity_guardian_returncode_zero", "repair the scripts/guardian.py failure named in execution.stderr_tail"),
    "SOVEREIGN_LOCAL_QUIET_ENFORCER": ("QUIET_ENFORCER_NOT_COMPLETE", "quiet_enforcer_returncode_zero_and_receipt_state_COMPLETE", "resolve the condition named by receipt.failure_code"),
    "SOVEREIGN_LOCAL_STEGDEPLOY_RELAY": ("STEGDEPLOY_RELAY_NOT_COMPLETE", "stegdeploy_relay_returncode_zero_and_receipt_state_COMPLETE_or_NOOP_ALREADY_VERIFIED", "resolve the condition named by receipt.failure_code"),
    "SOVEREIGN_LOCAL_COINBASE_STEGDEPLOY_GATEWAY": ("COINBASE_STEGDEPLOY_GATEWAY_NOT_COMPLETE", "coinbase_gateway_activation_receipt_state_COMPLETE", "resolve the condition named by receipt.failure_code"),
    "NO_SOVEREIGN_HANDLER_BOUND": ("NO_SOVEREIGN_HANDLER_BOUND", "sovereign_local_handler_bound_for_repo_and_workflow", "bind a sovereign local handler for this repo/workflow in app/sovereign_scheduler.py or disable the target"),
}


def _target_retry_entrypoint(target: dict[str, Any]) -> str:
    aliases = target.get("aliases") if isinstance(target.get("aliases"), list) else []
    scope = str(aliases[0]) if aliases else str(target.get("repo", "")).split("/")[-1].lower()
    return f"RUN_SCOPE={scope} DISPATCH_MODE=manual {RETRY_ENTRYPOINT}"


def _with_disposition(target: dict[str, Any], record: dict[str, Any],
                      registry_records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Attach the six disposition fields to a non-ALLOW outcome that lacks them.

    The owning goal is the target's canonical_owner, else the one canonical task
    record that names it (``registry_records``; ``None`` means the registry is not
    materialized). Otherwise the lane default owns only the gap, and the six-field
    ``owning_goal_refusal`` says why no owner was derived. Metadata only: the
    record's state and outcome are never changed here.
    """
    if record.get("state") in ALLOW_STATES:
        return record
    missing = [field for field in DISPOSITION_FIELDS if not record.get(field)]
    if not missing:
        return record
    outcome = str(record.get("outcome", ""))
    failure_code, predicate, repair = OUTCOME_DISPOSITIONS.get(
        outcome, (outcome or "SOVEREIGN_TARGET_NOT_COMPLETE", "sovereign_target_outcome_admitted", "resolve the condition named by outcome"))
    receipt = record.get("receipt")
    if isinstance(receipt, dict) and receipt.get("failure_code"):
        failure_code = f"{failure_code}:{receipt['failure_code']}"
    retry_entrypoint = _target_retry_entrypoint(target)
    owner, refusal = owning_goal_for_target(target, registry_records, retry_entrypoint=retry_entrypoint)
    derived = non_allow(failure_code, predicate, repair, retry_entrypoint=retry_entrypoint,
                        owning_existing_goal=owner or (refusal or {})["owning_existing_goal"])
    # A record that already names some fields keeps them; only the missing ones are completed.
    completed = {**record, **{field: derived[field] for field in missing}}
    if "owning_existing_goal" in missing:
        if refusal is not None:
            # No owner is guessed: the lane default owns the gap, and the refusal names the repair.
            completed["owning_goal_refusal"] = refusal
        elif not str(target.get("canonical_owner") or "").strip():
            completed["owning_existing_goal_source"] = REGISTRY_SOURCE
    return completed


RECEIVER_UNAVAILABLE_DISPOSITION = "DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION"
CHILD_SAFETY_RECONCILIATION_ENTRYPOINT = "STEGVERSE_CHILD_SAFETY_REPORT=<local report path> python scripts/check_child_safety_public_deployment.py (cwd: StegVerse-Labs/Site root)"
CHILD_SAFETY_BOUNDARY_FIELDS = ("authority_effect", "github_token_required", "artifact_custody_required")


def _child_safety_reachability(payload: dict[str, Any], observer_returncode: int) -> dict[str, Any]:
    """Record public reachability as an observation field; never wait or poll for it."""
    if payload.get("state") == "VERIFIED_PUBLICLY_REACHABLE" and observer_returncode == 0:
        evidence = {key: value for key, value in payload.items() if key not in CHILD_SAFETY_BOUNDARY_FIELDS}
        return {"reachability_observation": {"consequence_observation": "OBSERVED", "state": "VERIFIED_PUBLICLY_REACHABLE", "evidence": evidence}}
    observation = {**unobserved_consequence(CHILD_SAFETY_RECONCILIATION_ENTRYPOINT),
                   "observer_reported_state": payload.get("state"), "observer_returncode": observer_returncode}
    return {"reachability_observation": observation, "receiver_unavailable_disposition": RECEIVER_UNAVAILABLE_DISPOSITION}


_REGISTRY_FROM_ROOTS = object()


def _execute_target(target: dict[str, Any], roots: dict[str, Path], all_roots_json: str,
                    registry_records: Any = _REGISTRY_FROM_ROOTS) -> dict[str, Any]:
    record = _execute_target_handler(target, roots, all_roots_json)
    if registry_records is _REGISTRY_FROM_ROOTS:
        registry_records = registry_records_from_roots(roots)
    return _with_disposition(target, record, registry_records)


def _execute_target_handler(target: dict[str, Any], roots: dict[str, Path], all_roots_json: str) -> dict[str, Any]:
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

    if repo == "StegVerse-Labs/Site" and workflow == "executive-rhetoric-ledger-local-sync":
        from app.site_erl_sync import execute_site_erl_sync
        return execute_site_erl_sync(target, roots, base)

    if repo == "StegVerse-Labs/Site" and workflow == "site-b27-native-validation":
        local_forbidden = (
            "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT", "TVC_EPHEMERAL_GITHUB_TOKEN",
            "STEGVERSE_PROVIDER_TOKEN", "STEGVERSE_MASTER_RECORDS_TOKEN", "STEGVERSE_HIL_REVIEW_TOKEN",
            "STEGVERSE_HIL_PUBLICATION_TOKEN", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
        )
        present = [name for name in local_forbidden if os.getenv(name)]
        if present:
            return {**base, "state": "BLOCKED", "outcome": "SITE_B27_FORBIDDEN_CREDENTIAL_ENV", "forbidden": sorted(present)}
        commands = [
            "scripts/check_thought_experiments_publication.py", "scripts/write_site_workflow_inventory.py",
            "scripts/check_site_workflow_inventory.py", "scripts/check_session_work_claims.py",
            "scripts/site_handoff_orchestrator.py", "scripts/check_ecosystem_heartbeat_orchestration.py",
            "scripts/check_ecosystem_chat_application.py", "scripts/check_iphone_heartbeat_transition_projection.py",
            "scripts/run_sandbox_validation.py", "scripts/check_stegfin_phone_projection.py",
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
                return {**base, "state": "BLOCKED", "outcome": "SITE_B27_VALIDATION_BLOCKED", "source_head": source_head, "failed_script": script, "execution": executions}
        thought_path = root / "thought-experiments-publication.report.json"
        inventory_path = root / "data" / "site-workflow-inventory.json"
        task_path = root / "data" / "tasks" / "SITE-ACTIONS-COST-CONTAINMENT-001-B27.json"
        if not thought_path.is_file() or not inventory_path.is_file() or not task_path.is_file():
            return {**base, "state": "BLOCKED", "outcome": "SITE_B27_REQUIRED_RECEIPT_MISSING", "source_head": source_head, "execution": executions}
        thought = _load_json(thought_path); inventory = _load_json(inventory_path); task = _load_json(task_path)
        standalone = root / ".github" / "workflows" / "verify-thought-experiments-publication.yml"
        complete = (thought.get("state") == "PASS" and thought.get("authority_effect") is False and thought.get("activation_effect") is False and not standalone.exists() and inventory.get("canonical_count") == 3 and inventory.get("placeholder_count") == 0 and task.get("credential_authority") == "TV/TVC" and task.get("non_tv_tvc_secret_or_token_allowed") is False and task.get("github_actions_runtime_authority") == "NONE" and task.get("render_required") is False)
        receipt = {"schema":"stegverse.healer.site_b27_validation_receipt/v0.1","state":"PASS" if complete else "BLOCKED",**({} if complete else non_allow("SITE_B27_RECEIPT_PREDICATES_UNMET", "site_b27_receipt_predicates_hold", "bring the Site receipts to the required values", retry_entrypoint=_target_retry_entrypoint(target))),"source_head":source_head,"credential_authority":"TV/TVC","github_token_required":False,"remote_checkout_required":False,"artifact_custody_required":False,"repository_writeback_authority":False,"runtime_authority":False,"wallet_signing_broadcast_authority":False,"publication_authority":False,"settlement_authority":False,"thought_experiments_publication":thought.get("state"),"thought_experiments_authority_effect":thought.get("authority_effect"),"thought_experiments_activation_effect":thought.get("activation_effect"),"standalone_workflow_retired":not standalone.exists(),"workflow_file_count":inventory.get("workflow_file_count"),"canonical_count":inventory.get("canonical_count"),"migration_required_operational_count":inventory.get("migration_required_operational_count"),"placeholder_count":inventory.get("placeholder_count"),"validated_scripts":commands}
        return {**base, "state": "COMPLETE" if complete else "BLOCKED", "outcome": "SOVEREIGN_LOCAL_SITE_B27_VALIDATION", "source_head": source_head, "execution": executions, "receipt": receipt}

    if repo == "StegVerse-Labs/Site" and workflow == "marketplace-coinbase-local-observer":
        script = root / "scripts" / "advance_marketplace_coinbase_activation.py"
        if not script.is_file(): return {**base,"state":"BLOCKED","outcome":"SITE_MARKETPLACE_OBSERVER_MISSING"}
        result = _run([sys.executable, str(script.relative_to(root))], root, {"STEGVERSE_REPO_ROOTS_JSON": all_roots_json}, timeout=90)
        payload = _json_tail(result)
        if result["returncode"] != 0 or not payload: return {**base,"state":"BLOCKED","outcome":"SITE_MARKETPLACE_OBSERVER_FAILED","execution":result,"receipt":payload}
        state = "COMPLETE" if str(payload.get("state", "")) in {"COMPLETE","ACTIVE_STEGVERSE_CONTINUATION"} else "BLOCKED"
        return {**base,"state":state,"outcome":"SOVEREIGN_LOCAL_SITE_MARKETPLACE_OBSERVATION","execution":result,"receipt":payload}

    if repo == "StegVerse-Labs/Site" and workflow == "marketplace-coinbase-local-projection-import":
        script = root / "scripts" / "import_marketplace_coinbase_accessibility.py"
        if not script.is_file(): return {**base,"state":"BLOCKED","outcome":"SITE_MARKETPLACE_PROJECTION_IMPORTER_MISSING"}
        if roots.get("GCAT-BCAT-Engine/Publisher") is None: return {**base,"state":"BLOCKED","outcome":"PUBLISHER_LOCAL_REPOSITORY_NOT_MATERIALIZED"}
        result = _run([sys.executable, str(script.relative_to(root))], root, {"STEGVERSE_REPO_ROOTS_JSON": all_roots_json}, timeout=90)
        status_path = root / "data" / "marketplace-coinbase-accessibility-status.json"; payload = json.loads(status_path.read_text(encoding="utf-8")) if status_path.is_file() else None
        if result["returncode"] != 0 or not payload: return {**base,"state":"BLOCKED","outcome":"SITE_MARKETPLACE_PROJECTION_IMPORT_FAILED","execution":result,"receipt":payload}
        state = "COMPLETE" if str(payload.get("state", "")) in {"PAPER_ACCESSIBLE","PENDING_UPSTREAM"} else "BLOCKED"
        return {**base,"state":state,"outcome":"SOVEREIGN_LOCAL_SITE_MARKETPLACE_PROJECTION_IMPORT","execution":result,"receipt":payload}

    if repo == "StegVerse-Labs/Site" and workflow == "child-safety-public-deployment-observer":
        script = root / "scripts" / "check_child_safety_public_deployment.py"
        if not script.is_file(): return {**base,"state":"BLOCKED","outcome":"SITE_CHILD_SAFETY_OBSERVER_MISSING"}
        # The controlled step is the one-shot observer run materializing its local
        # report; public reachability is recorded, never a transition predicate.
        with tempfile.TemporaryDirectory(prefix="stegverse-child-safety-") as temp_dir:
            receipt_path = Path(temp_dir) / "child-safety-public-deployment.report.json"
            try:
                result = _run([sys.executable, str(script.relative_to(root))], root, {"STEGVERSE_CHILD_SAFETY_REPORT": str(receipt_path)}, timeout=60)
            except subprocess.TimeoutExpired:
                return {**base,"state":"BLOCKED","outcome":"SITE_CHILD_SAFETY_OBSERVER_TIMEOUT","receiver_unavailable_disposition":RECEIVER_UNAVAILABLE_DISPOSITION,"reachability_observation":unobserved_consequence(CHILD_SAFETY_RECONCILIATION_ENTRYPOINT)}
            try:
                payload = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else None
            except ValueError:
                payload = None
        if not isinstance(payload, dict) or not payload: return {**base,"state":"BLOCKED","outcome":"SITE_CHILD_SAFETY_REPORT_NOT_MATERIALIZED","execution":result,"receipt":payload}
        if not all(payload.get(name) is False for name in CHILD_SAFETY_BOUNDARY_FIELDS): return {**base,"state":"BLOCKED","outcome":"SITE_CHILD_SAFETY_REPORT_BOUNDARY_VIOLATED","execution":result,"receipt":payload}
        record = {**base,"state":"COMPLETE","outcome":"SOVEREIGN_LOCAL_SITE_CHILD_SAFETY_PUBLIC_OBSERVATION","execution":result,"receipt":payload}
        return {**record, **_child_safety_reachability(payload, result["returncode"])}

    if repo == "StegVerse-Labs/Site" and workflow == "heartbeat-response-sovereign-carrier":
        local_forbidden = ("GITHUB_TOKEN","GH_TOKEN","GITHUB_PAT","TVC_EPHEMERAL_GITHUB_TOKEN","STEGVERSE_PROVIDER_TOKEN","STEGVERSE_MASTER_RECORDS_TOKEN","CLOUDFLARE_API_TOKEN","CLOUDFLARE_ACCOUNT_ID","ACTIONS_ID_TOKEN_REQUEST_TOKEN")
        present = [name for name in local_forbidden if os.getenv(name)]
        if present:
            return {**base,"state":"BLOCKED","outcome":"SITE_HEARTBEAT_RESPONSE_FORBIDDEN_CREDENTIAL_ENV","forbidden":sorted(present)}
        commands = [
            ([sys.executable,"scripts/process_heartbeat_response_node.py","--apply"], "node_apply"),
            ([sys.executable,"scripts/collect_heartbeat_response_receipts.py","--apply"], "collector_apply"),
            ([sys.executable,"scripts/check_heartbeat_response_network.py"], "network_validation"),
        ]
        missing = [command[0][1] for command in commands if not (root / command[0][1]).is_file()]
        if missing:
            return {**base,"state":"BLOCKED","outcome":"SITE_HEARTBEAT_RESPONSE_CARRIER_SOURCE_MISSING","missing":missing}
        head_result = _run(["git","rev-parse","HEAD"], root, timeout=30)
        source_head = str(head_result.get("stdout_tail","")).strip().splitlines()[-1] if head_result["returncode"] == 0 and str(head_result.get("stdout_tail","")).strip() else ""
        if head_result["returncode"] != 0 or len(source_head) != 40:
            return {**base,"state":"BLOCKED","outcome":"SITE_HEARTBEAT_RESPONSE_SOURCE_HEAD_UNPROVEN","execution":head_result}
        executions = []
        for command, label in commands:
            result = _run(command, root, timeout=240)
            result["label"] = label
            executions.append(result)
            if result["returncode"] != 0:
                return {**base,"state":"BLOCKED","outcome":"SITE_HEARTBEAT_RESPONSE_SOVEREIGN_EXECUTION_BLOCKED","source_head":source_head,"failed_step":label,"execution":executions}
        receipt = {
            "schema":"stegverse.healer.site_heartbeat_response_carrier_receipt/v0.1",
            "state":"PASS",
            "source_head":source_head,
            "canonical_owner":"StegVerse-Labs/Site#234",
            "migration_issue":"StegVerse-Labs/Site#411",
            "credential_authority":"TV/TVC",
            "github_token_required":False,
            "remote_checkout_required":False,
            "artifact_custody_required":False,
            "repository_writeback_authority":False,
            "local_state_mutation":True,
            "runtime_authority":False,
            "activation_authority":False,
            "publication_authority":False,
            "custody_authority":False,
            "release_authority":False,
            "commands":[item[0] for item in commands],
            "persistence_boundary":"LOCAL_MATERIALIZED_SITE_ONLY_UNTIL_SEPARATELY_ADMITTED_PROPAGATION",
        }
        return {**base,"state":"COMPLETE","outcome":"SOVEREIGN_LOCAL_SITE_HEARTBEAT_RESPONSE_CARRIER","source_head":source_head,"execution":executions,"receipt":receipt}

    if repo == "StegVerse-Labs/Site" and workflow == "stegfin-public-wallet-transport-observer":
        local_forbidden = ("GITHUB_TOKEN","GH_TOKEN","GITHUB_PAT","TVC_EPHEMERAL_GITHUB_TOKEN","STEGVERSE_PROVIDER_TOKEN","STEGVERSE_MASTER_RECORDS_TOKEN","CLOUDFLARE_API_TOKEN","CLOUDFLARE_ACCOUNT_ID","ACTIONS_ID_TOKEN_REQUEST_TOKEN")
        present = [name for name in local_forbidden if os.getenv(name)]
        if present: return {**base,"state":"BLOCKED","outcome":"SITE_STEGFIN_PUBLICATION_FORBIDDEN_CREDENTIAL_ENV","forbidden":sorted(present)}
        script = root / "scripts" / "check_stegfin_public_wallet_transport.py"
        if not script.is_file(): return {**base,"state":"BLOCKED","outcome":"SITE_STEGFIN_PUBLICATION_OBSERVER_MISSING"}
        with tempfile.TemporaryDirectory(prefix="stegverse-stegfin-publication-") as temp_dir:
            receipt_path = Path(temp_dir) / "stegfin-public-wallet-transport.report.json"
            result = _run([sys.executable, str(script.relative_to(root))], root, {"STEGFIN_PUBLICATION_REPORT": str(receipt_path)}, timeout=60)
            payload = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else None
        if result["returncode"] != 0 or not payload: return {**base,"state":"BLOCKED","outcome":"SITE_STEGFIN_PUBLICATION_OBSERVATION_BLOCKED","execution":result,"receipt":payload}
        complete = payload.get("state") == "VERIFIED_PUBLICATION" and payload.get("publication_proven") is True and payload.get("observed_ui_blob") == "114b3c39052d5b1622407080407259a0040a1369" and payload.get("credential_authority") == "TV/TVC" and payload.get("credential_requirement") == "NONE" and payload.get("non_tv_tvc_secret_or_token_used") is False and payload.get("github_token_required") is False and payload.get("render_required") is False and payload.get("authority_effect") is False
        return {**base,"state":"COMPLETE" if complete else "BLOCKED","outcome":"SOVEREIGN_LOCAL_SITE_STEGFIN_PUBLICATION_OBSERVATION","execution":result,"receipt":payload}

    if repo == "StegVerse-Labs/repo-standards" and workflow == "st018-local-task-manager":
        script = root / "tools" / "run_st018_task_manager.py"; registry = root / "orchestration" / "st018-task-registry.json"
        if not script.is_file(): return {**base,"state":"BLOCKED","outcome":"RSTD_ST018_TASK_MANAGER_MISSING"}
        if not registry.is_file(): return {**base,"state":"BLOCKED","outcome":"RSTD_ST018_TASK_REGISTRY_MISSING"}
        result = _run([sys.executable, str(script.relative_to(root))], root, timeout=240)
        report_path = root / "reports" / "st018-task-execution.report.json"; payload = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else None
        if result["returncode"] != 0 or not payload: return {**base,"state":"BLOCKED","outcome":"RSTD_ST018_TASK_MANAGER_FAILED","execution":result,"receipt":payload}
        state = "COMPLETE" if payload.get("status") == "PASS" else "BLOCKED"
        return {**base,"state":state,"outcome":"SOVEREIGN_LOCAL_RSTD_ST018_TASK_MANAGER","execution":result,"receipt":payload}

    if repo == "StegVerse-Labs/TV" and workflow == "tv_self_heal.yml":
        tvc_root = roots.get("StegVerse-Labs/TVC")
        if tvc_root is None: return {**base,"state":"BLOCKED","outcome":"TVC_LOCAL_REPOSITORY_NOT_MATERIALIZED"}
        with tempfile.TemporaryDirectory(prefix="stegverse-tv-heal-") as temp_dir:
            receipt_path = Path(temp_dir) / "tv-self-heal.json"
            result = _run([sys.executable,"scripts/sovereign_self_heal.py"], root, {"STEGVERSE_TV_ROOT":str(root),"STEGVERSE_TVC_ROOT":str(tvc_root),"TV_SELF_HEAL_RECEIPT":str(receipt_path)}, timeout=180)
            payload = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else _json_tail(result)
        state = "COMPLETE" if result["returncode"] == 0 and payload and payload.get("state") == "COMPLETE" else "BLOCKED"
        return {**base,"state":state,"outcome":"TVC_GRANTED_LOCAL_TV_SELF_HEAL","receipt":payload,"execution":result}

    if repo == "StegVerse-Labs/Continuity" and workflow == "continuity.yml":
        result = _run([sys.executable,"scripts/guardian.py"], root, {"STEGVERSE_REPO_ROOTS_JSON":all_roots_json,"GUARDIAN_DAYS_NO_ACK":"3"}, timeout=90)
        return {**base,"state":"COMPLETE" if result["returncode"] == 0 else "BLOCKED","outcome":"SOVEREIGN_LOCAL_CONTINUITY_GUARDIAN","execution":result}

    if repo == "StegVerse-Labs/StegVerse-Healer" and workflow == "quiet_enforcer.yml":
        with tempfile.TemporaryDirectory(prefix="stegverse-quiet-") as temp_dir:
            receipt = Path(temp_dir) / "quiet.json"
            result = _run([sys.executable,"app/audit_schedules.py"], root, {"TARGETS_FILE":str(root / "data/orchestrator_targets.json"),"QUIET_RECEIPT":str(receipt),"STEGVERSE_REPO_ROOTS_JSON":all_roots_json}, timeout=90)
            payload = json.loads(receipt.read_text(encoding="utf-8")) if receipt.is_file() else None
        state = "COMPLETE" if result["returncode"] == 0 and payload and payload.get("state") == "COMPLETE" else "BLOCKED"
        return {**base,"state":state,"outcome":"SOVEREIGN_LOCAL_QUIET_ENFORCER","receipt":payload,"execution":result}

    if repo == "StegVerse-Labs/StegVerse-Healer" and workflow == "stegdeploy-publication-relay.yml":
        with tempfile.TemporaryDirectory(prefix="stegverse-relay-") as temp_dir:
            state_path = Path(temp_dir) / "relay.json"; intake_path = Path(temp_dir) / "intake.json"
            result = _run([sys.executable,"app/relay_stegdeploy_publication.py"], root, {"STEGVERSE_REPO_ROOTS_JSON":all_roots_json,"HEALER_RELAY_STATE":str(state_path),"STEGDEPLOY_RUNTIME_INTAKE_RECEIPT":str(intake_path),"HEALER_LAST_PUBLICATION_RECEIPT_SHA256":os.getenv("HEALER_LAST_PUBLICATION_RECEIPT_SHA256","")}, timeout=210)
            payload = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else _json_tail(result)
        state = "COMPLETE" if result["returncode"] == 0 and payload and payload.get("state") in {"COMPLETE","NOOP_ALREADY_VERIFIED"} else "BLOCKED"
        return {**base,"state":state,"outcome":"SOVEREIGN_LOCAL_STEGDEPLOY_RELAY","receipt":payload,"execution":result}

    if repo == "StegVerse-org/LLM-adapter" and workflow == "coinbase-stegdeploy-sovereign-gateway":
        from app.coinbase_stegdeploy_gateway import execute as execute_coinbase_gateway
        try:
            payload = execute_coinbase_gateway(all_roots_json)
        except Exception as exc:
            payload = {
                "schema":"stegverse.healer.coinbase_stegdeploy_gateway_activation/v1",
                "state":"BLOCKED",
                "outcome":str(exc),
                **non_allow(str(exc) or type(exc).__name__, "coinbase_gateway_activation_preconditions_met",
                            "supply or repair the input named by failure_code",
                            retry_entrypoint=_target_retry_entrypoint(target), owning_existing_goal=str(target.get("canonical_owner") or "") or "LLMA-DECLARED-PATH-CONFORMANCE-368"),
                "credential_authority":"TV/TVC",
                "github_token_required":False,
                "provider_operation_started":False,
                "production_public_route_observed":False,
                "authority_effect":"NONE",
            }
        state = "COMPLETE" if payload.get("state") == "COMPLETE" else "BLOCKED"
        return {**base,"state":state,"outcome":"SOVEREIGN_LOCAL_COINBASE_STEGDEPLOY_GATEWAY","receipt":payload}

    return {**base, "state": "REVIEW_REQUIRED", "outcome": "NO_SOVEREIGN_HANDLER_BOUND"}


def build_and_execute(config_path: Path) -> dict[str, Any]:
    _forbid_github_credentials(); config = _load_json(config_path); targets = config.get("targets")
    if not isinstance(targets, list): raise ValueError("targets must be a list")
    roots = _repo_roots(); roots_json = json.dumps({repo:str(path) for repo,path in sorted(roots.items())}, sort_keys=True)
    scope = (os.getenv("RUN_SCOPE") or "all").strip().lower(); mode = (os.getenv("DISPATCH_MODE") or "schedule").strip().lower(); now = _now(); selected = []
    for target in targets:
        if not isinstance(target, dict) or not target.get("enabled", True): continue
        short = str(target.get("repo", "")).split("/")[-1].lower(); aliases = {str(value).lower() for value in target.get("aliases", [])}
        if scope != "all" and scope != short and scope not in aliases: continue
        if _due(target, now, mode): selected.append(target)
    registry_records = registry_records_from_roots(roots)  # read once; only disposition metadata uses it
    outcomes = [_execute_target(target, roots, roots_json, registry_records) for target in selected]
    terminal = "COMPLETE"
    if any(item["state"] == "FAILED" for item in outcomes): terminal = "FAILED"
    elif any(item["state"] == "BLOCKED" for item in outcomes): terminal = "BLOCKED"
    elif any(item["state"] == "REVIEW_REQUIRED" for item in outcomes): terminal = "REVIEW_REQUIRED"
    disposition: dict[str, str] = {}
    if terminal not in ALLOW_STATES:
        first = next(item for item in outcomes if item["state"] == terminal)
        disposition = non_allow(f"SCHEDULER_TARGET_{terminal}:{first.get('failure_code') or first.get('outcome')}",
                                "every_selected_target_state_COMPLETE",
                                f"repair {first.get('repo')}/{first.get('workflow')} per its outcome disposition",
                                retry_entrypoint=str(first.get("retry_entrypoint") or RETRY_ENTRYPOINT),
                                **({"owning_existing_goal": first["owning_existing_goal"]} if first.get("owning_existing_goal") else {}))
    return {"schema":"stegverse.healer.sovereign_scheduler_receipt/v0.1","state":terminal,**disposition,"generated_at":now.isoformat().replace("+00:00","Z"),"scope":scope,"mode":mode,"credential_authority":"TV/TVC","github_token_required":False,"github_actions_production_role":False,"selected_targets":len(selected),"outcomes":outcomes}


def main() -> int:
    config_path = Path(os.getenv("TARGETS_FILE", "data/orchestrator_targets.json")).resolve()
    try: receipt = build_and_execute(config_path)
    except Exception as exc: receipt = {"schema":"stegverse.healer.sovereign_scheduler_receipt/v0.1","state":"FAILED",**non_allow(exception_failure_code(exc, "SCHEDULER_CONFIGURATION_INVALID"), "scheduler_configuration_and_repo_roots_valid", "repair the configuration named in error", retry_entrypoint=RETRY_ENTRYPOINT),"credential_authority":"TV/TVC","github_token_required":False,"error":str(exc)}
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["state"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())