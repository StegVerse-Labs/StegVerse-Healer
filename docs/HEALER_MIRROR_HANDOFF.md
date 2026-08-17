# StegVerse-Healer Mirror Handoff

## Authority and active goal

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Branch: `main`
- Primary goal ID: `HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001`
- Released integration goal ID: `HEALER-G18-PRE-CARRIER-ASSIST-001`
- Originating goal: keep Healer scheduling/repair local and sovereign, preserve TV/TVC as the only credential/admission authority, and assist canonical heartbeat recovery without creating a second heartbeat or scheduler.
- Canonical organization continuation: `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`
- Canonical heartbeat continuation: `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`
- Canonical Healer scheduler continuation: `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`
- Repository-local continuation: this handoff, `data/session_consolidation/g18-pre-carrier-assist.json`, `data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json`, and `data/summary/single_scheduler_migration.json`.
- Current repository state: `PRE_CARRIER_ASSIST_COMPLETE_RELEASED_LIVE_HB30_MACHINE_OWNED`.

## Governing invariants

```text
credential_authority: TV/TVC
credential_requirement_for_pre_carrier_assist: NONE
non_tv_tvc_secret_or_token_allowed: false
github_token_production_authority: NONE
github_actions_production_role: NONE
heartbeat_owner: StegVerse-Labs/.github G18
healer_pre_carrier_authority_effect: NONE
healer_may_execute_hb29_to_hb30_transition: false
healer_may_synthesize_hb30: false
arbitrary_target_command_authority: NONE
remote_source_checkout_required_for_production: false
missing local capability: FAIL_CLOSED
hosted_validation: non-authorizing
wallet_signing_and_broadcast: USER_ONLY
```

Healer may inspect and diagnose canonical heartbeat prerequisites before HB30 exists. It does not own the heartbeat transition, WorkerCoordinator authority, worker claim/fence/lease, carrier state, provider/wallet state, or TV/TVC authority.

## Authoritative files

```text
docs/HEALER_MIRROR_HANDOFF.md
app/sovereign_scheduler.py
app/pre_carrier_assist.py
tests/test_pre_carrier_assist.py
data/orchestrator_targets.json
data/session_consolidation/g18-pre-carrier-assist.json
data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json
data/summary/single_scheduler_migration.json
.github/workflows/test-readiness.yml
```

Cross-repository authority/evidence:

```text
StegVerse-Labs/.github/management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
StegVerse-Labs/.github/authorizations/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
StegVerse-Labs/.github/control/worker-registry.d/healer-sovereign-scheduler-001.json
StegVerse-Labs/.github/control/process-worker-adapters.json
StegVerse-Labs/.github#65 comment 5317133105
StegVerse-Labs/TV/scripts/sovereign_self_heal.py
StegVerse-Labs/TVC/policies/local_repository_mutation/tv_self_heal.v1.json
StegVerse-Labs/SCW/scw/local_health.py
StegVerse-Labs/Continuity/scripts/guardian.py
```

## Execution ownership and claims

### MACHINE_OWNED — do not compete

`SHWP-DURABLE-RUNTIME-ACTIVATION / G18 / fencing token 18` owns the real HB29→HB30+ transition and the transition handoff to an independently admitted `WorkerCoordinator` observation.

`SHWP-HEALER-SOVEREIGN-SCHEDULER-001` owns ordinary post-carrier Healer scheduling and fixed local target execution.

Neither machine path may be replaced by a chat session, GitHub Actions, Render, Vercel, Cloudflare, hosted inference, or another scheduler/process host.

### Released session claim

```yaml
task_id: HEALER-G18-PRE-CARRIER-ASSIST-001
issue: StegVerse-Labs/StegVerse-Healer#4
pull_request: StegVerse-Labs/StegVerse-Healer#5
merge_commit: 571b6a86737173a89235110294025f9808695531
claimant: current-session-healer-pre-carrier-integration-lane
role: CLAIMED_FOR_IMPLEMENTATION
claim_created_at: 2026-08-17T14:39:58Z
claim_released_at: 2026-08-17T14:44:00Z
claim_state: COMPLETE_RELEASED
claim_record: data/session_consolidation/g18-pre-carrier-assist.json
collision_boundary: no live heartbeat/worker claim/fence/lease/carrier-state mutation and no credential/provider/wallet authority
```

No chat/session implementation claim remains on the released Healer pre-carrier source.

## Installed pre-carrier G18 assist

`app/pre_carrier_assist.py` is a bounded local diagnostic/readiness producer for an already-materialized `StegVerse-Labs/.github` source tree.

It:

