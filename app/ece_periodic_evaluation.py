#!/usr/bin/env python3
"""Run one bounded periodic ECE cycle through the installed SDK diagnostic processor.

The cycle is non-authorizing. It converts the canonical ECE registry plus optional
resident observations into a manifested ``ecosystem_diagnostic`` SDK request,
retains the exact SDK diagnostic-result bytes, translates only those results into
ECE observation input, executes the canonical ECE evaluator, retains exact ECE
bytes through Master Records custody/reconstruction, prepares Healer finding
intake, and creates a Site-safe projection. Source repositories remain read-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _run(command: list[str], cwd: Path, timeout: int = 120) -> dict[str, Any]:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
    }
    proc = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False, timeout=timeout)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"ECE_SOURCE_MISSING:{label}:{path}")


def _diagnostic_request(registry: dict[str, Any], observations: dict[str, Any], evaluated_at: str) -> dict[str, Any]:
    observation_map = {
        (row.get("component_id"), row.get("predicate_id")): row
        for row in observations.get("observations", [])
        if isinstance(row, dict)
    }
    tests: list[dict[str, Any]] = []
    for component in registry.get("components", []):
        component_id = component["component_id"]
        owner = component["authority_owner"]
        for predicate in component.get("predicates", []):
            predicate_id = predicate["predicate_id"]
            source = observation_map.get((component_id, predicate_id))
            observation = None
            if source is not None:
                observation = {
                    "state": source.get("state", "UNKNOWN"),
                    "observed_at": source.get("observed_at"),
                    "evidence_refs": list(source.get("evidence", [])),
                    "evidence_age_seconds": source.get("evidence_age_seconds"),
                    "detail": source.get("detail"),
                }
            tests.append({
                "test_id": f"ece:{component_id}:{predicate_id}",
                "component_id": component_id,
                "predicate_id": predicate_id,
                "authority_owner": owner,
                "observation": observation,
            })
    return {
        "schema": "stegverse.ecosystem-diagnostic-request.v1",
        "diagnostic_request_id": "ece-sdk-" + hashlib.sha256(
            f"{evaluated_at}:{_canonical_sha256(registry)}".encode("utf-8")
        ).hexdigest()[:24],
        "scope": "ecosystem",
        "mutation_permitted": False,
        "expected_evidence_fields": ["evidence_refs", "observed_at"],
        "tests": tests,
    }


def _ece_observations_from_diagnostic(result: dict[str, Any], diagnostic_sha256: str) -> dict[str, Any]:
    if result.get("schema") != "stegverse.ecosystem-diagnostic-result.v1":
        raise ValueError("SDK_DIAGNOSTIC_RESULT_SCHEMA_INVALID")
    if result.get("processing_capability") != "ecosystem_diagnostic":
        raise ValueError("SDK_DIAGNOSTIC_RESULT_CAPABILITY_DRIFT")
    if result.get("route_id") != "stegverse.route.ecosystem-diagnostic.v1":
        raise ValueError("SDK_DIAGNOSTIC_RESULT_ROUTE_DRIFT")
    if result.get("authority_effect") != "NONE_DIAGNOSTIC_ONLY":
        raise ValueError("SDK_DIAGNOSTIC_RESULT_AUTHORITY_DRIFT")
    if result.get("mutation_performed") is not False:
        raise ValueError("SDK_DIAGNOSTIC_RESULT_MUTATION_DRIFT")
    if result.get("continuity_state_present") is not False or "continuity_state" in result:
        raise ValueError("SDK_DIAGNOSTIC_RESULT_MUST_NOT_SUPPLY_CONTINUITY")

    envelope_ref = f"sdk-diagnostic-result-sha256:{diagnostic_sha256}"
    translated = []
    for row in result.get("results", []):
        if not isinstance(row, dict):
            raise ValueError("SDK_DIAGNOSTIC_RESULT_ROW_INVALID")
        evidence = list(row.get("evidence_refs") or [])
        if envelope_ref not in evidence:
            evidence.append(envelope_ref)
        translated.append({
            "component_id": row.get("component_id"),
            "predicate_id": row.get("predicate_id"),
            "state": row.get("observation_state"),
            "evidence": evidence,
            "evidence_age_seconds": row.get("evidence_age_seconds"),
            "detail": row.get("detail") or "",
            "sdk_diagnostic_test_id": row.get("test_id"),
        })
    return {"observations": translated}


def execute_periodic_ece(roots: dict[str, Path], resident_root: Path, evaluated_at: str | None = None) -> dict[str, Any]:
    github_root = roots.get("StegVerse-Labs/.github")
    site_root = roots.get("StegVerse-Labs/Site")
    mr_root = roots.get("master-records/orchestration")
    healer_root = roots.get("StegVerse-Labs/StegVerse-Healer")
    sdk_root = roots.get("StegVerse-org/StegVerse-SDK")
    missing = [name for name, value in {
        "StegVerse-Labs/.github": github_root,
        "StegVerse-Labs/Site": site_root,
        "master-records/orchestration": mr_root,
        "StegVerse-Labs/StegVerse-Healer": healer_root,
        "StegVerse-org/StegVerse-SDK": sdk_root,
    }.items() if value is None]
    if missing:
        return {
            "state": "BLOCKED",
            "outcome": "ECE_REQUIRED_LOCAL_SOURCE_MISSING",
            "missing": sorted(missing),
            "authority_effect": "NONE",
        }

    assert github_root is not None and site_root is not None and mr_root is not None and healer_root is not None and sdk_root is not None
    evaluator = github_root / "scripts" / "evaluate_ecosystem_continuity.py"
    registry_path = github_root / "data" / "ecosystem-continuity-registry.json"
    sdk_builder = sdk_root / "stegverse" / "manifest_builder.py"
    sdk_runtime = sdk_root / "stegverse" / "ecosystem_diagnostic_runtime.py"
    sdk_cli = sdk_root / "stegverse" / "ecosystem_diagnostic_cli.py"
    mr_ingest = mr_root / "scripts" / "ingest_ecosystem_continuity_evaluation.py"
    mr_reconstruct = mr_root / "scripts" / "reconstruct_ecosystem_continuity_evaluation.py"
    healer_intake = healer_root / "app" / "ece_finding_intake.py"
    site_projection = site_root / "scripts" / "project_ecosystem_continuity.py"
    for path, label in [
        (evaluator, "evaluator"), (registry_path, "registry"),
        (sdk_builder, "sdk_manifest_builder"), (sdk_runtime, "sdk_diagnostic_runtime"), (sdk_cli, "sdk_diagnostic_cli"),
        (mr_ingest, "master_records_ingest"), (mr_reconstruct, "master_records_reconstruct"),
        (healer_intake, "healer_intake"), (site_projection, "site_projection"),
    ]:
        _require_file(path, label)

    resident_root = resident_root.expanduser().resolve()
    output_root = resident_root / "receipts" / "ecosystem-continuity"
    custody_root = resident_root / "master-records" / "ecosystem-continuity"
    output_root.mkdir(parents=True, exist_ok=True)
    custody_root.mkdir(parents=True, exist_ok=True)

    explicit_observations = os.getenv("STEGVERSE_ECE_OBSERVATIONS", "").strip()
    resident_observations = Path(explicit_observations).expanduser().resolve() if explicit_observations else output_root / "observations.latest.json"
    observation_bundle_present = resident_observations.is_file()
    evaluated_at = evaluated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="stegverse-ece-sdk-") as td:
        temp_root = Path(td)
        if observation_bundle_present:
            source_observations = json.loads(resident_observations.read_text(encoding="utf-8"))
        else:
            source_observations = {"observations": []}

        diagnostic_request = _diagnostic_request(registry, source_observations, evaluated_at)
        request_path = temp_root / "diagnostic-request.json"
        request_path.write_text(json.dumps(diagnostic_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        source_payload = {
            "schema": "stegverse.ece-diagnostic-cycle-source.v1",
            "evaluated_at": evaluated_at,
            "registry_sha256": _canonical_sha256(registry),
            "observation_bundle_present": observation_bundle_present,
            "observation_bundle_sha256": _canonical_sha256(source_observations),
        }
        payload_path = temp_root / "diagnostic-source.json"
        payload_path.write_text(json.dumps(source_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        manifest_path = temp_root / "diagnostic-manifest.json"
        diagnostic_result_temp = temp_root / "diagnostic-result.json"
        steps: list[dict[str, Any]] = []

        build_run = _run([
            sys.executable, "-m", "stegverse.manifest_builder", "build",
            "--input", str(payload_path), "--processor-request", str(request_path),
            "--process", "ecosystem_diagnostic", "--source-framework", "StegVerse-Healer",
            "--source-output-id", diagnostic_request["diagnostic_request_id"],
            "--data-class", "stegverse.ece-diagnostic-cycle-source.v1",
            "--return-depth", "result+evidence", "--created-at", evaluated_at,
            "--output", str(manifest_path),
        ], sdk_root)
        steps.append(build_run)
        if build_run["returncode"] != 0 or not manifest_path.is_file():
            return {"state":"BLOCKED","outcome":"ECE_SDK_DIAGNOSTIC_MANIFEST_BUILD_FAILED","execution":steps,"authority_effect":"NONE"}

        sdk_run = _run([
            sys.executable, "-m", "stegverse.ecosystem_diagnostic_cli",
            "--manifest", str(manifest_path), "--output", str(diagnostic_result_temp),
        ], sdk_root)
        steps.append(sdk_run)
        if sdk_run["returncode"] != 0 or not diagnostic_result_temp.is_file():
            return {"state":"BLOCKED","outcome":"ECE_SDK_DIAGNOSTIC_EXECUTION_FAILED","execution":steps,"authority_effect":"NONE"}

        diagnostic_raw = diagnostic_result_temp.read_bytes()
        diagnostic_sha = hashlib.sha256(diagnostic_raw).hexdigest()
        diagnostic_id = "sdkdiag_" + diagnostic_sha[:24]
        exact_diagnostic = output_root / f"{diagnostic_id}.result.json"
        latest_diagnostic = output_root / "sdk-diagnostic-result.latest.json"
        if exact_diagnostic.exists() and exact_diagnostic.read_bytes() != diagnostic_raw:
            return {"state":"BLOCKED","outcome":"ECE_SDK_DIAGNOSTIC_IDENTITY_CONFLICT","diagnostic_result_id":diagnostic_id,"authority_effect":"NONE"}
        exact_diagnostic.write_bytes(diagnostic_raw)
        latest_diagnostic.write_bytes(diagnostic_raw)
        diagnostic_result = json.loads(diagnostic_raw)

        try:
            ece_observation_bundle = _ece_observations_from_diagnostic(diagnostic_result, diagnostic_sha)
        except ValueError as exc:
            return {"state":"BLOCKED","outcome":str(exc),"diagnostic_result_id":diagnostic_id,"authority_effect":"NONE"}
        translated_observations = temp_root / "ece-observations-from-sdk.json"
        translated_observations.write_text(json.dumps(ece_observation_bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        temp_evaluation = temp_root / "evaluation.json"
        evaluation_run = _run([
            sys.executable, str(evaluator), "--registry", str(registry_path), "--observations", str(translated_observations),
            "--output", str(temp_evaluation), "--evaluated-at", evaluated_at,
        ], github_root)
        steps.append(evaluation_run)
        if evaluation_run["returncode"] != 0 or not temp_evaluation.is_file():
            return {"state":"BLOCKED","outcome":"ECE_EVALUATION_FAILED","execution":steps,"authority_effect":"NONE"}

        evaluation = json.loads(temp_evaluation.read_text(encoding="utf-8"))
        if evaluation.get("authority_effect") != "NONE_DIAGNOSTIC_ONLY":
            return {"state":"BLOCKED","outcome":"ECE_EVALUATION_AUTHORITY_DRIFT","execution":steps,"authority_effect":"NONE"}
        evaluation_id = str(evaluation.get("evaluation_id", ""))
        if not evaluation_id.startswith("ece_"):
            return {"state":"BLOCKED","outcome":"ECE_EVALUATION_ID_INVALID","execution":steps,"authority_effect":"NONE"}

        exact_eval = output_root / f"{evaluation_id}.evaluation.json"
        latest_eval = output_root / "evaluation.latest.json"
        raw = temp_evaluation.read_bytes()
        if exact_eval.exists() and exact_eval.read_bytes() != raw:
            return {"state":"BLOCKED","outcome":"ECE_RESIDENT_IDENTITY_CONFLICT","evaluation_id":evaluation_id,"authority_effect":"NONE"}
        exact_eval.write_bytes(raw)
        latest_eval.write_bytes(raw)

        custody_run = _run([
            sys.executable, str(mr_ingest), "--evaluation", str(exact_eval), "--custody-root", str(custody_root),
        ], mr_root)
        steps.append(custody_run)
        if custody_run["returncode"] != 0:
            return {"state":"BLOCKED","outcome":"ECE_MASTER_RECORDS_CUSTODY_FAILED","evaluation_id":evaluation_id,"execution":steps,"authority_effect":"NONE"}
        try:
            custody_result = json.loads(custody_run["stdout_tail"].strip().splitlines()[-1])
        except Exception:
            return {"state":"BLOCKED","outcome":"ECE_MASTER_RECORDS_CUSTODY_RECEIPT_INVALID","evaluation_id":evaluation_id,"execution":steps,"authority_effect":"NONE"}

        custody_ref = Path(str(custody_result.get("custody_ref", "")))
        reconstructed = temp_root / "reconstructed.json"
        reconstruction_run = _run([
            sys.executable, str(mr_reconstruct), "--record", str(custody_ref), "--custody-root", str(custody_root), "--output", str(reconstructed),
        ], mr_root)
        steps.append(reconstruction_run)
        if reconstruction_run["returncode"] != 0 or not reconstructed.is_file() or reconstructed.read_bytes() != raw:
            return {"state":"BLOCKED","outcome":"ECE_MASTER_RECORDS_RECONSTRUCTION_FAILED","evaluation_id":evaluation_id,"execution":steps,"authority_effect":"NONE"}

        intake_path = output_root / "healer-intake.latest.json"
        intake_run = _run([sys.executable, str(healer_intake), "--input", str(exact_eval), "--output", str(intake_path)], healer_root)
        steps.append(intake_run)
        if intake_run["returncode"] != 0 or not intake_path.is_file():
            return {"state":"BLOCKED","outcome":"ECE_HEALER_INTAKE_FAILED","evaluation_id":evaluation_id,"execution":steps,"authority_effect":"NONE"}

        projection_path = output_root / "site-projection.latest.json"
        projection_run = _run([sys.executable, str(site_projection), "--input", str(exact_eval), "--output", str(projection_path)], site_root)
        steps.append(projection_run)
        if projection_run["returncode"] != 0 or not projection_path.is_file():
            return {"state":"BLOCKED","outcome":"ECE_SITE_PROJECTION_FAILED","evaluation_id":evaluation_id,"execution":steps,"authority_effect":"NONE"}

    receipt = {
        "schema": "stegverse.healer-ecosystem-continuity-cycle/v1",
        "state": "COMPLETE",
        "evaluation_id": evaluation_id,
        "evaluated_at": evaluated_at,
        "continuity_state": evaluation.get("continuity_state"),
        "observation_bundle_present": observation_bundle_present,
        "observation_source": str(resident_observations) if observation_bundle_present else None,
        "sdk_diagnostic_request_id": diagnostic_request["diagnostic_request_id"],
        "sdk_diagnostic_result_id": diagnostic_id,
        "sdk_diagnostic_result_ref": str(exact_diagnostic),
        "sdk_diagnostic_result_sha256": diagnostic_sha,
        "sdk_diagnostic_result_bound_into_ece": True,
        "evaluation_ref": str(exact_eval),
        "evaluation_sha256": _sha256(exact_eval),
        "custody_ref": str(custody_ref),
        "custody_sha256": _sha256(custody_ref),
        "healer_intake_ref": str(intake_path),
        "healer_intake_sha256": _sha256(intake_path),
        "site_projection_ref": str(projection_path),
        "site_projection_sha256": _sha256(projection_path),
        "source_repository_writeback": False,
        "github_token_required": False,
        "second_scheduler_created": False,
        "sdk_diagnostic_mutation_performed": False,
        "sdk_diagnostic_continuity_authority": False,
        "recovery_verified": False,
        "recovery_rule": "LATER_INDEPENDENT_ECE_PASS_REQUIRED",
        "authority_effect": "NONE",
        "execution": steps,
    }
    receipt_path = output_root / "cycle.latest.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt
