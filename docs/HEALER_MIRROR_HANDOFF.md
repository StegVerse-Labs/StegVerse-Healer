# StegVerse-Healer Mirror Handoff

## Current goal
Make `StegVerse-Labs/StegVerse-Healer` the sole scheduling authority for managed StegVerse repositories, while downstream repositories expose quiet, manual/event-driven orchestrators and retain durable repair continuity.

## Active source of truth
This file, `docs/HEALER_ACTIVATION_PLAN.md`, `registry/managed_repos.yml`, `data/orchestrator_targets.json`, and `data/summary/single_scheduler_migration.json` jointly define current ownership, scope, blockers, and continuation requirements.

## Decisions now durable
1. `StegVerse-Healer` is the only managed repository permitted to contain approved `on.schedule` triggers.
2. Downstream managed repositories must expose verified `workflow_dispatch` or bounded event entrypoints and contain no local schedules after migration.
3. Existing repository-specific orchestrators should be adapted rather than duplicated when they already preserve required logic.
4. Obsolete workflows are replaced in place by `templates/disabled_legacy_workflow.yml` or deleted only after their logic is migrated and history is preserved in Git.
5. The scheduler reads `data/orchestrator_targets.json`; target duplication inside workflow YAML is prohibited for ordinary cadence targets.
6. `quiet_enforcer.yml` audits configured target repositories for unauthorized schedules.
7. Cross-repository mutation is not implied by dispatch. Observation-only inputs are required until runtime validation and authority checks pass.
8. Evidence-dependent relays may use dedicated Healer workflows when their payload must be derived from a verified upstream receipt rather than static scheduler inputs.
9. A stale upstream receipt may trigger one deduplicated remediation dispatch to the canonical source workflow. Repeated hourly runs must not create an unbounded dispatch loop.

## Current implemented files
- `.github/workflows/healer_scheduler.yml` — sole hourly clock; validates configuration and invokes the dispatcher.
- `.github/workflows/quiet_enforcer.yml` — daily unauthorized-schedule audit.
- `app/dispatch_orchestrators.py` — config-driven cross-repository workflow dispatcher.
- `data/orchestrator_targets.json` — active dispatch target list.
- `data/summary/single_scheduler_migration.json` — machine-readable SCW migration receipt and pending-validation record.
- `templates/universal_ingestion_orchestrator.yml` — downstream event-driven orchestrator contract with adapter discovery.
- `templates/disabled_legacy_workflow.yml` — manual-only legacy workflow tombstone.
- `actions/yaml-corrector/action.yml` — YAML normalization and healer reporting.
- `.github/workflows/supercheck_core.yml` — reusable repair workflow.
- `.github/workflows/stegdeploy-publication-relay.yml` — Healer-owned hourly evidence relay for verified StegDeploy publication evidence.
- `app/relay_stegdeploy_publication.py` — validates v2 publication evidence, emits bounded consumer events, and requests one canonical remediation run when the retained receipt is stale.
- `data/summary/stegdeploy_publication_dispatch.json` — durable relay, remediation, blocker, and duplicate-suppression state.

## Managed migration scope and state

### Site
- Existing dispatch entrypoint: `.github/workflows/site-task-runner.yml`.
- Healer target is enabled with `task=all-local`.
- Site still contains its historical six-hour schedule; migration remains pending because its handoff requires exactly two operational workflows and the existing task runner must be adapted in place rather than duplicated.

### SCW
- `.github/workflows/scw_orchestrator.yml` and `.github/workflows/uptime.yml` were fully inspected.
- Both local `schedule:` triggers were removed while retaining their operational logic.
- Healer now dispatches `scw_orchestrator.yml` hourly in observation mode using `cmd=org-scan`, `orgs=StegVerse-Labs`, and `dry_run=true`.
- Healer also dispatches `uptime.yml` through the same central hourly clock.
- Runtime validation is pending; configuration does not claim successful dispatch or restored monitoring until Actions evidence is observed.
- Durable evidence commits:
  - SCW uptime migration: `e39e70f0caa2439a805444b72555a2654df4d04e`
  - SCW orchestrator migration: `caeaff52297070bdfcd55ec69b7abba7d2048e62`
  - Healer SCW activation registry: `9c554a1d70c6b80e6133faf302695bf38d0b3085`
  - Healer uptime target: `24f693933f176ade0218656265205916e3c12b00`
  - Migration receipt: `87306f88660643424a3c2dbc2d26c7ed9f6cafd4`

