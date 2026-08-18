# Healer StegFin Public Wallet Transport Observer Mirror Handoff

## Canonical state

```text
goal_id: HEALER-STEGFIN-PUBLIC-WALLET-TRANSPORT-001
originating_session_goal: make the StegFin trade path release-ready without Render or NON-TV/TVC credentials by proving the merged Site wallet-browser compatibility projection is actually public before current-phone USER_ONLY continuation
repository: StegVerse-Labs/StegVerse-Healer
branch: main
source_site_owner: StegVerse-Labs/Site#388
source_site_handoff: StegVerse-Labs/Site/docs/STEGFIN_PHONE_PROJECTION_MIRROR_HANDOFF.md
source_site_observer: StegVerse-Labs/Site/scripts/check_stegfin_public_wallet_transport.py
source_site_merge: ec8b5136ff9281ea37e861281f9428c7c283fbe4
expected_public_ui_blob: 114b3c39052d5b1622407080407259a0040a1369
canonical_scheduler: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
implementation_claim: CLAIMED_FOR_IMPLEMENTATION
validation_claim: CLAIMED_FOR_VALIDATION
claim_created_at: 2026-08-18T01:40:00Z
claim_release_condition: fixed target executes the Site publication observer through the existing sovereign scheduler and emits COMPLETE with nested VERIFIED_PUBLICATION receipt for the exact expected UI blob
credential_authority: TV/TVC
credential_requirement: NONE
non_tv_tvc_secret_or_token_allowed: false
github_token_required: false
remote_checkout_required: false
artifact_custody_required: false
render_required: false
wallet_signing_and_broadcast: USER_ONLY
second_scheduler_or_heartbeat_allowed: false
state: ACTIVE_IMPLEMENTATION
```

## Collision and authority boundaries

This task must reuse the existing sovereign Healer scheduler. Do not create a second scheduler, heartbeat, hosted runtime, GitHub-token path, wallet relay, wallet signing path, or broadcast path. The observer only performs public HTTPS verification of the Site participant and exact public UI blob. It grants no publication authority, transaction authority, wallet authority, settlement authority, or runtime authority.

## Required implementation

```text
data/orchestrator_targets.json::StegVerse-Labs/Site/stegfin-public-wallet-transport-observer
app/sovereign_scheduler.py::_execute_target fixed handler
tests/test_site_stegfin_public_wallet_transport_observer.py
this handoff
```

The fixed target must execute the already-released Site script `scripts/check_stegfin_public_wallet_transport.py` only against an already-materialized local Site root from `STEGVERSE_REPO_ROOTS_JSON`. No remote checkout is allowed. The Site script itself performs credential-free public HTTPS observation of `stegverse.org` and writes its result to an ephemeral/local receipt path supplied by Healer.

## Required completion predicate

A scheduler outcome is COMPLETE only when all are true:

```text
Site root materialized locally
Site observer script present
observer process exits 0
nested receipt state == VERIFIED_PUBLICATION
nested publication_proven == true
nested observed_ui_blob == 114b3c39052d5b1622407080407259a0040a1369
nested credential_authority == TV/TVC
nested credential_requirement == NONE
nested non_tv_tvc_secret_or_token_used == false
nested github_token_required == false
nested render_required == false
nested authority_effect == false
```

Any mismatch is BLOCKED. No current-phone activation is inferred from this observer.

## Cross-repository continuation

```text
StegVerse-Labs/Site#388
-> this Healer fixed observer on SHWP-HEALER-SOVEREIGN-SCHEDULER-001
-> COMPLETE/VERIFIED_PUBLICATION receipt
-> StegVerse-Labs/stegfin-governance#81
-> current phone USER_ONLY: Safari fail-closed -> local wallet-browser reopen -> NEW PREPARE -> governed injected provider -> wallet review
```

## Validation commands

```text
python -m unittest -q tests.test_site_stegfin_public_wallet_transport_observer
python -m unittest -q
```

## Completion accounting

```text
developed_files: 1/4
validation: 0/2
integration: 0/2
goal_activation: 0/2
session_consolidation: all session requirements already durable in Site #388 and StegFin #81; this handoff owns only the noncompeting sovereign publication-observer carrier
```

## Archive condition

This scoped task is archive-safe only after the fixed target, scheduler handler, deterministic tests, and release evidence are complete or continuation is durably transferred to the existing machine-owned scheduler. Live current-phone signing/broadcast remains outside Healer and USER_ONLY.
