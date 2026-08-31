#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import ssl
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

LLM_REPO = "StegVerse-org/LLM-adapter"
TVC_REPO = "StegVerse-Labs/TVC"
ROLE = "service_gateway_coinbase_skap_ciphertext_intake"
DECISION_SCHEMA = "stegverse.tvc.coinbase_service_gateway_no_value_decision/v1"
READINESS_URL = "http://127.0.0.1:8000/api/coinbase/skap/readiness"
TLS_CERT_ENV = "STEGVERSE_SERVICE_GATEWAY_TLS_CERT_FILE"
TLS_KEY_ENV = "STEGVERSE_SERVICE_GATEWAY_TLS_KEY_FILE"
TLS_BIND_ENV = "STEGVERSE_SERVICE_GATEWAY_TLS_BIND_ADDRESS"
TLS_PORT_ENV = "STEGVERSE_SERVICE_GATEWAY_TLS_PORT"
TLS_ADOPTION_RECEIPT_ENV = "STEGVERSE_TVC_SERVICE_GATEWAY_TLS_ADOPTION_RECEIPT"
TLS_ADOPTION_RECEIPT_DEFAULT = Path("/var/lib/stegverse/tvc/service-gateway-tls/latest.json")
TVC_TLS_CREDENTIAL_ROOT = Path("/run/stegverse/tv-tvc-credentials")
TLS_ADOPTION_SCHEMA = "stegverse.tvc.service_gateway_tls_material_adoption/v1"
EVALUATOR_ENABLED_ENV = "STEGVERSE_EVALUATOR_INTR_ENABLED"
EVALUATOR_UPSTREAM_ENV = "STEGVERSE_EVALUATOR_INTR_UPSTREAM"
EVALUATOR_LOOPBACK_UPSTREAM = "http://127.0.0.1:8765/intr/evaluator"
SV002_OBSERVE_ENABLED_ENV = "STEGVERSE_SV002_OBSERVE_ENABLED"
SV002_OBSERVE_UPSTREAM_ENV = "STEGVERSE_SV002_OBSERVE_UPSTREAM"
SV002_OBSERVE_LOOPBACK_UPSTREAM = "http://127.0.0.1:8766/intr/sv002-observe"
SV002_GATEWAY_READINESS_PATH = "/intr/sv002-observe/readiness"
HIL_INTR_ENABLED_ENV = "STEGVERSE_HIL_INTR_ENABLED"
HIL_INTR_UPSTREAM_ENV = "STEGVERSE_HIL_INTR_UPSTREAM"
HIL_INTR_LOOPBACK_UPSTREAM = "http://127.0.0.1:8765/intr/materialization"
HIL_INTR_GATEWAY_READINESS_PATH = "/intr/materialization/readiness"
FORBIDDEN_ENV = (
    "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT", "HEALER_GH_TOKEN", "HEALER_PAT",
    "GH_STEGVERSE_AI_TOKEN", "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    "STEGVERSE_PROVIDER_TOKEN", "STEGVERSE_MASTER_RECORDS_TOKEN",
    "STEGVERSE_EXTERNAL_REVIEW_SUBMIT_TOKEN", "STEGVERSE_EXTERNAL_REVIEW_RECEIPT_KEY",
)
DECISION_CANDIDATES = (
    "receipts/coinbase/service-gateway-intake-decision.json",
    "runtime/coinbase/service-gateway-intake-decision.json",
    "receipts/service-gateway/coinbase-skap-intake-decision.json",
)


class GatewayActivationError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(ch in "0123456789abcdef" for ch in value[7:])
    )


def _tls_bind_port() -> tuple[str, int]:
    bind_address = os.getenv(TLS_BIND_ENV, "0.0.0.0").strip() or "0.0.0.0"
    try:
        port = int(os.getenv(TLS_PORT_ENV, "443"))
    except ValueError as exc:
        raise GatewayActivationError("TLS_PORT_INVALID") from exc
    if not (1 <= port <= 65535):
        raise GatewayActivationError("TLS_PORT_INVALID")
    return bind_address, port


