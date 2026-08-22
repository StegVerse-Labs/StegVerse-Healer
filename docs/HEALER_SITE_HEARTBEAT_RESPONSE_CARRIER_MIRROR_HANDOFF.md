# Healer Site Heartbeat Response Carrier Mirror Handoff

Updated: 2026-08-22

## Identity

```text
goal_id: HEALER-SITE-HEARTBEAT-RESPONSE-CARRIER-035
repository: StegVerse-Labs/StegVerse-Healer
issue: #35
branch: claim/site-heartbeat-response-sovereign-carrier-35
upstream_heartbeat_owner: StegVerse-Labs/Site#234
upstream_cost_migration: StegVerse-Labs/Site#411
scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_token_runtime_authority: NONE
render_required: false
state: SOURCE_IMPLEMENTED_VALIDATION_PENDING
```

This task supplies a bounded local carrier to the existing sovereign Healer scheduler. It does not acquire heartbeat product authority from Site #234 and does not authorize Site #411 to remove hosted mutating schedules until successful sovereign execution and durable persistence/propagation evidence are consumed.

## Implemented source

- `data/orchestrator_targets.json` binds fixed target `StegVerse-Labs/Site/heartbeat-response-sovereign-carrier` on the existing scheduler.
- `app/sovereign_scheduler.py` executes the Site self-node apply path, collector apply path, then semantic network validation against a locally materialized Site checkout.
- `tests/test_site_heartbeat_response_carrier.py` proves target binding, credential refusal, missing-source fail-closed behavior, successful local execution receipt semantics, and collector-failure containment.

## Carrier contract

```text
local dependency: STEGVERSE_REPO_ROOTS_JSON::StegVerse-Labs/Site
commands:
  - python scripts/process_heartbeat_response_node.py --apply
  - python scripts/collect_heartbeat_response_receipts.py --apply
  - python scripts/check_heartbeat_response_network.py
source head: git rev-parse HEAD required
local state mutation: allowed inside materialized Site root
canonical Git writeback authority: false
remote checkout required: false
artifact custody required: false
github token required: false
runtime authority: false
activation authority: false
publication authority: false
custody authority: false
release authority: false
```

A successful carrier receipt is `stegverse.healer.site_heartbeat_response_carrier_receipt/v0.1` and records the exact Site source head and executed commands. The persistence boundary remains `LOCAL_MATERIALIZED_SITE_ONLY_UNTIL_SEPARATELY_ADMITTED_PROPAGATION`.

## Collision boundaries

- Site #234 remains canonical heartbeat-response semantics/transition owner.
- Site #411 remains the hosted Actions migration owner.
- No second scheduler or heartbeat may be introduced.
- No GitHub-token, NON-TV/TVC secret/token, Render, hosted artifact custody, or remote checkout may become runtime authority.
- Source implementation and hosted validation do not prove ordinary sovereign scheduler execution.
- Site hourly self-node/collector workflows must not be retired until Site consumes a successful sovereign carrier receipt and proves required durable state persistence/propagation.

## Validation and completion gate

Pending strongest available validation on the exact branch/head. Completion requires:

1. deterministic unit tests pass on the exact source head;
2. repository validation passes without credential authority expansion;
3. source merges to `main`;
4. ordinary `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` execution produces a successful carrier receipt against current locally materialized Site;
5. Site #234/#411 consumes that receipt and proves the required persistence/propagation path;
6. only then may the hosted hourly schedules be removed/narrowed and validated on Site.

Until steps 4-6 occur, the migration is not activated or complete.
