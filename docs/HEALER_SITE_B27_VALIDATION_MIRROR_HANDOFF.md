# Healer Site B27 Sovereign Validation Mirror Handoff

This is a scoped, noncompeting child handoff for `HEALER-SITE-B27-SOVEREIGN-VALIDATION-001`. The repository-wide canonical handoff remains `docs/HEALER_MIRROR_HANDOFF.md`.

## Canonical state

```text
goal_id: HEALER-SITE-B27-SOVEREIGN-VALIDATION-001
originating_goal: provide an equal-or-stronger StegVerse-native validation path for Site B27 while GitHub-hosted validation is billing-blocked
repository: StegVerse-Labs/StegVerse-Healer
canonical_branch: main
canonical_issue: StegVerse-Labs/StegVerse-Healer#14
source_site_owner: StegVerse-Labs/Site#268
source_site_task: data/tasks/SITE-ACTIONS-COST-CONTAINMENT-001-B27.json
source_site_pr: StegVerse-Labs/Site#387
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_token_required: false
remote_checkout_required: false
github_artifact_custody_required: false
render_required: false
github_actions_production_role: NONE
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
second_scheduler_or_heartbeat_allowed: false
wallet_signing_and_broadcast: USER_ONLY
implementation_claim: COMPLETE_RELEASED
validation_claim: COMPLETE_RELEASED_SOURCE_CARRIER
claim_created_at: 2026-08-18T00:52:19Z
claim_released_by: PR #15 merge e68fc136598af641481152176dc41725e1663fe0
state: SOURCE_CONTROL_RELEASED_LIVE_EXECUTION_MACHINE_OWNED
```

## Authoritative surfaces

- `data/orchestrator_targets.json::StegVerse-Labs/Site/site-b27-native-validation`
- `app/sovereign_scheduler.py::_execute_target`
- `tests/test_site_b27_native_validation.py`
- `docs/HEALER_SITE_B27_VALIDATION_MIRROR_HANDOFF.md`
- issue `StegVerse-Labs/StegVerse-Healer#14`
- Site continuation `StegVerse-Labs/Site#268`, Site PR #387, and Site `data/tasks/SITE-ACTIONS-COST-CONTAINMENT-001-B27.json`

## Installed execution contract

The fixed target reuses the existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; no second scheduler or heartbeat exists. It operates only on an already-materialized local `StegVerse-Labs/Site` root from `STEGVERSE_REPO_ROOTS_JSON`, proves the local Git `HEAD`, and performs no remote checkout.

It executes these bounded deterministic Site validators:

1. `scripts/check_thought_experiments_publication.py`
2. `scripts/write_site_workflow_inventory.py`
3. `scripts/check_site_workflow_inventory.py`
4. `scripts/check_session_work_claims.py`
5. `scripts/site_handoff_orchestrator.py`
6. `scripts/check_ecosystem_heartbeat_orchestration.py`
7. `scripts/check_ecosystem_chat_application.py`
8. `scripts/check_iphone_heartbeat_transition_projection.py`
9. `scripts/run_sandbox_validation.py`
10. `scripts/check_stegfin_phone_projection.py`

The carrier fails closed when the Site root is absent, any required validator is absent, the local source head cannot be proven, any validator exits nonzero, required deterministic receipts are absent, the Thought Experiments receipt is not `PASS`, authority or activation is asserted, the retired standalone workflow still exists, the workflow inventory is not canonical-3/placeholders-0, the B27 task does not preserve TV/TVC-only credential authority, or a credential-bearing validation environment is present.

A successful outcome embeds `stegverse.healer.site_b27_validation_receipt/v0.1` in the existing sovereign scheduler receipt. The receipt includes the exact local source head, workflow counts, validated scripts, and explicit false values for GitHub-token requirement, remote checkout, artifact custody, repository writeback authority, runtime authority, wallet signing/broadcast authority, publication authority, and settlement authority.

## Source and release evidence

```text
target binding: 334badfaf4bcbf189a1963c970bedfcbefdd728c
scheduler handler: 83c491650ff16be246944643b9a84e832aa676a5
deterministic tests: cd8ea6d26b531827708c12411af7200bdc590ed8
handoff source: 55ef1cd07919efe555c12a5a41bb58b51048a98f
PR: #15
merge: e68fc136598af641481152176dc41725e1663fe0
Test Readiness: 32086347511 SUCCESS
repo-smoke job: 95559570146 SUCCESS
credential refusal: PASS
anonymous exact-source fetch: PASS
baseline repository smoke: PASS
deterministic Healer tests: 27 PASS / 0 FAIL
Site B27 carrier tests: 5 PASS / 0 FAIL
validation-only authority boundary: PASS
HEALER_RUNTIME_EXECUTION_AUTHORITY: NONE
HEALER_GITHUB_TOKEN_AUTHORITY: NONE
```

The directly inspected Test Readiness log shows all five `test_site_b27_native_validation` cases passing: credential-bearing environment blocks, missing validator blocks, exact local-head/non-authorizing PASS receipt completes, existing scheduler target binding is correct, and validator failure blocks.

## Cross-repository integration

A sovereign scheduler receipt may satisfy the Site B27 task's allowed `equal-or-stronger StegVerse-native validation` path only when the `site-b27-native-validation` outcome is `COMPLETE`, its nested receipt is `PASS`, and its `source_head` exactly matches the then-current Site B27 candidate head. Site #268 must still verify its own release predicates, keep the branch current with main, merge through the canonical Site release path, and separately observe the post-merge Thought Experiments public routes.

This carrier grants no Site merge authority and cannot sign/broadcast a StegFin wallet transaction, publish on behalf of a human, grant runtime authority, or settle a trade.

## Activation boundary and machine-owned work

Source and test integration are `COMPLETE_RELEASED`. Live execution remains `MACHINE_OWNED` by the already-existing ordinary scheduler. Activation still requires the canonical receipt `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`; source merge, GitHub CI, or chat state cannot substitute for that receipt.

The Site B27 repository must be materialized at the exact candidate head for the native carrier to produce exact-head release evidence. Missing materialization or a nonmatching head is fail-closed.

## Session consolidation

The local-model/runtime source goals remain complete/released elsewhere and are not duplicated here. StegFin signing/broadcast remains USER_ONLY. GitHub billing is no longer the only possible B27 validation carrier because this source path is now released.

```text
developed_files: 4/4
validation: 2/3
integration: 2/3
goal_activation: 2/3
session_consolidation: 5/5
archive_condition: source carrier released; remaining live execution is machine-owned with a durable observer and exact release condition
```

## Next executable actions

1. Existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` executes `site-b27-native-validation` against a materialized Site B27 candidate.
2. Inspect the scheduler receipt and require `state=COMPLETE`, nested `state=PASS`, and `source_head` equal to the exact Site B27 candidate.
3. Propagate that receipt evidence to Site #268 / B27 task.
4. Site completes exact-current-main merge plus post-merge Thought Experiments public-route observation, then releases the B27 claim/task/handoff.