def _validate_tvc_tls_locator(raw: Any, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise GatewayActivationError(f"TVC_TLS_ADOPTION_{label}_LOCATOR_MISSING")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise GatewayActivationError(f"TVC_TLS_ADOPTION_{label}_LOCATOR_NOT_ABSOLUTE")
    if path.is_symlink():
        raise GatewayActivationError(f"TVC_TLS_ADOPTION_{label}_LOCATOR_SYMLINK_FORBIDDEN")
    resolved = path.resolve()
    try:
        resolved.relative_to(TVC_TLS_CREDENTIAL_ROOT.resolve())
    except ValueError as exc:
        raise GatewayActivationError(f"TVC_TLS_ADOPTION_{label}_LOCATOR_OUTSIDE_TVC_ROOT") from exc
    if not resolved.is_file():
        raise GatewayActivationError(f"TVC_TLS_ADOPTION_{label}_FILE_NOT_MATERIALIZED")
    return resolved


def validate_tls_adoption_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema": TLS_ADOPTION_SCHEMA,
        "state": "READY_FOR_STEGDEPLOY_TLS",
        "credential_authority": "TV/TVC",
        "gateway_credential_authority": "NONE",
        "provider_operation_authority": "NONE",
        "certificate_material_present": True,
        "private_key_material_present": True,
        "private_key_bytes_recorded": False,
        "private_key_exported": False,
        "credential_material_exported": False,
        "certificate_pair_verified": True,
        "certificate_hostname_verified": True,
        "certificate_time_valid": True,
        "certificate_acquisition_performed": False,
        "certificate_issuance_performed": False,
        "certificate_renewal_performed": False,
        "certificate_revocation_performed": False,
        "generalized_certificate_manager_created": False,
        "github_token_required": False,
        "production_public_route_observed": False,
        "ready_for_owner_ingress": False,
        "authority_effect": "TVC_RESIDENT_TLS_MATERIAL_ADOPTION_ONLY",
    }
    failed = [key for key, value in expected.items() if receipt.get(key) != value]
    if failed:
        raise GatewayActivationError("TVC_TLS_ADOPTION_BOUNDARY_INVALID:" + ",".join(sorted(failed)))
    if not valid_sha256(receipt.get("certificate_sha256")):
        raise GatewayActivationError("TVC_TLS_ADOPTION_CERTIFICATE_SHA256_INVALID")
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    if receipt.get("receipt_sha256") != digest(body):
        raise GatewayActivationError("TVC_TLS_ADOPTION_RECEIPT_DIGEST_INVALID")
    hostname = receipt.get("hostname")
    if not isinstance(hostname, str) or not hostname or "/" in hostname or ":" in hostname:
        raise GatewayActivationError("TVC_TLS_ADOPTION_HOSTNAME_INVALID")
    cert_file = _validate_tvc_tls_locator(receipt.get("certificate_file_locator"), "CERT")
    key_file = _validate_tvc_tls_locator(receipt.get("private_key_file_locator"), "KEY")
    return {
        "cert_file": cert_file,
        "key_file": key_file,
        "hostname": hostname,
        "certificate_sha256": receipt["certificate_sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
    }


def locate_tls_adoption_receipt() -> tuple[Path, dict[str, Any]] | None:
    explicit = os.getenv(TLS_ADOPTION_RECEIPT_ENV, "").strip()
    path = Path(explicit).expanduser().resolve() if explicit else TLS_ADOPTION_RECEIPT_DEFAULT
    if not path.is_file():
        if explicit:
            raise GatewayActivationError("TVC_TLS_ADOPTION_RECEIPT_NOT_MATERIALIZED")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GatewayActivationError("TVC_TLS_ADOPTION_RECEIPT_UNREADABLE") from exc
    if not isinstance(value, dict):
        raise GatewayActivationError("TVC_TLS_ADOPTION_RECEIPT_OBJECT_REQUIRED")
    return path, value


def resolve_tls_request() -> dict[str, Any] | None:
    cert_raw = os.getenv(TLS_CERT_ENV, "").strip()
    key_raw = os.getenv(TLS_KEY_ENV, "").strip()
    if bool(cert_raw) != bool(key_raw):
        raise GatewayActivationError("TLS_CERT_AND_KEY_LOCATORS_MUST_BE_PAIRED")

    bind_address, port = _tls_bind_port()
    if cert_raw:
        cert_file = _validate_tvc_tls_locator(cert_raw, "CERT")
        key_file = _validate_tvc_tls_locator(key_raw, "KEY")
        return {
            "cert_file": cert_file,
            "key_file": key_file,
            "bind_address": bind_address,
            "port": port,
            "locator_source": "EXPLICIT_TV_TVC_RUNTIME_FILE_PATHS",
            "adoption_receipt_sha256": None,
        }

    located = locate_tls_adoption_receipt()
    if located is None:
        return None
    _path, receipt = located
    adopted = validate_tls_adoption_receipt(receipt)
    return {
        "cert_file": adopted["cert_file"],
        "key_file": adopted["key_file"],
        "bind_address": bind_address,
        "port": port,
        "locator_source": "TVC_TLS_ADOPTION_RECEIPT",
        "adoption_receipt_sha256": adopted["receipt_sha256"],
    }

def evaluator_runtime_config() -> dict[str, Any]:
    raw = os.getenv(EVALUATOR_ENABLED_ENV, "false").strip().lower()
    if raw not in {"true", "false", "1", "0", "yes", "no"}:
        raise GatewayActivationError("EVALUATOR_INTR_ENABLED_INVALID")
    enabled = raw in {"true", "1", "yes"}
    upstream = os.getenv(EVALUATOR_UPSTREAM_ENV, EVALUATOR_LOOPBACK_UPSTREAM).strip()
    if enabled and upstream != EVALUATOR_LOOPBACK_UPSTREAM:
        raise GatewayActivationError("EVALUATOR_INTR_UPSTREAM_NOT_CANONICAL_LOOPBACK")
    return {"enabled": enabled, "upstream": upstream if enabled else ""}


def sv002_observation_runtime_config() -> dict[str, Any]:
    raw = os.getenv(SV002_OBSERVE_ENABLED_ENV, "false").strip().lower()
    if raw not in {"true", "false", "1", "0", "yes", "no"}:
        raise GatewayActivationError("SV002_OBSERVE_ENABLED_INVALID")
    enabled = raw in {"true", "1", "yes"}
    upstream = os.getenv(SV002_OBSERVE_UPSTREAM_ENV, SV002_OBSERVE_LOOPBACK_UPSTREAM).strip()
    if enabled and upstream != SV002_OBSERVE_LOOPBACK_UPSTREAM:
        raise GatewayActivationError("SV002_OBSERVE_UPSTREAM_NOT_CANONICAL_LOOPBACK")
    return {"enabled": enabled, "upstream": upstream if enabled else ""}



def hil_intr_runtime_config() -> dict[str, Any]:
    raw = os.getenv(HIL_INTR_ENABLED_ENV, "false").strip().lower()
    if raw not in {"true", "false", "1", "0", "yes", "no"}:
        raise GatewayActivationError("HIL_INTR_ENABLED_INVALID")
    enabled = raw in {"true", "1", "yes"}
    upstream = os.getenv(HIL_INTR_UPSTREAM_ENV, HIL_INTR_LOOPBACK_UPSTREAM).strip()
    if enabled and upstream != HIL_INTR_LOOPBACK_UPSTREAM:
        raise GatewayActivationError("HIL_INTR_UPSTREAM_NOT_CANONICAL_LOOPBACK")
    return {"enabled": enabled, "upstream": upstream if enabled else ""}


def validate_hil_intr_gateway_readiness(payload: dict[str, Any]) -> None:
    expected = {
        "schema": "stegverse.service-gateway.hil-intr-readiness/v1",
        "enabled": True,
        "loopback_upstream_configured": True,
        "state": "READY",
        "transport": "InTr",
        "event_triggered": True,
        "always_on_receiver_required": False,
        "second_user_device_required": False,
        "g18_completion_required": False,
        "credential_authority": "TV/TVC",
        "github_token_runtime_authority": "NONE",
        "gateway_receipt_authority": False,
        "gateway_execution_authority": False,
        "gateway_custody_authority": False,
        "authority_effect": "NONE",
    }
    failed = [key for key, value in expected.items() if payload.get(key) != value]
    if failed:
        raise GatewayActivationError(
            "HIL_INTR_GATEWAY_READINESS_INVALID:" + ",".join(sorted(failed))
        )


def _hil_intr_gateway_readiness_url(*, tls_enabled: bool, tls_request: dict[str, Any] | None) -> str:
    if tls_enabled:
        if tls_request is None:
            raise GatewayActivationError("HIL_INTR_TLS_REQUEST_MISSING")
        return f"https://127.0.0.1:{int(tls_request['port'])}{HIL_INTR_GATEWAY_READINESS_PATH}"
    return "http://127.0.0.1:8000" + HIL_INTR_GATEWAY_READINESS_PATH

def build_deploy_command(tls_request: dict[str, Any] | None) -> tuple[list[str], str, bool]:
    if tls_request is None:
        return (
            [
                sys.executable,
                "scripts/stegdeploy_native_gateway.py",
                "start",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            READINESS_URL,
            False,
        )
    port = int(tls_request["port"])
    return (
        [
            sys.executable,
            "scripts/stegdeploy_native_gateway.py",
            "start",
            "--host",
            str(tls_request["bind_address"]),
            "--port",
            str(port),
        ],
        f"https://127.0.0.1:{port}/api/coinbase/skap/readiness",
        True,
    )


def load_roots(raw_override: str | None = None) -> dict[str, Path]:
    raw = (raw_override if raw_override is not None else os.getenv("STEGVERSE_REPO_ROOTS_JSON", "")).strip()
    if not raw:
        raise GatewayActivationError("STEGVERSE_REPO_ROOTS_JSON_REQUIRED")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise GatewayActivationError("STEGVERSE_REPO_ROOTS_JSON_OBJECT_REQUIRED")
    result: dict[str, Path] = {}
    for repo, path in value.items():
        if isinstance(repo, str) and isinstance(path, str):
            root = Path(path).expanduser().resolve()
            if root.is_dir():
                result[repo] = root
    return result


def validate_decision(receipt: dict[str, Any]) -> None:
    if receipt.get("schema") != DECISION_SCHEMA:
        raise GatewayActivationError("TVC_DECISION_SCHEMA_INVALID")
    body = {k: v for k, v in receipt.items() if k != "receipt_digest"}
    if receipt.get("receipt_digest") != digest(body):
        raise GatewayActivationError("TVC_DECISION_RECEIPT_DIGEST_INVALID")
    for field in ("policy_hash", "decision_id"):
        value = receipt.get(field)
        if not valid_sha256(value):
            raise GatewayActivationError(f"TVC_DECISION_{field.upper()}_INVALID")
    if receipt.get("role") != ROLE:
        raise GatewayActivationError("TVC_DECISION_ROLE_INVALID")
    if receipt.get("admissible") is not True or receipt.get("binding_matched") is not True:
        raise GatewayActivationError("TVC_DECISION_NOT_ADMISSIBLE")
    if list(receipt.get("allowed_keys") or []) != [] or list(receipt.get("denied_keys") or []) != []:
        raise GatewayActivationError("TVC_DECISION_NO_VALUE_SCOPE_INVALID")
    if receipt.get("credential_values_available") not in (None, False):
        raise GatewayActivationError("TVC_DECISION_CREDENTIAL_VALUE_SCOPE_FORBIDDEN")
    if not isinstance(receipt.get("decision_id"), str) or not receipt.get("decision_id"):
        raise GatewayActivationError("TVC_DECISION_ID_MISSING")


def locate_decision(tvc_root: Path) -> tuple[Path, dict[str, Any]]:
    explicit = os.getenv("STEGVERSE_COINBASE_GATEWAY_TVC_DECISION_RECEIPT_FILE", "").strip()
    candidates = [Path(explicit).expanduser().resolve()] if explicit else []
    candidates.extend((tvc_root / rel).resolve() for rel in DECISION_CANDIDATES)
    for path in candidates:
        if not path.is_file():
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            continue
        validate_decision(value)
        return path, value
    raise GatewayActivationError("TVC_NO_VALUE_GATEWAY_DECISION_NOT_MATERIALIZED")


def validate_readiness(payload: dict[str, Any], decision: dict[str, Any]) -> None:
    expected = {
        "state": "READY",
        "service_id": "stegverse-service-gateway",
        "adapter": "coinbase-skap-ciphertext-staging",
        "transport_protocol": "InTr",
        "completed_boundary": "DEVICE_TO_KV",
        "credential_authority": "TV/TVC",
        "gateway_credential_value_access": False,
        "gateway_decryption_authority": False,
        "gateway_execution_authority": "NONE",
        "tvc_admission_completed": False,
        "skap_vault_admission_completed": False,
        "next_required_transition": "KV_SKAP_VAULT_INTERLOCK_ADMISSION",
        "tvc_decision_id": decision["decision_id"],
    }
    failed = [key for key, value in expected.items() if payload.get(key) != value]
    if failed:
        raise GatewayActivationError("READINESS_BOUNDARY_INVALID:" + ",".join(sorted(failed)))


def validate_sv002_gateway_readiness(payload: dict[str, Any]) -> None:
    expected = {
        "schema": "stegverse.service-gateway.sv002-observation-readiness/v1",
        "enabled": True,
        "loopback_upstream_configured": True,
        "state": "READY",
        "transport": "InTr",
        "credential_authority": "TV/TVC",
        "gateway_receipt_authority": False,
        "gateway_experiment_authority": False,
        "authority_effect": "NONE",
    }
    failed = [key for key, value in expected.items() if payload.get(key) != value]
    if failed:
        raise GatewayActivationError(
            "SV002_OBSERVATION_GATEWAY_READINESS_INVALID:" + ",".join(sorted(failed))
        )


def _sv002_gateway_readiness_url(*, tls_enabled: bool, tls_request: dict[str, Any] | None) -> str:
    if tls_enabled:
        if tls_request is None:
            raise GatewayActivationError("SV002_OBSERVATION_TLS_REQUEST_MISSING")
        return f"https://127.0.0.1:{int(tls_request['port'])}{SV002_GATEWAY_READINESS_PATH}"
    return "http://127.0.0.1:8000" + SV002_GATEWAY_READINESS_PATH


def _clean_env(
    decision: dict[str, Any],
    *,
    tls_request: dict[str, Any] | None = None,
    evaluator: dict[str, Any] | None = None,
    sv002_observe: dict[str, Any] | None = None,
    hil_intr: dict[str, Any] | None = None,
) -> dict[str, str]:
    present = [name for name in FORBIDDEN_ENV if os.getenv(name)]
    if present:
        raise GatewayActivationError("FORBIDDEN_CREDENTIAL_ENV:" + ",".join(sorted(present)))
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", str(Path.home())),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
        "STEGVERSE_COINBASE_SKAP_TVC_DECISION_RECEIPT": json.dumps(decision, sort_keys=True),
        "STEGVERSE_PROVIDER_ENABLED": "false",
        "STEGVERSE_EXTERNAL_MUTATION_ENABLED": "false",
    }
    for name in ("XDG_STATE_HOME", "XDG_CONFIG_HOME", "STEGVERSE_SERVICE_GATEWAY_NATIVE_STATE_ROOT"):
        if os.getenv(name):
            env[name] = os.environ[name]
    if tls_request is not None:
        env["STEGDEPLOY_NATIVE_TLS_CERT_FILE"] = str(tls_request["cert_file"])
        env["STEGDEPLOY_NATIVE_TLS_KEY_FILE"] = str(tls_request["key_file"])
    if evaluator and evaluator.get("enabled") is True:
        env[EVALUATOR_ENABLED_ENV] = "true"
        env[EVALUATOR_UPSTREAM_ENV] = str(evaluator["upstream"])
    else:
        env[EVALUATOR_ENABLED_ENV] = "false"
        env[EVALUATOR_UPSTREAM_ENV] = ""
    if sv002_observe and sv002_observe.get("enabled") is True:
        env[SV002_OBSERVE_ENABLED_ENV] = "true"
        env[SV002_OBSERVE_UPSTREAM_ENV] = str(sv002_observe["upstream"])
    else:
        env[SV002_OBSERVE_ENABLED_ENV] = "false"
        env[SV002_OBSERVE_UPSTREAM_ENV] = ""
    if hil_intr and hil_intr.get("enabled") is True:
        env[HIL_INTR_ENABLED_ENV] = "true"
        env[HIL_INTR_UPSTREAM_ENV] = str(hil_intr["upstream"])
    else:
        env[HIL_INTR_ENABLED_ENV] = "false"
        env[HIL_INTR_UPSTREAM_ENV] = ""
    return env


def execute(roots_json: str | None = None) -> dict[str, Any]:
    roots = load_roots(roots_json)
    llm_root = roots.get(LLM_REPO)
    tvc_root = roots.get(TVC_REPO)
    if llm_root is None:
        raise GatewayActivationError("LLM_ADAPTER_LOCAL_REPOSITORY_NOT_MATERIALIZED")
    if tvc_root is None:
        raise GatewayActivationError("TVC_LOCAL_REPOSITORY_NOT_MATERIALIZED")

    tls_request = resolve_tls_request()
    required = [
        llm_root / "scripts/stegdeploy_native_gateway.py",
        llm_root / "llm_adapter/deployed_gateway.py",
        llm_root / "llm_adapter/service_gateway_composed.py",
        llm_root / "llm_adapter/service_gateway_hil_intr.py",
    ]
    missing = [str(path.relative_to(llm_root)) for path in required if not path.is_file()]
    if missing:
        raise GatewayActivationError("LLM_ADAPTER_STEGDEPLOY_SOURCE_INCOMPLETE:" + ",".join(missing))

    decision_path, decision = locate_decision(tvc_root)
    evaluator = evaluator_runtime_config()
    sv002_observe = sv002_observation_runtime_config()
    hil_intr = hil_intr_runtime_config()
    env = _clean_env(decision, tls_request=tls_request, evaluator=evaluator, sv002_observe=sv002_observe, hil_intr=hil_intr)

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=llm_root, env={"PATH": env["PATH"]},
        text=True, capture_output=True, check=False, timeout=30,
    )
    source_head = head.stdout.strip().lower()
    if head.returncode != 0 or len(source_head) != 40:
        raise GatewayActivationError("LLM_ADAPTER_SOURCE_HEAD_UNPROVEN")

    deploy_command, readiness_url, tls_enabled = build_deploy_command(tls_request)
    deploy = subprocess.run(
        deploy_command,
        cwd=llm_root, env=env, text=True, capture_output=True, check=False, timeout=900,
    )
    if deploy.returncode != 0:
        return {
            "schema": "stegverse.healer.coinbase_stegdeploy_gateway_activation/v1",
            "state": "BLOCKED",
            "outcome": "STEGDEPLOY_BOOTSTRAP_BLOCKED",
            "source_head": source_head,
            "decision_ref": str(decision_path),
            "returncode": deploy.returncode,
            "stderr_tail": deploy.stderr[-2000:],
            "credential_authority": "TV/TVC",
            "github_token_required": False,
            "provider_operation_started": False,
            "production_public_route_observed": False,
            "tls_enabled": tls_enabled,
            "runtime_topology": "HOST_NATIVE_PYTHON_UVICORN",
            "evaluator_intr_enabled": evaluator["enabled"],
            "sv002_observation_enabled": sv002_observe["enabled"],
            "authority_effect": "NONE",
        }

    try:
        context = ssl._create_unverified_context() if tls_enabled else None
        with urllib.request.urlopen(readiness_url, timeout=5, context=context) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise GatewayActivationError("LOCAL_COINBASE_READINESS_UNAVAILABLE:" + type(exc).__name__) from exc
    if not isinstance(payload, dict):
        raise GatewayActivationError("LOCAL_COINBASE_READINESS_OBJECT_REQUIRED")
    validate_readiness(payload, decision)

    sv002_readiness = None
    sv002_readiness_url = None
    if sv002_observe["enabled"]:
        sv002_readiness_url = _sv002_gateway_readiness_url(
            tls_enabled=tls_enabled,
            tls_request=tls_request,
        )
        try:
            with urllib.request.urlopen(
                sv002_readiness_url,
                timeout=5,
                context=context,
            ) as response:
                sv002_readiness = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise GatewayActivationError(
                "LOCAL_SV002_OBSERVATION_GATEWAY_READINESS_UNAVAILABLE:" + type(exc).__name__
            ) from exc
        if not isinstance(sv002_readiness, dict):
            raise GatewayActivationError("LOCAL_SV002_OBSERVATION_GATEWAY_READINESS_OBJECT_REQUIRED")
        validate_sv002_gateway_readiness(sv002_readiness)

    return {
        "schema": "stegverse.healer.coinbase_stegdeploy_gateway_activation/v1",
        "state": "COMPLETE",
        "outcome": "LOCAL_SOVEREIGN_COINBASE_GATEWAY_TLS_READY" if tls_enabled else "LOCAL_SOVEREIGN_COINBASE_GATEWAY_READY",
        "source_head": source_head,
        "decision_ref": str(decision_path),
        "decision_id": decision["decision_id"],
        "readiness_url": readiness_url,
        "readiness": payload,
        "sv002_observation_readiness_url": sv002_readiness_url,
        "sv002_observation_readiness": sv002_readiness,
        "credential_authority": "TV/TVC",
        "credential_material_present": False,
        "github_token_required": False,
        "render_required": False,
        "tls_enabled": tls_enabled,
        "runtime_topology": "HOST_NATIVE_PYTHON_UVICORN",
        "docker_required": False,
        "evaluator_intr_enabled": evaluator["enabled"],
        "evaluator_intr_upstream": evaluator["upstream"] if evaluator["enabled"] else None,
        "sv002_observation_enabled": sv002_observe["enabled"],
        "sv002_observation_upstream": sv002_observe["upstream"] if sv002_observe["enabled"] else None,
        "tls_locator_source": str(tls_request.get("locator_source")) if tls_enabled and tls_request else "NONE",
        "tls_adoption_receipt_sha256": tls_request.get("adoption_receipt_sha256") if tls_enabled and tls_request else None,
        "tls_private_key_material_recorded": False,
        "public_certificate_hostname_verified": False,
        "network_source_fetch_performed": False,
        "provider_operation_started": False,
        "may_authorize_order": False,
        "production_public_route_observed": False,
        "authority_effect": "LOCAL_TLS_RUNTIME_OBSERVATION_ONLY" if tls_enabled else "LOCAL_RUNTIME_OBSERVATION_ONLY",
    }


def main() -> int:
    state_path_raw = os.getenv("HEALER_COINBASE_GATEWAY_STATE", "").strip()
    state_path = Path(state_path_raw).expanduser().resolve() if state_path_raw else None
    try:
        result = execute()
    except Exception as exc:
        result = {
            "schema": "stegverse.healer.coinbase_stegdeploy_gateway_activation/v1",
            "state": "BLOCKED",
            "outcome": str(exc),
            "credential_authority": "TV/TVC",
            "credential_material_present": False,
            "github_token_required": False,
            "render_required": False,
            "provider_operation_started": False,
            "production_public_route_observed": False,
            "authority_effect": "NONE",
        }
    if state_path is not None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("state") == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
