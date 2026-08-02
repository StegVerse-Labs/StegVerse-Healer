#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_SESSION_STATES = {
    "ACTIVE_UNIQUE_WORK_REMAINS",
    "ACTIVE_DISTINCT_SUPPORT_ROLE",
    "BLOCKED_RETAIN_TEMPORARILY",
    "MERGED_INTO_CANONICAL_WORKSTREAM",
    "COMPLETE_ARCHIVE",
}
ALLOWED_CLAIM_STATES = {
    "UNCLAIMED",
    "CLAIMED_FOR_IMPLEMENTATION",
    "CLAIMED_FOR_VALIDATION",
    "CLAIMED_FOR_INTEGRATION",
    "MACHINE_OWNED",
    "BLOCKED",
    "COMPLETE",
    "SUPERSEDED",
    "MERGED_INTO_CANONICAL_WORKSTREAM",
}
REQUIRED_ITEM_FIELDS = {
    "task_id",
    "originating_goal",
    "destination",
    "branch",
    "location",
    "owner",
    "claim_state",
    "completion_state",
    "validation_state",
    "integration_state",
    "archival_dependency",
    "evidence",
    "next_action",
}


def fail(message: str) -> None:
    raise SystemExit(f"session inventory invalid: {message}")


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/session_consolidation/single_scheduler_session_inventory.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("schema") != "stegverse.session-execution-inventory.v1":
        fail("unexpected schema")
    if data.get("session_state") not in ALLOWED_SESSION_STATES:
        fail("invalid session_state")
    if not data.get("canonical_continuation"):
        fail("canonical_continuation is required")

    claims = data.get("claims")
    inventory = data.get("inventory")
    if not isinstance(claims, list) or not claims:
        fail("claims must be a non-empty list")
    if not isinstance(inventory, list) or not inventory:
        fail("inventory must be a non-empty list")

    claim_ids: set[str] = set()
    for claim in claims:
        missing = {"task_id", "state", "owner", "location", "release_condition"} - set(claim)
        if missing:
            fail(f"claim missing fields: {sorted(missing)}")
        if claim["state"] not in ALLOWED_CLAIM_STATES:
            fail(f"invalid claim state for {claim['task_id']}")
        if claim["task_id"] in claim_ids:
            fail(f"duplicate claim task_id: {claim['task_id']}")
        claim_ids.add(claim["task_id"])

    inventory_ids: set[str] = set()
    for item in inventory:
        missing = REQUIRED_ITEM_FIELDS - set(item)
        if missing:
            fail(f"inventory item missing fields: {sorted(missing)}")
        if item["claim_state"] not in ALLOWED_CLAIM_STATES:
            fail(f"invalid inventory claim state for {item['task_id']}")
        if item["task_id"] in inventory_ids:
            fail(f"duplicate inventory task_id: {item['task_id']}")
        if not item["location"] or not item["owner"] or not item["next_action"]:
            fail(f"empty durable owner/location/action for {item['task_id']}")
        inventory_ids.add(item["task_id"])

    archival = data.get("archival", {})
    required_archival = {"unique_context_transferred", "session_claim_released", "archive_ready", "canonical_location", "deletion_loss_test"}
    missing_archival = required_archival - set(archival)
    if missing_archival:
        fail(f"archival missing fields: {sorted(missing_archival)}")

    if archival["archive_ready"]:
        if not archival["unique_context_transferred"] or not archival["session_claim_released"]:
            fail("archive_ready requires transferred context and released session claim")
        if data["session_state"] not in {"MERGED_INTO_CANONICAL_WORKSTREAM", "COMPLETE_ARCHIVE"}:
            fail("archive_ready requires merged or complete session state")
        if any(item.get("archival_dependency") for item in inventory):
            fail("archive_ready conflicts with an inventory archival dependency")

    print(
        json.dumps(
            {
                "result": "PASS",
                "inventory": str(path),
                "claims": len(claims),
                "tasks": len(inventory),
                "session_state": data["session_state"],
                "archive_ready": archival["archive_ready"],
                "canonical_location": archival["canonical_location"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
