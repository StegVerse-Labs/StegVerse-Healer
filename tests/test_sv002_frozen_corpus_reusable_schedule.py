from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "SHWP-SV002-FROZEN-CORPUS-MATERIALIZATION-001"
COSV = "50000000107001"
RT_ID = "RT-TVC-PRIMARY-RUNTIME-BINDING-001"


def test_sv002_frozen_corpus_uses_existing_neutral_reusable_scheduler() -> None:
    schedule = json.loads((ROOT / "data" / "reusable_task_schedule.json").read_text(encoding="utf-8"))
    assert schedule["schema"] == "stegverse.reusable-task-schedule/v1"
    rows = [row for row in schedule["tasks"] if row.get("tracking_task_id") == TASK_ID]
    assert len(rows) == 1
    row = rows[0]
    assert row["reusable_task_id"] == RT_ID
    assert row["cosv_task_vector"] == COSV
    assert row["repository"] == "StegVerse-Labs/.github"
    assert row["enabled"] is True
    assert row["run_hours_utc"] == list(range(24))
    assert row["retry_interval_minutes"] == 15
    assert row["max_attempts_per_slot"] == 4
    params = row["parameters"]
    assert params["canonical_tvc_source"].startswith("already-local")
    assert params["binder_task_ref"] == "StegVerse-Labs/TVC:tasks/TVC-PRIMARY-RUNTIME-BINDER-005.json"
    assert params["activation_delivery_task_ref"] == "StegVerse-Labs/TVC:tasks/TVC-PRIMARY-RUNTIME-ACTIVATION-DELIVERY-006.json"
    assert params["vault_broker_socket"] == "/run/stegverse/vault-broker.sock"
    assert params["provider_operation_surface"] == "https://tvc.stegverse.org/v1/provider-operation"
    assert params["activation_authority_declaration"] == "TV/TVC"
