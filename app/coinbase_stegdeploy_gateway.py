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


def resolve_tls_request() -> dict[str, Any] | None:
    cert_raw = os.getenv(TLS_CERT_ENV, "").strip()
    key_raw = os.getenv(TLS_KEY_ENV, "").strip()
    if bool(cert_raw) != bool(key_raw):
        raise GatewayActivationError("TLS_CERT_AND_KEY_LOCATORS_MUST_BE_PAIRED")
    if not cert_raw:
        return None

    cert_file = Path(cert_raw).expanduser().resolve()
    key_file = Path(key_raw).expanduser().resolve()
    if not cert_file.is_file():
        raise GatewayActivationError("TLS_CERT_FILE_NOT_MATERIALIZED")
    if not key_file.is_file():
        raise GatewayActivationError("TLS_KEY_FILE_NOT_MATERIALIZED")

    bind_address = os.getenv(TLS_BIND_ENV, "0.0.0.0").strip() or "0.0.0.0"
    try:
        port = int(os.getenv(TLS_PORT_ENV, "443"))
    except ValueError as exc:
        raise GatewayActivationError("TLS_PORT_INVALID") from exc
    if not (1 <= port <= 65535):
        raise GatewayActivationError("TLS_PORT_INVALID")

    return {
        "cert_file": cert_file,
        "key_file": key_file,
        "bind_address": bind_address,
        "port": port,
    }


def build_deploy_command(tls_request: dict[str, Any] | None) -> tuple[list[str], str, bool]:
    if tls_request is None:
        return (
            [sys.executable, "scripts/stegdeploy_bootstrap.py", "deploy", "--health-url", "http://127.0.0.1:8000/health"],
            READINESS_URL,
            False,
        )
    port = int(tls_request["port"])
    return (
        [
            sys.executable,
            "scripts/stegdeploy_bootstrap.py",
            "deploy-tls",
            "--tls-cert-file",
            str(tls_request["cert_file"]),
            "--tls-key-file",
            str(tls_request["key_file"]),
            "--bind-address",
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


def _clean_env(decision: dict[str, Any]) -> dict[str, str]:
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
    for name in ("XDG_STATE_HOME", "XDG_CONFIG_HOME"):
        if os.getenv(name):
            env[name] = os.environ[name]
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
        llm_root / "scripts/stegdeploy_bootstrap.py",
        llm_root / "compose.stegdeploy.yaml",
        llm_root / "llm_adapter/deployed_gateway.py",
        llm_root / "llm_adapter/service_gateway_composed.py",
    ]
    if tls_request is not None:
        required.append(llm_root / "compose.stegdeploy.tls.yaml")
    missing = [str(path.relative_to(llm_root)) for path in required if not path.is_file()]
    if missing:
        raise GatewayActivationError("LLM_ADAPTER_STEGDEPLOY_SOURCE_INCOMPLETE:" + ",".join(missing))

    decision_path, decision = locate_decision(tvc_root)
    env = _clean_env(decision)

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

    return {
        "schema": "stegverse.healer.coinbase_stegdeploy_gateway_activation/v1",
        "state": "COMPLETE",
        "outcome": "LOCAL_SOVEREIGN_COINBASE_GATEWAY_TLS_READY" if tls_enabled else "LOCAL_SOVEREIGN_COINBASE_GATEWAY_READY",
        "source_head": source_head,
        "decision_ref": str(decision_path),
        "decision_id": decision["decision_id"],
        "readiness_url": readiness_url,
        "readiness": payload,
        "credential_authority": "TV/TVC",
        "credential_material_present": False,
        "github_token_required": False,
        "render_required": False,
        "tls_enabled": tls_enabled,
        "tls_locator_source": "TV_TVC_RUNTIME_FILE_PATHS" if tls_enabled else "NONE",
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