- requires `STEGVERSE_REPO_ROOTS_JSON` and provides no remote-checkout production fallback;
- rejects GitHub/provider/wallet credential variables because this assist requires no credential;
- verifies immutable legacy HB29 and generation 29;
- verifies v12 carrier and independent WorkerCoordinator source presence;
- verifies `management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json`: HB29 immutable, first successor HB30, v12 runtime, separate WorkerCoordinator, canonical transition producer, no extra-machine requirement, no always-on-host requirement, TV/TVC authority, and no NON-TV/TVC secret/token authority;
- verifies G18 remains `MACHINE_OWNED_BOUND_G18` at fencing token 18 and live activation is unclaimed;
- returns `READY_FOR_G18_TRANSITION`, `BLOCKED`, `REVIEW_REQUIRED`, or `FAILED` plus an exact next action;
- hashes legacy HB29 as evidence but does not mutate it;
- does not invoke `scripts/advance_heartbeat_transition.py`;
- does not create `control/heartbeat-carrier-runtime-state.json` or synthesize HB30.

The released authority path is:

```text
already-materialized StegVerse source
-> Healer pre-carrier inspection/diagnosis (authority_effect NONE)
-> READY_FOR_G18_TRANSITION or exact fail-closed blocker
-> existing G18 claim/fence
-> scripts/advance_heartbeat_transition.py
-> HB30+
-> independent WorkerCoordinator observation
-> ordinary Healer scheduler may later execute under its own admitted worker
```

This removes the diagnostic circularity without making Healer a second heartbeat or transition owner.

## Existing sovereign scheduler

`app/sovereign_scheduler.py` remains the ordinary post-carrier Healer scheduler. It rejects GitHub credential variables, operates on already-materialized repositories, uses fixed code-defined handlers, fails closed on missing repositories/capabilities, and grants no GitHub/provider/wallet/release/deployment authority.

Managed local targets remain Site, SCW, SCW uptime, TV self-heal through TVC authority, Continuity, Quiet Enforcer, and StegDeploy relay. CosDen remains audit-only under StegDB canonical ownership.

## Completed mutation evidence

Pre-carrier integration:

```text
StegVerse-Healer issue #4 CLOSED_COMPLETED
StegVerse-Healer PR #5 MERGED
571b6a86737173a89235110294025f9808695531 merge commit
32039990314 PR-head Test Readiness SUCCESS
32040015153 main Test Readiness SUCCESS
32040015173 main Validate Session Consolidation SUCCESS
5317133105 .github#65 G18 continuation comment
```

Existing scheduler/source control remains released: GitHub workflow-dispatch production transport and GitHub-token/PAT production scheduler authority are superseded; SCW, Continuity, TV/TVC self-heal, Quiet Enforcer, StegDeploy relay/intake and worker binding remain source/control complete. Historical evidence is preserved in Git history and migration records.

## Validation

Deterministic commands:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python app/pre_carrier_assist.py
```

`Test Readiness` now runs the unit suite. PR-head run `32039990314` and post-merge main run `32040015153` passed. `Validate Session Consolidation` run `32040015173` passed on merge commit `571b6a86737173a89235110294025f9808695531`.

Hosted runs are source/test evidence only. They do not prove HB30, independent WorkerCoordinator observation, ordinary Healer scheduler activation, provider execution, wallet readiness, signing, broadcast, or trade settlement.

## Active Site Marketplace Coinbase local-observer integration

Owner issue: `StegVerse-Labs/StegVerse-Healer#6`.

Implementation PR: `StegVerse-Labs/StegVerse-Healer#7` on `feat/site-marketplace-coinbase-local-observer-6`.

Claim record: `data/session_consolidation/site-marketplace-coinbase-local-observer.json`.

Purpose: preserve the nonterminal Site#131 Marketplace–Coinbase observation semantics while retiring the GitHub-hosted Site controller/token/writeback path. The work reuses the existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; it does not create another scheduler or heartbeat.

Installed source behavior:

- `data/orchestrator_targets.json` binds `StegVerse-Labs/Site` target `marketplace-coinbase-local-observer` to the existing sovereign scheduler;
- `app/sovereign_scheduler.py` executes only the already-materialized Site `scripts/advance_marketplace_coinbase_activation.py` and passes local repository roots;
- missing Site repository/script fails closed;
- GitHub/Marketplace evidence token variables are forbidden;
- no GitHub API, PAT, provider, wallet, Marketplace, Coinbase live/financial, publication, release or execution authority is granted;
- Site PR #329 owns removal of `.github/workflows/advance-marketplace-coinbase-activation.yml` and conversion of the Site observer to local-repository evidence only.

