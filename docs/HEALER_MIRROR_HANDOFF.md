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
- `.github/workflows/stegdeploy-publication-relay.yml` — Healer-owned hourly evidence relay for a newly verified StegDeploy publication receipt.
- `app/relay_stegdeploy_publication.py` — validates the upstream v2 receipt, suppresses duplicate dispatch, and emits a bounded repository event.
- `data/summary/stegdeploy_publication_dispatch.json` — durable relay state and blocker receipt.

## Managed migration scope and state

### Site
- Existing dispatch entrypoint: `.github/workflows/site-task-runner.yml`.
- Healer target is enabled with `task=all-local`.
- Site still contains its historical six-hour schedule; migration remains pending because its handoff requires exactly two operational workflows and the existing task runner must be adapted in place rather than duplicated.

### SCW
- `.github/workflows/scw_orchestrator.yml` and `.github/workflows/uptime.yml` were fully inspected.
- Both local `schedule:` triggers were removed while retaining their operational logic.
- Healer now dispatches `scw_orchestrator.yml` hourly in observation mode using:
  - `cmd=org-scan`
  - `orgs=StegVerse-Labs`
  - `dry_run=true`
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
- Downstream entrypoint: `StegVerse-org/core-node-runtime-demo/.github/workflows/stegdeploy-runtime-intake.yml`.
- The downstream non-Healer schedule was removed and replaced by `repository_dispatch` event `stegdeploy-image-published` at merge `f742105877541f67a85abd7fbe23154ce4addee7`.
- The Healer relay accepts only a source receipt with:
  - schema `stegdeploy.image-publication.v2`;
  - state `PUBLISHED`;
  - SHA-256 image digest;
  - `consumer_pull_verified=true`;
  - source repository identity `StegVerse-org/LLM-adapter`;
  - a retained receipt hash.
- A receipt hash is dispatched once. Repeated observations become `NOOP_ALREADY_DISPATCHED`.
- The relay grants no provider execution, custody, deployment, publication, release, or Site-activation authority.
- Current source receipt remains v1, so the first relay run is expected to retain `BLOCKED` until the canonical image workflow produces a v2 receipt.

### Remaining initial targets
- `StegVerse-Labs/TV`
- `StegVerse-Labs/CosDen`
- `StegVerse-Labs/Continuity`

These remain disabled in the dispatch registry until their handoffs, workflow dependencies, and retained entrypoints are verified.

## Discovered tasks and blockers

### Authentication blocker
Cross-repository dispatch and private-repository auditing require `HEALER_GH_TOKEN` with repository access and Actions read/write plus Contents read. The token value is never stored in this repository; its presence and scope must be validated through a controlled run.

### Runtime validation requirements
- Controlled Healer dispatch of SCW orchestrator succeeds.
- Controlled Healer dispatch of SCW uptime succeeds.
- SCW job summaries show `workflow_dispatch` authority and Healer scheduling authority.
- SCW observation dispatch uses `dry_run=true` and creates no commit or PR.
- `quiet_enforcer.yml` reports zero SCW schedules.
- The resulting run IDs and conclusions are added to `data/summary/single_scheduler_migration.json`.
- StegDeploy relay retains an exact `BLOCKED`, `DISPATCHED`, or `NOOP_ALREADY_DISPATCHED` state.
- A future `DISPATCHED` state must correspond to a v2 `PUBLISHED` receipt and a downstream runtime-intake run with the same receipt hash and image digest.

### Required downstream work
1. Read each target repository's `*_MIRROR_HANDOFF.md` before mutation; create it first when absent.
2. Inventory every `.github/workflows/*.yml` and `.yaml` file, including schedules, cross-repo dispatches, reusable calls, and required scripts.
3. Classify each automatic workflow as retained logic, migrated logic, disabled legacy logic, or prohibited duplicate schedule.
4. Adapt a verified existing entrypoint where possible; install the universal orchestrator only when no suitable repository-specific entrypoint exists.
5. Replace obsolete workflow contents with the disabled stub only after recording the original path and migration mapping in the repo handoff.
6. Remove unauthorized schedules only after confirming central dispatch coverage in configuration and preserving required behavior.

## Ownership
- Central scheduler, templates, registry, dispatch, audit policy, evidence relays, and central receipts: `StegVerse-Labs/StegVerse-Healer`.
- Repository-specific logic and handoff accuracy: each target repository, coordinated through Healer.
- Pending secret installation or scope correction: repository/organization administrator.
- Runtime evidence observation and receipt update: successor Healer validation session.

## Permitted continuation scope
A continuation session may inspect registered target repositories, update their mirror handoffs, adapt event-driven entrypoints, migrate retained workflow logic, disable obsolete automatic triggers, update the registry, add evidence-derived relay logic, and record dispatch/audit evidence. It must not blindly disable workflows whose purpose, dependencies, and replacement path have not been reconstructed, expose secrets, or claim activation without observed runtime evidence.

## Next activation tasks
1. Validate and merge the StegDeploy publication relay.
2. Observe its first Healer-owned run and retain the exact source-receipt blocker or successful dispatch evidence.
3. Observe or initiate a controlled Healer scheduler dispatch for scope `scw`.
4. Verify both configured SCW targets were accepted by GitHub Actions and remained observation-only where applicable.
5. Run the quiet enforcer and record a zero-schedule SCW result.
6. Update `data/summary/single_scheduler_migration.json` with run IDs, conclusions, and timestamps.
7. Adapt Site's existing task runner to remove its local schedule only after preserving its two-workflow architecture and Healer dispatch coverage.
8. After SCW validation, scan `TV`, then `CosDen`, then `Continuity`.
9. Add StegVerse-Healer self-validation and stable machine-readable audit receipts.

## Release and ecosystem propagation
When the single-scheduler migration reaches release readiness, tag StegVerse-Healer and create verification tasks for relevant policy or integration updates in:
- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `StegVerse-Labs/stegguardian-wiki`

## Done condition
Activation is complete when all registered targets are dispatchable through Healer, contain no unauthorized schedules, use real repository adapters or verified existing entrypoints rather than placeholder scaffolding, preserve repo-local handoffs, and produce non-failing execution or intentional no-op receipts without manual reconstruction.
