# Site Executive Rhetoric Ledger Sovereign Sync Mirror Handoff

## Canonical state

```text
goal: HEALER-SITE-ERL-SOVEREIGN-SYNC-039
repository: StegVerse-Labs/StegVerse-Healer
canonical_issue: #39
source_pull_request: #40
validated_head: aca5b7871e2720b0d56757e33fc2a22c10291136
merge_commit: ff3d9985b773d91dce0d90351a7a8a04a499c59b
credential_authority: TV/TVC
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
source_state: COMPLETE_RELEASED
live_execution_state: MACHINE_OWNED_PENDING_SCHEDULER_RECEIPT
site_github_workflow_retirement_authorized: false
```

## Installed fixed target

`data/orchestrator_targets.json` now contains one enabled fixed target:

```text
repo: StegVerse-Labs/Site
workflow: executive-rhetoric-ledger-local-sync
source repository: StegVerse-Labs/Executive_Rhetoric_Ledger
source path: publication/compendium.json
destination path: public/data/executive-rhetoric-ledger/compendium.json
acknowledgment path: receipts/executive-rhetoric-ledger-ack.json
run hour: 14 UTC
scheduler: existing SHWP-HEALER-SOVEREIGN-SCHEDULER-001 only
```

No second scheduler or heartbeat was created.

## Fixed local handler

`app/site_erl_sync.py`:

- refuses GitHub token/PAT credential environments;
- requires already-materialized local Site and Executive_Rhetoric_Ledger roots;
- refuses missing or malformed source data;
- validates the source compendium as JSON;
- copies the exact source bytes into the Site mirror path;
- verifies SHA-256 source/destination identity;
- writes a destination-owned acknowledgment receipt;
- records that source self-acknowledgment is not allowed;
- requires no remote checkout or artifact custody;
- grants no GitHub writeback, runtime, provider, publication, or activation authority.

`app/sovereign_scheduler.py` adds only the fixed dispatch binding for `executive-rhetoric-ledger-local-sync`; existing handlers are unchanged.

## Deterministic validation

Test Readiness run `32670203077`, job `97269769966`: SUCCESS on exact head `aca5b7871e2720b0d56757e33fc2a22c10291136`.

The full deterministic Healer test suite passed, including six focused `tests/test_site_erl_sync.py` cases covering:

- fixed daily target/cadence;
- exact byte and SHA-256 mirror identity;
- destination-owned acknowledgment semantics;
- missing source root failure;
- missing source file failure;
- malformed JSON failure without destination/ack creation;
- GitHub credential fail-closed behavior.

Validation also passed the repository smoke test, failure-mailbox benchmark, and validation-only authority boundary.

## Activation boundary

Source and CI are not live scheduler execution.

Canonical executable handoff:

`StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`

Current observed state: `HANDOFF_READY` with authorized heartbeat carrier and a required checkpoint at:

`StegVerse-Labs/.github/receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`

At this handoff revision that required scheduler receipt is absent. Therefore the new ERL target has **not** been proven in live sovereign execution.

## Site retirement gate

Do not remove or disable `StegVerse-Labs/Site/.github/workflows/sync-executive-rhetoric-ledger.yml` until a live scheduler receipt proves the fixed `executive-rhetoric-ledger-local-sync` target executed successfully against materialized Site + Executive_Rhetoric_Ledger roots and produced a PASS destination acknowledgment.

Only after that physical execution proof exists may Site #268:

1. admit the exact-current Site retirement claim;
2. remove the daily schedule and GitHub-token/PR mutation carrier;
3. preserve any intentionally required manual/source validation semantics;
4. validate current Site claim/orchestration gates;
5. merge and record the retirement evidence.

Until that receipt exists, leaving the current Site workflow in place is required continuity preservation, not a failure to complete the source migration.

## Authority boundary

```text
non_tv_tvc_secret_or_token_used: false
github_token_runtime_authority: NONE
remote_checkout_required: false
artifact_custody_required: false
repository_writeback_authority: false
runtime_authority: false
provider_authority: false
publication_authority: false
activation_authority: false
render_required: false
```

Issue creation, PR merge, Test Readiness success, or this handoff does not satisfy live scheduler activation.