Validation evidence before this handoff update:

```text
PR #7 earlier source test: 32042403535 SUCCESS, 10 deterministic tests PASS
credential audit of that run: actions/checkout and actions/setup-python still consumed GitHub-managed token transport
credential-clean validation correction: ad98b4cf17ee70f6419be0f596937c525c523e5b
credential-clean Test Readiness: 32044366801 SUCCESS
job: 95429088491 SUCCESS
credential refusal: PASS
anonymous exact-ref fetch without credential helper/extraheader: PASS
preinstalled Python: PASS
baseline smoke: PASS
deterministic Healer tests: PASS
validation-only authority boundary: PASS
```

The `Test Readiness` workflow now has `permissions: {}`, no `actions/checkout`, no `actions/setup-python`, no artifact upload, no repository writeback, and no credential-bearing environment. Hosted validation remains non-authorizing.

Release condition for this integration: exact-head validation after this handoff update must pass; PR #7 may then merge as source integration, while the claim remains active until companion Site PR #329 is independently validated/merged and continuation semantics are preserved. Ordinary Healer scheduler activation still requires the canonical admitted post-carrier worker receipt and is not inferred from CI or merge.

## Machine-observable incomplete work

### Heartbeat activation

Owner: `StegVerse-Labs/.github / SHWP-DURABLE-RUNTIME-ACTIVATION / G18`.

Next executable action: on the next admitted G18 execution opportunity, consume the pre-carrier assist result. If `READY_FOR_G18_TRANSITION`, G18 executes `scripts/advance_heartbeat_transition.py` under its existing claim/fence. If the assist returns a fail-closed state, G18 consumes its exact blocker/next action without granting Healer heartbeat authority.

Release condition:

```text
receipts/heartbeat-transition-continuity/latest.json = valid CARRIER_TRANSITION_COMPLETE at HB30+
control/heartbeat-carrier-runtime-state.json = HB30+
control/heartbeat-state.json = unchanged legacy HB29
control/worker-runtime-state.json = independently observes carrier epoch
worker-control-plane evidence present
reconstruction PASS
no duplicate claim/fence
no NON-TV/TVC credential authority
```

### Ordinary Healer scheduler activation

Owner: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`.

Release condition: admitted post-carrier execution emits `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json` with current target outcomes and no forbidden credential authority.

### Downstream activation

Sovereign inference remains owned by `.github#60` and its TVC → LLM-adapter → Master Records chain. StegFin remains owned by its canonical worker/task state and must stop at `WALLET_HANDOFF_READY` before USER_ONLY signing/broadcast.

## Cross-repository propagation

No propagation is inferred from source completion. After immutable activation evidence and applicable consumer release gates, evidence may propagate to Site, Publisher, admissibility-wiki, stegguardian-wiki, and passive Master Records custody where required by their canonical contracts.

## Session consolidation

The unique Healer pre-carrier requirement is fully durable and transferred. The source is merged, tests are green, issue #4 is closed, claim state is `COMPLETE_RELEASED`, and `.github#65` contains the G18 consumption contract.

The Site Marketplace Coinbase observer migration is active and durable in Healer issue #6, PR #7, the claim record, and Site PR #329. It remains a distinct support responsibility until Healer exact-head validation/merge and companion Site validation/merge complete.

MERGED INTO for the released pre-carrier work:

```text
StegVerse-Labs/StegVerse-Healer/docs/HEALER_MIRROR_HANDOFF.md
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github#65 comment 5317133105
```

## Completion accounting

Current denominator for `HEALER-G18-PRE-CARRIER-ASSIST-001`:

- required developed/source-control surfaces: 5;
- deterministic validation groups: 2;
- integration groups: 3;
- live activation groups: 2;
- session transfer groups: 1.

Current state:

- developed files/control surfaces: 5/5;
- scaffolding or production stubs: 0;
- missing source/control files: 0;
- deterministic validation: 2/2;
- integration: 3/3;
- live activation: 0/2 — intentionally machine-owned by G18 and independent WorkerCoordinator;
- session consolidation for this Healer goal: 1/1.

For `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`, source/control surfaces are implemented; exact-head validation after the handoff update, merge, companion Site validation/merge, and claim release remain.

## Archive condition

The Healer pre-carrier implementation itself is source/archive-safe and no longer chat-owned. The broader originating session is not archive-ready while the active Site Marketplace Coinbase observer migration remains unmerged/unreleased and while Site workflow/token minimization continues. Live HB30+, independent WorkerCoordinator observation, sovereign inference and downstream product activation remain separately machine-owned and are not inferred from source/CI state.
