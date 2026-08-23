from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

FORBIDDEN_CREDENTIALS = (
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_PAT",
    "HEALER_GH_TOKEN",
    "HEALER_PAT",
    "GH_STEGVERSE_AI_TOKEN",
    "STEGVERSE_CROSS_REPO_READ_TOKEN",
)


def _blocked(base: dict[str, Any], outcome: str, **extra: Any) -> dict[str, Any]:
    return {**base, "state": "BLOCKED", "outcome": outcome, **extra}


def execute_site_erl_sync(
    target: dict[str, Any],
    roots: dict[str, Path],
    base: dict[str, Any],
) -> dict[str, Any]:
    present = [name for name in FORBIDDEN_CREDENTIALS if os.getenv(name)]
    if present:
        return _blocked(base, "SITE_ERL_SYNC_FORBIDDEN_CREDENTIAL_ENV", forbidden=sorted(present))

    site_root = roots.get("StegVerse-Labs/Site")
    source_repo = str(target.get("source_repository", "StegVerse-Labs/Executive_Rhetoric_Ledger"))
    source_root = roots.get(source_repo)
    if site_root is None:
        return _blocked(base, "SITE_ERL_SYNC_SITE_ROOT_NOT_MATERIALIZED")
    if source_root is None:
        return _blocked(base, "SITE_ERL_SYNC_SOURCE_ROOT_NOT_MATERIALIZED", source_repository=source_repo)

    source_rel = Path(str(target.get("source_path", "publication/compendium.json")))
    destination_rel = Path(str(target.get("destination_path", "public/data/executive-rhetoric-ledger/compendium.json")))
    acknowledgment_rel = Path(str(target.get("acknowledgment_path", "receipts/executive-rhetoric-ledger-ack.json")))
    source_path = source_root / source_rel
    destination_path = site_root / destination_rel
    acknowledgment_path = site_root / acknowledgment_rel

    if not source_path.is_file():
        return _blocked(base, "SITE_ERL_SYNC_SOURCE_MISSING", source_path=str(source_rel))

    try:
        source_bytes = source_path.read_bytes()
        source_json = json.loads(source_bytes.decode("utf-8"))
    except Exception as exc:
        return _blocked(base, "SITE_ERL_SYNC_SOURCE_INVALID_JSON", source_path=str(source_rel), error=str(exc))
    if not isinstance(source_json, (dict, list)):
        return _blocked(base, "SITE_ERL_SYNC_SOURCE_INVALID_SHAPE", source_path=str(source_rel))

    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    destination_path.write_bytes(source_bytes)
    destination_bytes = destination_path.read_bytes()
    destination_sha256 = hashlib.sha256(destination_bytes).hexdigest()
    byte_equal = destination_bytes == source_bytes
    if not byte_equal or destination_sha256 != source_sha256:
        return _blocked(
            base,
            "SITE_ERL_SYNC_DESTINATION_IDENTITY_MISMATCH",
            source_sha256=source_sha256,
            destination_sha256=destination_sha256,
        )

    receipt = {
        "schema": "stegverse.healer.site_erl_sync_receipt/v0.1",
        "state": "PASS",
        "canonical_owner": "StegVerse-Labs/StegVerse-Healer#39",
        "source_repository": source_repo,
        "source_path": str(source_rel),
        "source_sha256": source_sha256,
        "destination_repository": "StegVerse-Labs/Site",
        "destination_path": str(destination_rel),
        "destination_sha256": destination_sha256,
        "byte_equal": True,
        "acknowledgment_owned_by_destination": True,
        "source_self_acknowledgment_allowed": False,
        "credential_authority": "TV/TVC",
        "github_token_required": False,
        "remote_checkout_required": False,
        "artifact_custody_required": False,
        "repository_writeback_authority": False,
        "local_materialization_mutation": True,
        "runtime_authority": False,
        "publication_authority": False,
        "activation_authority": False,
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    acknowledgment_path.parent.mkdir(parents=True, exist_ok=True)
    acknowledgment_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        **base,
        "state": "COMPLETE",
        "outcome": "SOVEREIGN_LOCAL_SITE_ERL_SYNC",
        "receipt": receipt,
    }
