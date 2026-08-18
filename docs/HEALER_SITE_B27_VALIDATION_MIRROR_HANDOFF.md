# Healer Site B27 Sovereign Validation Mirror Handoff

This is a scoped, noncompeting child handoff for `HEALER-SITE-B27-SOVEREIGN-VALIDATION-001`. The repository-wide canonical handoff remains `docs/HEALER_MIRROR_HANDOFF.md`.

## Canonical state

```text
goal_id: HEALER-SITE-B27-SOVEREIGN-VALIDATION-001
originating_goal: provide an equal-or-stronger StegVerse-native validation path for Site B27 while GitHub-hosted validation is billing-blocked
repository: StegVerse-Labs/StegVerse-Healer
branch: feat/site-b27-sovereign-validation-carrier-14
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
implementation_claim: CLAIMED_FOR_IMPLEMENTATION
validation_claim: CLAIMED_FOR_VALIDATION
claim_created_at: 2026-08-18T00:52:19Z
claim_release_condition: source carrier and deterministic tests merged/released, or explicit BLOCKED state with machine-observable release condition
state: SOURCE_IMPLEMENTED_VALIDATION_PENDING
```

## Authoritative surfaces

- `data/orchestrator_targets.json::StegVerse-Labs/Site/site-b27-native-validation`
- `app/sovereign_scheduler.py::_execute_target`
- `tests/test_site_b27_native_validation.py`
- `docs/HEALER_SITE_B27_VALIDATION_MIRROR_HANDOFF.md`
- issue `StegVerse-Labs/StegVerse-Healer#14`
- source continuation `StegVerse-Labs/Site#268`, Site PR #387, and Site `data/tasks/SITE-ACTIONS-COST-CONTAINMENT-001-B27.json`

## Installed execution contract

The new fixed target reuses the existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; no second scheduler or heartbeat is created. It runs only against an already-materialized local `StegVerse-Labs/Site` root from `STEGVERSE_REPO_ROOTS_JSON` and never performs remote checkout.

The target executes the bounded deterministic Site validators required for B27 release evidence:

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

The carrier fails closed when the Site root is absent, any required validator is absent, the local Git source head cannot be proven, any validator exits nonzero, required deterministic receipts are absent, the Thought Experiments receipt is not `PASS`, authority or activation is asserted, the retired standalone workflow still exists, the workflow inventory has anything other than three canonical workflows or zero placeholders, the B27 task does not preserve TV/TVC-only credential authority, or a credential-bearing validation environment is present.

Successful output is embedded in the existing sovereign scheduler receipt as `stegverse.healer.site_b27_validation_receipt/v0.1` and includes the exact local source head, workflow counts, validated script list, and explicit false values for GitHub-token requirement, remote checkout, artifact custody, repository writeback authority, runtime authority, wallet signing/broadcast authority, publication authority, and settlement authority.

## Source commits

```text
target binding: 334badfaf4bcbf189a1963c970bedfcbefdd728c
scheduler handler: 83c491650ff16be246944643b9a84e832aa676a5
deterministic tests: cd8ea6d26b531827708c12411af7200bdc590ed8
```

## Validation

Static/source inspection: COMPLETE.
Deterministic unit test source: INSTALLED.
Hosted Healer test execution: PENDING.
Ordinary sovereign scheduler execution against the Site B27 materialized source: MACHINE_OWNED / PENDING.

Required validation commands after source checkout/materialization:

```bash
python -m unittest tests.test_site_b27_native_validation
python -m unittest discover -s tests
```

Strongest release evidence requires either successful Healer test execution or an equal/stronger local deterministic execution plus direct inspection. Source presence alone does not prove the live scheduler executed.

## Cross-repository integration

When a sovereign scheduler receipt contains a `site-b27-native-validation` outcome with `state=COMPLETE`, receipt `state=PASS`, and `source_head` exactly equal to the then-current Site B27 candidate head, Site #268 may use that as the StegVerse-native pre-merge validation carrier allowed by `data/tasks/SITE-ACTIONS-COST-CONTAINMENT-001-B27.json`. Site must still verify its own release predicates, remain current with main, merge through its canonical release path, and separately observe the post-merge Thought Experiments public routes.

This carrier grants no Site merge authority and cannot sign/broadcast a StegFin wallet transaction, publish on behalf of a human, grant runtime authority, or settle a trade.

## Blockers and machine-owned work

- Ordinary Healer scheduler activation is MACHINE_OWNED and remains proven only by the canonical scheduler receipt `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`.
- The Site B27 candidate must be locally materialized at the exact candidate head for exact-head proof.
- GitHub-hosted CI may remain billing-blocked; this source carrier exists specifically so that GitHub billing is not the only possible validation path.

## Session consolidation

The user-session requirement to continue actual execution despite prior archive wording is durably represented by this issue/handoff and the Site #268 continuation. The local-model/runtime source goals remain complete/released elsewhere and are not duplicated here. StegFin signing/broadcast remains USER_ONLY.

```text
developed_files: 4/4
validation: 1/3
integration: 1/3
goal_activation: 1/3
session_consolidation: 4/5
archive_condition: Healer source carrier released or durably blocked; Site continuation remains self-sufficient; no chat-only requirement remains
```

## Next executable actions

1. Execute Healer deterministic tests on this exact branch/head through the strongest available path.
2. Correct any source/test failure without weakening fail-closed or credential boundaries.
3. Merge/release issue #14 only after test evidence is inspected.
4. Wait for the existing sovereign scheduler machine lane to execute `site-b27-native-validation` against the exact materialized Site B27 head.
5. Propagate a matching PASS receipt to Site #268 / B27 task; Site then completes its own merge and post-merge public-route proof.
