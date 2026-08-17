# StegVerse-Healer Mirror Handoff

## Authority and active goal

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Canonical branch: `main`
- Primary goal ID: `HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001`
- Released integration goals: `HEALER-G18-PRE-CARRIER-ASSIST-001`, `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`
- Originating goal: keep Healer scheduling/repair local and sovereign, preserve TV/TVC as the only credential/admission authority, assist canonical heartbeat recovery without creating a second heartbeat or scheduler, and absorb bounded recurring observation work from GitHub-hosted controllers when a fixed local handler is appropriate.
- Canonical organization continuation: `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`
- Canonical heartbeat continuation: `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`
- Canonical Healer scheduler continuation: `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`
- Repository-local continuation: this handoff plus `data/session_consolidation/*.json` and `data/summary/single_scheduler_migration.json`.
- Current repository state: `SOURCE_CONTROL_RELEASED_LIVE_SCHEDULER_ACTIVATION_MACHINE_OWNED`.

## Governing invariants

```text
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_token_production_authority: NONE
github_actions_production_role: NONE
remote_source_checkout_required_for_production: false
missing_local_capability: FAIL_CLOSED
heartbeat_owner: StegVerse-Labs/.github G18
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
healer_may_execute_hb29_to_hb30_transition: false
healer_may_synthesize_hb30: false
arbitrary_target_command_authority: NONE
wallet_signing_and_broadcast: USER_ONLY
hosted_validation: non-authorizing
```

Healer does not own heartbeat transition authority, WorkerCoordinator authority, worker claims/fences/leases, provider credentials, wallet authority, Marketplace/Publisher/crypto-bot product authority, or Site publication/release/live/financial authority.

## Authoritative files

```text
docs/HEALER_MIRROR_HANDOFF.md
app/sovereign_scheduler.py
app/pre_carrier_assist.py
data/orchestrator_targets.json
tests/test_pre_carrier_assist.py
tests/test_site_marketplace_coinbase_observer.py
data/session_consolidation/g18-pre-carrier-assist.json
data/session_consolidation/site-marketplace-coinbase-local-observer.json
data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json
data/summary/single_scheduler_migration.json
.github/workflows/test-readiness.yml
```

## Execution ownership and collision boundaries

### MACHINE_OWNED — do not compete

`SHWP-DURABLE-RUNTIME-ACTIVATION / G18` owns the real HB29→HB30+ transition and handoff to independently admitted WorkerCoordinator observation.

`SHWP-HEALER-SOVEREIGN-SCHEDULER-001` owns ordinary post-carrier Healer scheduling and fixed local target execution.

Neither machine path may be replaced by a chat session, GitHub Actions, Render, Vercel, Cloudflare, hosted inference, or another scheduler/process host.

## Released G18 pre-carrier assist

Claim record: `data/session_consolidation/g18-pre-carrier-assist.json`.

```text
issue: StegVerse-Healer#4 CLOSED_COMPLETED
PR: StegVerse-Healer#5 MERGED
merge: 571b6a86737173a89235110294025f9808695531
PR-head Test Readiness: 32039990314 SUCCESS
main Test Readiness: 32040015153 SUCCESS
main Validate Session Consolidation: 32040015173 SUCCESS
claim_state: COMPLETE_RELEASED
authority_effect: NONE
```

`app/pre_carrier_assist.py` inspects an already-materialized `.github` source tree, verifies immutable HB29 / v12 / G18 prerequisites, refuses forbidden credential environments, and returns `READY_FOR_G18_TRANSITION`, `BLOCKED`, `REVIEW_REQUIRED`, or `FAILED`. It does not invoke the transition producer, synthesize HB30, or mutate legacy HB29.

## Released Site Marketplace–Coinbase local observer integration

Claim record: `data/session_consolidation/site-marketplace-coinbase-local-observer.json`.

Purpose: replace the GitHub-hosted Site Marketplace/Coinbase observation controller with a fixed local target in the existing sovereign Healer scheduler while preserving the nonterminal product chain and all authority boundaries.

Installed behavior:

- `data/orchestrator_targets.json` binds Site target `marketplace-coinbase-local-observer` to the existing scheduler;
- `app/sovereign_scheduler.py` invokes only the already-materialized Site `scripts/advance_marketplace_coinbase_activation.py`;
- `STEGVERSE_REPO_ROOTS_JSON` is the only repository-materialization input;
- missing local Site script/repository fails closed;
- GitHub and Marketplace evidence credential variables are rejected;
- no GitHub API/PAT/provider/wallet credential path is present;
- no second scheduler or heartbeat was created;
- no Marketplace, Coinbase live/financial, Publisher, crypto-bot, Site publication/release/execution, StegFin, or wallet authority was granted.

Release evidence:

```text
Healer issue: #6
Healer PR: #7
Healer final head: 547d44555be78e610fd4623ca30786fc02188221
Healer merge: ecf96188348c097dfdea3ce55c47db9dff6e84ef
Healer credential-clean Test Readiness: 32044423476 SUCCESS
Healer validation job: 95429249175 SUCCESS
Site PR: #329
Site final head: caf9b6dae32f09b7475a0dbe61cbc5e7e873c089
Site merge: 72ca1b9377a918983d5bcb329fa4c13ab0294cc8
Site Bootstrap Validate: 32044523223 SUCCESS
Site Handoff Orchestrator: 32044523168 SUCCESS
Ecosystem Heartbeat Orchestration: 32044523264 SUCCESS
Check StegFin Phone Projection: 32044523162 SUCCESS
Site claim release: c00ac1906dc6bcfd5195e07dc7916e3cc2d760bc
Site Actions handoff release: c0c87e2004e41acb22afe7fddaec61947d451df4
Site Marketplace handoff release: 60b7cd74be751df8b11e7b5bbc940dc4fd0319a9
Healer claim release: 76b5523e02dbc37ad726ece7689902d551604a75
claim_state: COMPLETE_RELEASED
authority_effect: NONE
runtime_activation_effect: NONE
financial_authority_effect: NONE
```

The credential-clean Healer `Test Readiness` path uses `permissions: {}`, refuses credential-bearing environment, anonymously fetches the exact public ref with credential helper/extraheader disabled, uses preinstalled Python, performs no repository writeback or artifact upload, and grants no runtime authority.

## Ordinary scheduler activation remains unproven

Source merge and CI success do not prove live Healer execution. Runtime activation remains owned by `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` and requires an admitted post-carrier execution receipt:

```text
receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
```

The receipt must show current fixed-target outcomes and no forbidden credential authority.

## Heartbeat activation remains machine-owned

Owner: `StegVerse-Labs/.github / SHWP-DURABLE-RUNTIME-ACTIVATION / G18`.

Release condition remains:

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

## Downstream activation

- Sovereign inference remains owned by `.github#60` and its TVC → LLM-adapter → Master Records chain.
- StegFin remains owned by its canonical task state and current phone path; USER_ONLY remains the sole signer/broadcaster.
- Site workflow/token minimization continues under `StegVerse-Labs/Site#268`.

## Session consolidation

The Healer-specific Marketplace observer work from this session is fully durable, source-merged, validated, and released. No chat-owned Healer implementation claim remains.

MERGED INTO:

```text
StegVerse-Labs/StegVerse-Healer/docs/HEALER_MIRROR_HANDOFF.md
StegVerse-Labs/StegVerse-Healer/data/session_consolidation/site-marketplace-coinbase-local-observer.json
StegVerse-Labs/Site/docs/ACTIONS_COST_CONTAINMENT_MIRROR_HANDOFF.md
StegVerse-Labs/Site#268
```

## Completion accounting

For `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`:

```text
developed/source-control surfaces: 5/5
scaffolding or production stubs: 0
missing source/control files: 0
deterministic validation: 2/2
cross-repository integration: 2/2 (Healer merge + Site controller retirement merge)
claim release: 1/1
live scheduler activation: separate MACHINE_OWNED gate; not inferred
```

## Archive condition

The Healer-specific support task is archive-safe. The broader originating session is not archive-ready because Site #268 still has executable workflow/token minimization debt. HB30+, independent WorkerCoordinator observation, sovereign inference, ordinary Healer execution, and downstream product activation remain separately machine-owned and are not inferred from source/CI state.