### StegDeploy publication relay
- Source evidence: `StegVerse-org/LLM-adapter/receipts/stegdeploy-image-publication.json`.
- Source workflow: `StegVerse-org/LLM-adapter/.github/workflows/stegdeploy-image.yml`.
- Downstream entrypoint: `StegVerse-org/core-node-runtime-demo/.github/workflows/stegdeploy-runtime-intake.yml`.
- The downstream non-Healer schedule was replaced by `repository_dispatch` event `stegdeploy-image-published` at merge `f742105877541f67a85abd7fbe23154ce4addee7`.
- The relay accepts only schema `stegdeploy.image-publication.v2`, state `PUBLISHED`, a SHA-256 digest, `consumer_pull_verified=true`, the canonical source repository identity, and a retained receipt hash.
- A publication receipt hash is dispatched once. Repeated observations become `NOOP_ALREADY_DISPATCHED`.
- The observed source receipt remains v1 after the main-branch trigger merge. The relay has truthfully retained `BLOCKED` with exact blockers.
- The remediation repair requests `stegdeploy-image.yml` through `workflow_dispatch` once for each stale source commit, records `REMEDIATION_DISPATCHED`, and then records `BLOCKED_REMEDIATION_PENDING` until the source receipt changes.
- Remediation does not fabricate publication evidence and does not dispatch the consumer event unless a valid v2 `PUBLISHED` receipt appears.
- The relay grants no provider execution, custody, deployment, publication, release, Site-activation, admissibility, or receipt-minting authority.

### Remaining initial targets
- `StegVerse-Labs/TV`
- `StegVerse-Labs/CosDen`
- `StegVerse-Labs/Continuity`

These remain disabled in the dispatch registry until their handoffs, workflow dependencies, and retained entrypoints are verified.

## Discovered tasks and blockers

### Authentication blocker
Cross-repository dispatch and private-repository auditing require `HEALER_GH_TOKEN` with repository access, Actions read/write, and Contents read. The token value is never stored in this repository; its presence and scope must be validated through controlled runs.

### Runtime validation requirements
- Controlled Healer dispatch of SCW orchestrator succeeds.
- Controlled Healer dispatch of SCW uptime succeeds.
- SCW observation dispatch remains `dry_run=true` and creates no commit or PR.
- `quiet_enforcer.yml` reports zero SCW schedules.
- StegDeploy relay retains an exact `BLOCKED`, `REMEDIATION_DISPATCHED`, `BLOCKED_REMEDIATION_PENDING`, `DISPATCHED`, or `NOOP_ALREADY_DISPATCHED` state.
- A `REMEDIATION_DISPATCHED` state must identify the stale source commit and must not repeat for that same commit.
- A future `DISPATCHED` state must correspond to a v2 `PUBLISHED` receipt and a downstream runtime-intake run with the same receipt hash and image digest.

### Required downstream work
1. Read each target repository's `*_MIRROR_HANDOFF.md` before mutation; create it first when absent.
2. Inventory every `.github/workflows/*.yml` and `.yaml` file, including schedules, cross-repo dispatches, reusable calls, and required scripts.
3. Classify each automatic workflow as retained logic, migrated logic, disabled legacy logic, or prohibited duplicate schedule.
4. Adapt a verified existing entrypoint where possible; install the universal orchestrator only when no suitable repository-specific entrypoint exists.
5. Replace obsolete workflow contents with the disabled stub only after recording the original path and migration mapping in the repo handoff.
6. Remove unauthorized schedules only after confirming central dispatch coverage and preserving required behavior.

## Ownership
- Central scheduler, templates, registry, dispatch, audit policy, evidence relays, remediation dispatch, and central receipts: `StegVerse-Labs/StegVerse-Healer`.
- Repository-specific logic and handoff accuracy: each target repository, coordinated through Healer.
- Pending secret installation or scope correction: repository/organization administrator.
- Runtime evidence observation and receipt update: successor Healer validation session.

## Permitted continuation scope
A continuation session may inspect registered target repositories, update their mirror handoffs, adapt event-driven entrypoints, migrate retained workflow logic, disable obsolete automatic triggers, update the registry, add evidence-derived relay and bounded remediation logic, and record dispatch/audit evidence. It must not blindly disable workflows, expose secrets, create unbounded retry loops, or claim activation without observed runtime evidence.

## Next activation tasks
1. Validate and merge the bounded StegDeploy remediation repair.
2. Observe the first Healer run and retain whether the source workflow dispatch was accepted.
3. Observe the resulting canonical v2 `PUBLISHED` or exact `BLOCKED` source receipt.
4. If published, verify the downstream runtime-intake receipt matches the source receipt hash and image digest.
5. Continue SCW controlled dispatch and quiet-enforcer validation.
6. Adapt Site's existing task runner only after preserving its two-workflow architecture and Healer coverage.
7. After SCW validation, scan `TV`, then `CosDen`, then `Continuity`.
8. Add StegVerse-Healer self-validation and stable machine-readable audit receipts.

## Release and ecosystem propagation
When the single-scheduler migration reaches release readiness, tag StegVerse-Healer and create verification tasks for relevant policy or integration updates in `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-Labs/stegguardian-wiki`.

## Done condition
Activation is complete when all registered targets are dispatchable through Healer, contain no unauthorized schedules, use verified repository adapters or existing entrypoints, preserve repo-local handoffs, and produce non-failing execution or intentional no-op receipts without manual reconstruction.
