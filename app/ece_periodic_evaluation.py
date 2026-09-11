#!/usr/bin/env python3
"""Run one bounded periodic ECE cycle from already-local canonical source.

The cycle is non-authorizing. It reads an optional resident observation bundle,
executes the canonical ECE evaluator, retains exact bytes through the canonical
Master Records custody/reconstruction source, prepares Healer finding intake,
and creates a Site-safe projection. All generated state is written under the
resident runtime root; source repositories remain read-only.
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


def execute_periodic_ece(roots: dict[str, Path], resident_root: Path, evaluated_at: str | None = None) -> dict[str, Any]:
    github_root = roots.get("StegVerse-Labs/.github")
    site_root = roots.get("StegVerse-Labs/Site")
    mr_root = roots.get("master-records/orchestration")
    healer_root = roots.get("StegVerse-Labs/StegVerse-Healer")
    missing = [name for name, value in {
        "StegVerse-Labs/.github": github_root,
        "StegVerse-Labs/Site": site_root,
        "master-records/orchestration": mr_root,
        "StegVerse-Labs/StegVerse-Healer": healer_root,
    }.items() if value is None]
    if missing:
        return {
            "state": "BLOCKED",
            "outcome": "ECE_REQUIRED_LOCAL_SOURCE_MISSING",
            "missing": sorted(missing),
            "authority_effect": "NONE",
        }

    assert github_root is not None and site_root is not None and mr_root is not None and healer_root is not None
    evaluator = github_root / "scripts" / "evaluate_ecosystem_continuity.py"
    registry = github_root / "data" / "ecosystem-continuity-registry.json"
    mr_ingest = mr_root / "scripts" / "ingest_ecosystem_continuity_evaluation.py"
    mr_reconstruct = mr_root / "scripts" / "reconstruct_ecosystem_continuity_evaluation.py"
    healer_intake = healer_root / "app" / "ece_finding_intake.py"
    site_projection = site_root / "scripts" / "project_ecosystem_continuity.py"
    for path, label in [
        (evaluator, "evaluator"), (registry, "registry"), (mr_ingest, "master_records_ingest"),
        (mr_reconstruct, "master_records_reconstruct"), (healer_intake, "healer_intake"),
        (site_projection, "site_projection"),
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

    with tempfile.TemporaryDirectory(prefix="stegverse-ece-") as td:
        temp_root = Path(td)
        if observation_bundle_present:
            observations = resident_observations
        else:
            observations = temp_root / "observations.empty.json"
            observations.write_text(json.dumps({"observations": []}, sort_keys=True) + "\n", encoding="utf-8")

        temp_evaluation = temp_root / "evaluation.json"
        evaluated_at = evaluated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        steps: list[dict[str, Any]] = []

        evaluation_run = _run([
            sys.executable, str(evaluator), "--registry", str(registry), "--observations", str(observations),
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
        "recovery_verified": False,
        "recovery_rule": "LATER_INDEPENDENT_ECE_PASS_REQUIRED",
        "authority_effect": "NONE",
        "execution": steps,
    }
    receipt_path = output_root / "cycle.latest.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt
