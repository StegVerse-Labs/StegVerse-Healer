# Healer StegFin Public Wallet Transport Observer Mirror Handoff

## Canonical state

```text
goal_id: HEALER-STEGFIN-PUBLIC-WALLET-TRANSPORT-001
originating_session_goal: make the StegFin trade path release-ready without Render or NON-TV/TVC credentials by proving the merged Site wallet-browser compatibility projection is actually public before current-phone USER_ONLY continuation
repository: StegVerse-Labs/StegVerse-Healer
branch: feat/stegfin-public-wallet-transport-observer-17
canonical_issue: StegVerse-Labs/StegVerse-Healer#17
source_site_owner: StegVerse-Labs/Site#388
source_site_handoff: StegVerse-Labs/Site/docs/STEGFIN_PHONE_PROJECTION_MIRROR_HANDOFF.md
source_site_observer: StegVerse-Labs/Site/scripts/check_stegfin_public_wallet_transport.py
source_site_observer_scheduler_path_commit: 6d7ad7a99091dc5c0ff134b5a2f4c79b49b60034
source_site_merge: ec8b5136ff9281ea37e861281f9428c7c283fbe4
expected_public_ui_blob: 114b3c39052d5b1622407080407259a0040a1369
canonical_scheduler: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
implementation_claim: COMPLETE_ON_BRANCH_PENDING_RELEASE
validation_claim: CLAIMED_FOR_VALIDATION
claim_created_at: 2026-08-18T01:40:00Z
claim_release_condition: fixed target and handler pass deterministic validation, merge to main, then existing sovereign scheduler emits COMPLETE with nested VERIFIED_PUBLICATION receipt for the exact expected UI blob
credential_authority: TV/TVC
credential_requirement: NONE
non_tv_tvc_secret_or_token_allowed: false
github_token_required: false
remote_checkout_required: false
artifact_custody_required: false
render_required: false
wallet_signing_and_broadcast: USER_ONLY
second_scheduler_or_heartbeat_allowed: false
state: IMPLEMENTED_PENDING_VALIDATION_RELEASE
```

## Collision and authority boundaries

This task reuses the existing sovereign Healer scheduler. No second scheduler, heartbeat, hosted runtime, GitHub-token path, wallet relay, wallet signing path, or broadcast path is introduced. The observer only performs public HTTPS verification of the Site participant and exact public UI blob. It grants no publication authority, transaction authority, wallet authority, settlement authority, or runtime authority.

## Implemented surfaces

```text
data/orchestrator_targets.json::StegVerse-Labs/Site/stegfin-public-wallet-transport-observer
  commit: 341b58d55a6abc5109268f1fb497439077843d3a
app/sovereign_scheduler.py::_execute_target fixed handler
  commit: efcde0f5b16981273a1ba5dd1c7ff6a7e9659ee0
tests/test_site_stegfin_public_wallet_transport_observer.py
  commit: d8e3dcea6677de85561d55361d2b5125c7c0dbe7
this handoff
```

The fixed target executes the released Site script `scripts/check_stegfin_public_wallet_transport.py` only against an already-materialized local Site root from `STEGVERSE_REPO_ROOTS_JSON`. No remote checkout is performed. The Site observer writes to an ephemeral receipt path supplied by the scheduler and accepts both the canonical `STEGVERSE_STEGFIN_PUBLICATION_REPORT` variable and the scheduler-local `STEGFIN_PUBLICATION_REPORT` alias; Site commit `6d7ad7a99091dc5c0ff134b5a2f4c79b49b60034` installed that deterministic path compatibility.

The scheduler handler refuses credential-bearing environments before invoking the observer. The refusal set includes GitHub credentials, TVC ephemeral GitHub token material, provider/master-records token paths, Cloudflare credentials, and Actions OIDC request material. Missing Site materialization and missing observer script fail closed.

## Required completion predicate

A scheduler outcome is COMPLETE only when all are true:

```text
Site root materialized locally
Site observer script present
credential-bearing environment absent
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

Any mismatch is BLOCKED. No current-phone activation, wallet signing, broadcast, publication authority, or settlement is inferred from this observer.

## Deterministic test contract

`tests/test_site_stegfin_public_wallet_transport_observer.py` covers:

1. fixed target is hourly on the existing scheduler;
2. missing observer script fails closed;
3. credential-bearing environment fails closed before execution;
4. exact `VERIFIED_PUBLICATION` + expected blob completes without authority;
5. wrong blob and nonzero observer execution block.

## Cross-repository continuation

```text
StegVerse-Labs/Site#388
-> this Healer fixed observer on SHWP-HEALER-SOVEREIGN-SCHEDULER-001
-> COMPLETE/VERIFIED_PUBLICATION receipt
-> StegVerse-Labs/stegfin-governance#81
-> current phone USER_ONLY: Safari fail-closed -> local wallet-browser reopen -> NEW PREPARE -> governed injected provider -> wallet review
```

The original local-model/runtime goal remains complete and machine-owned elsewhere; this task does not duplicate it.

## Validation commands

```text
python -m unittest -q tests.test_site_stegfin_public_wallet_transport_observer
python -m unittest -q
```

No validation PASS is claimed until an execution surface directly reports it.

## Completion accounting

```text
developed_files: 4/4
scaffolding_or_stubs: 0
missing_required_files: 0
validation: 0/2 pending execution
integration: 1/2 source surfaces integrated on branch; main release pending
goal_activation: 0/2 source release + machine receipt both required
session_consolidation: all unique session requirements durable in Site #388, StegFin #81, Healer #17, and this handoff
```

## Exact next actions

1. Open Healer #17 pull request from `feat/stegfin-public-wallet-transport-observer-17` to `main`.
2. Inspect Test Readiness/repository validation jobs and logs; require deterministic observer tests to execute and pass.
3. Merge only if the branch remains mergeable/current and validation evidence is sufficient.
4. Existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` executes the released fixed target against a materialized current Site root.
5. Accept publication proof only from a scheduler outcome `COMPLETE` whose nested receipt is `VERIFIED_PUBLICATION` for blob `114b3c39052d5b1622407080407259a0040a1369`.
6. Propagate that proof to Site #388 and StegFin #81, then release this implementation claim; current-phone proof remains USER_ONLY.

## Archive condition

This scoped implementation becomes archive-safe after source release and durable machine-owned continuation are proven. Current-phone signing/broadcast remains outside Healer and USER_ONLY. If source is released but the machine receipt is pending, continuation may be transferred to the existing scheduler only when its target, acceptance predicate, and downstream owner are all durably recorded.
