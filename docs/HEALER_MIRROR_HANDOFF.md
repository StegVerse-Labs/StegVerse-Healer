# StegVerse-Healer Mirror Handoff

## Authority and active goal

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Canonical branch: `main`
- Primary goal ID: `HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001`
- Released integration goals: `HEALER-G18-PRE-CARRIER-ASSIST-001`, `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`
- Active integration goal: `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`
- Originating goal: keep Healer scheduling/repair local and sovereign, preserve TV/TVC as the only credential/admission authority, assist canonical heartbeat recovery without creating a second heartbeat or scheduler, and absorb bounded recurring work from GitHub-hosted controllers only through fixed local handlers in the existing sovereign scheduler.
- Canonical organization continuation: `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`
- Canonical heartbeat continuation: `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`
- Canonical Healer scheduler continuation: `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`
- Current repository state: `SOURCE_CONTROL_ACTIVE_INTEGRATION_LIVE_SCHEDULER_ACTIVATION_MACHINE_OWNED`.

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
tests/test_site_marketplace_projection_import.py
data/session_consolidation/g18-pre-carrier-assist.json
data/session_consolidation/site-marketplace-coinbase-local-observer.json
data/session_consolidation/site-marketplace-projection-local-import.json
data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json
.github/workflows/test-readiness.yml
```

## Machine-owned execution boundaries

`SHWP-DURABLE-RUNTIME-ACTIVATION / G18` owns HB29→HB30+ and the independent WorkerCoordinator observation handoff.

`SHWP-HEALER-SOVEREIGN-SCHEDULER-001` owns ordinary post-carrier Healer scheduling and fixed local target execution.

Neither machine path may be replaced by a chat session, GitHub Actions, Render, hosted inference, or another scheduler/process host.

## Released G18 pre-carrier assist

```text
claim: HEALER-G18-PRE-CARRIER-ASSIST-001 / COMPLETE_RELEASED
issue: #4 CLOSED_COMPLETED
PR: #5 MERGED
merge: 571b6a86737173a89235110294025f9808695531
PR-head Test Readiness: 32039990314 SUCCESS
main Test Readiness: 32040015153 SUCCESS
main Validate Session Consolidation: 32040015173 SUCCESS
authority_effect: NONE
```

The assist verifies immutable HB29/v12/G18 prerequisites from already-materialized source and does not synthesize HB30 or invoke the transition producer.

## Released Site Marketplace observer integration

```text
claim: HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001 / COMPLETE_RELEASED
issue: #6 CLOSED_COMPLETED
PR: #7 MERGED
Healer merge: ecf96188348c097dfdea3ce55c47db9dff6e84ef
Healer Test Readiness: 32044423476 SUCCESS
Site PR #329 merge: 72ca1b9377a918983d5bcb329fa4c13ab0294cc8
Site claim release: c00ac1906dc6bcfd5195e07dc7916e3cc2d760bc
Healer claim release: 76b5523e02dbc37ad726ece7689902d551604a75
authority_effect: NONE
runtime_activation_effect: NONE
financial_authority_effect: NONE
```

Fixed target `marketplace-coinbase-local-observer` invokes only the already-materialized Site observation script and uses local repository roots. No GitHub API/token/PAT path or second scheduler exists.

## Active Site Marketplace projection-import integration

Claim: `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`.

Issue: `StegVerse-Labs/StegVerse-Healer#8`.

PR: `StegVerse-Labs/StegVerse-Healer#9` on `feat/site-marketplace-projection-local-import-8`.

Purpose: remove the remaining scheduled GitHub-hosted Site Marketplace/Coinbase projection importer and execute that bounded recurrence through the existing sovereign Healer scheduler.

Installed behavior:

- `data/orchestrator_targets.json` binds fixed target `marketplace-coinbase-local-projection-import` to the existing scheduler;
- `app/sovereign_scheduler.py` invokes only the already-materialized Site `scripts/import_marketplace_coinbase_accessibility.py`;
- both Site and `GCAT-BCAT-Engine/Publisher` must be present in `STEGVERSE_REPO_ROOTS_JSON`;
- missing Site importer or Publisher repository fails closed;
- no GitHub API, raw GitHub URL, PAT, provider, wallet, or NON-TV/TVC credential is used;
- no second scheduler or heartbeat is created;
- no publication, release, execution, live, custody, withdrawal, or financial authority is granted.

Deterministic tests added in `tests/test_site_marketplace_projection_import.py` verify fixed-target binding, missing-Site failure, missing-Publisher failure, and local execution against materialized Site/Publisher repositories.

Validation before this handoff update:

```text
PR #9 Test Readiness: 32045128811 SUCCESS
job: 95431214621 SUCCESS
credential refusal: PASS
anonymous exact-ref validation fetch: PASS
baseline smoke: PASS
14 deterministic Healer tests: PASS
validation-only authority boundary: PASS
```

Companion Site branch `chore/site-marketplace-projection-import-retirement-20260817` removes `.github/workflows/import-marketplace-coinbase-accessibility.yml`, makes the Site importer local-only, expands deterministic tests, and carries semantic claim `SITE-MARKETPLACE-COINBASE-PROJECTION-IMPORT-RETIREMENT-20260817`.

Release condition: exact-head credential-clean Healer validation after this handoff update must pass; PR #9 may then merge as source integration. The Healer claim remains active until companion Site exact-head validation/merge and Site claim/handoff release complete. Ordinary Healer runtime activation remains a separate machine-owned gate.

## Credential-clean hosted validation boundary

`.github/workflows/test-readiness.yml` uses `permissions: {}`, refuses credential-bearing environment, performs an anonymous exact-ref fetch with credential helper/extraheader disabled, uses preinstalled Python, performs no repository writeback or artifact upload, and emits:

```text
HEALER_VALIDATION_ONLY=TRUE
HEALER_RUNTIME_EXECUTION_AUTHORITY=NONE
HEALER_GITHUB_TOKEN_AUTHORITY=NONE
```

GitHub runner metadata may expose platform-level metadata permission, but the workflow does not consume a GitHub token as an input or authority surface.

## Ordinary scheduler activation remains unproven

Source merge/CI do not prove live Healer execution. Activation requires admitted post-carrier execution receipt:

```text
receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
```

## Downstream owners

- HB30+ / WorkerCoordinator: `.github` G18 machine owner.
- Sovereign inference: `.github#60` TVC → LLM-adapter → Master Records chain.
- StegFin: canonical worker/task state and phone path; USER_ONLY signing/broadcast.
- Site workflow/token minimization: `StegVerse-Labs/Site#268`.

## Completion accounting

Released Healer source goals are complete. For active `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`:

```text
developed/source-control surfaces: 5/5
scaffolding or production stubs: 0
missing source/control files: 0
pre-handoff deterministic validation: PASS
exact-head post-handoff validation: PENDING
Healer source merge: PENDING
companion Site integration: PENDING
live scheduler activation: separate MACHINE_OWNED gate; not inferred
```

## Archive condition

The broader session is not archive-ready while this active Healer/Site projection-import migration remains unreleased and Site #268 retains additional workflow/token minimization debt. Machine-owned runtime/product activation remains separate and is not inferred from source or CI state.
