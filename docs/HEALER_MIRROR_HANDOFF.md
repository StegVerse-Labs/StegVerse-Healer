# StegVerse-Healer Mirror Handoff

## Active goal

- Goal ID: `SV-HEALER-SINGLE-SCHEDULER-001`
- Goal: make `StegVerse-Labs/StegVerse-Healer` the sole approved clock for managed repositories while preserving repository-specific event entrypoints, deterministic receipts, and fail-closed continuation.
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Branch: `main`
- State: `MULTI_TARGET_IMPLEMENTED_PENDING_RUNTIME_VALIDATION`

## Authoritative records

- `docs/HEALER_MIRROR_HANDOFF.md`
- `docs/HEALER_ACTIVATION_PLAN.md`
- `registry/managed_repos.yml`
- `data/orchestrator_targets.json`
- `data/summary/single_scheduler_migration.json`
- `.github/workflows/healer_scheduler.yml`
- `.github/workflows/quiet_enforcer.yml`
- `app/dispatch_orchestrators.py`

## Durable policy

1. Healer is the only approved repository containing managed `schedule:` triggers.
2. Downstream workflows retain `workflow_dispatch`, bounded push/workflow events, or repository dispatch as required by existing architecture.
3. Existing verified entrypoints are adapted instead of adding duplicate generic orchestrators.
4. Missing runtime evidence never becomes successful activation.
5. Cross-repository dispatch does not imply mutation, deployment, release, custody, or provider authority.
6. Obsolete workflows are stubbed or deleted only after retained behavior and provenance are durably mapped.
7. `data/orchestrator_targets.json` owns ordinary cadence configuration; dedicated evidence relays may exist when dispatch inputs must be derived from verified upstream receipts.

## Implemented central components

- `.github/workflows/healer_scheduler.yml`: hourly clock with manual scope selection and scheduled/manual event-mode propagation.
- `app/dispatch_orchestrators.py`: enabled-target filtering, aliases, cadence hours, deterministic inputs, aggregated failure reporting, and manual cadence bypass.
- `.github/workflows/quiet_enforcer.yml`: unauthorized downstream schedule audit.
- `data/orchestrator_targets.json`: active target registry.
- `data/summary/single_scheduler_migration.json`: machine-readable migration state and pending-validation receipt.
- `templates/universal_ingestion_orchestrator.yml`: adapter-based fallback contract when no suitable existing entrypoint exists.
- `templates/disabled_legacy_workflow.yml`: manual-only tombstone for proven obsolete workflows.
- `.github/workflows/supercheck_core.yml` and `actions/yaml-corrector/action.yml`: reusable workflow repair path.

## Managed targets

### SCW

- `.github/workflows/scw_orchestrator.yml`: local schedule removed; Healer cadence `0,6,12,18` UTC; observation inputs `cmd=org-scan`, `orgs=StegVerse-Labs`, `dry_run=true`.
- `.github/workflows/uptime.yml`: local hourly schedule removed; Healer hourly dispatch configured.
- Target commits: `caeaff52297070bdfcd55ec69b7abba7d2048e62`, `e39e70f0caa2439a805444b72555a2654df4d04e`.
- State: implemented, runtime validation pending.

### TV

- `.github/workflows/tv_self_heal.yml`: local daily schedule removed; `workflow_dispatch` and bounded path-triggered push retained.
- Healer daily cadence at 06:00 UTC.
- Direct commit remains disabled through the reusable Healer call.
- Target commit: `9db4f33ad0e6545dcbeb7da407c71707a41fb33c`.
- State: implemented, runtime validation pending.

### Continuity

- `.github/workflows/continuity.yml`: local six-hour schedule removed; manual and main-branch push retained.
- Healer cadence `0,6,12,18` UTC.
- Workflow repair commit `282f09fd4abb41afa88a209bfbc248a369e15cbe` also repairs malformed OIDC extraction and TV access-token output, adds fail-closed configuration/token checks, concurrency, timeout, rebase-before-push, and summary evidence.
- Continuity handoff commit: `7b190c04786240d951afbf3ca536e8a991a3c61c`.
- Healer registry commit: `0c57885b5268776a1f746f751eb960528bc90d06`.
- Migration receipt commit: `081de304be91a74d98a54715e89452723cffa0ba`.
- State: implemented, runtime validation pending.

### Site

- Existing `.github/workflows/site-task-runner.yml` is already registered with `task=all-local` at UTC hours `0,6,12,18`.
- Site still contains its historical local schedule.
- Site must remain at exactly two operational workflows, so the existing task runner must be updated in place; no third orchestrator is permitted.
- State: central coverage configured, downstream schedule removal pending.

### CosDen

- No applicable `*_MIRROR_HANDOFF.md` was found by repository search in the current execution pass.
- No verified dispatch entrypoint has been established.
- State: disabled; handoff creation is the first permitted mutation.

## Dedicated StegDeploy evidence relay

- `.github/workflows/stegdeploy-publication-relay.yml` and `app/relay_stegdeploy_publication.py` implement an evidence-derived relay.
- Source receipt: `StegVerse-org/LLM-adapter/receipts/stegdeploy-image-publication.json`.
- Destination event: `stegdeploy-image-published` to `StegVerse-org/core-node-runtime-demo`.
- Only a v2 `PUBLISHED` receipt with verified consumer pull, source identity, digest, and receipt hash may dispatch.
- Duplicate receipt hashes become `NOOP_ALREADY_DISPATCHED`; unavailable evidence remains `BLOCKED`.
- This grants no deployment, publication, custody, execution, provider, or release authority.

## Actual blockers and release conditions

### `HEALER_GH_TOKEN`

Owner: repository or organization administrator.

Release condition: a controlled scheduler run proves Actions dispatch and Contents read across configured repositories without exposing the token.

### Runtime dispatch evidence

Owner: Healer scheduler and receipt updater.

Release condition for each target:

- downstream run exists;
- jobs and logs are inspected;
- configured inputs and event source match;
- mutation posture matches policy;
- run ID, conclusion, timestamp, and commit are persisted in `data/summary/single_scheduler_migration.json`.

### Quiet-enforcer evidence

Owner: `.github/workflows/quiet_enforcer.yml`.

Release condition: a persisted receipt reports zero unauthorized schedules for SCW, TV, and Continuity, and later Site and CosDen.

### Site local clock

Owner: `StegVerse-Labs/Site/.github/workflows/site-task-runner.yml`.

Release condition: remove only the `schedule:` trigger while retaining `workflow_dispatch`, `workflow_run`, task inputs, validation, generated-state commit, deployment, and evidence paths; then update `docs/SITE_MIRROR_HANDOFF.md`.

### CosDen discovery

Owner: successor Healer migration task.

Release condition: create one authoritative mirror handoff, inventory workflows and dependencies, identify a real entrypoint, migrate any clock, and register it only after static validation.

## Automation state model

Every migration target must resolve to one of:

- `COMPLETE`: runtime and quiet-enforcer evidence persisted;
- `BLOCKED`: explicit missing authority, credential, configuration, or dependency with observable release condition;
- `RETRY`: transient hosted failure with bounded retry evidence;
- `REVIEW_REQUIRED`: behavior cannot be safely migrated without human authority or dependency reconstruction;
- `FAILED`: deterministic implementation or validation failure.

Configuration alone is `IMPLEMENTED_PENDING_RUNTIME_VALIDATION`, not `COMPLETE`.

## Next executable tasks

1. `StegVerse-Labs/Site/.github/workflows/site-task-runner.yml`: remove its local cron in place and update `docs/SITE_MIRROR_HANDOFF.md`.
2. `StegVerse-Labs/StegVerse-Healer/.github/workflows/healer_scheduler.yml`: controlled manual scopes `scw`, `tv`, and `continuity` when token authority is available.
3. `StegVerse-Labs/StegVerse-Healer/.github/workflows/quiet_enforcer.yml`: persist a machine-readable audit receipt rather than logs alone.
4. `StegVerse-Labs/CosDen`: create the missing mirror handoff before any workflow mutation.
5. `data/summary/single_scheduler_migration.json`: record hosted evidence as it becomes available.

## Release and propagation

A Healer release or tag is prohibited until configured targets are runtime-validated and the quiet-enforcer receipt is zero-violation. At genuine release readiness, verify required policy or integration propagation to:

- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `StegVerse-Labs/stegguardian-wiki`

No propagation is currently claimed.

## Archive condition

The active goal remains open. Repository state preserves continuation, but archival is prohibited until Site and CosDen are assigned durable implementations, hosted validation observers are active, and unresolved targets have machine-owned release conditions.

## Progress denominator

Required deliverables: central scheduler, dispatcher, target registry, migration receipt, quiet-enforcer receipt, SCW migration, TV migration, Continuity migration, Site migration, CosDen migration, runtime validation evidence, release/propagation gate = 12.

- Task completion: 7/12 = 58%
- Developed files: 9/11 = 82%
- Validation completion: 4/9 = 44%
- Integration completion: 4/7 = 57%
- Goal activation: 58%
- Scaffolding or stubs: 2
- Missing required files: 2
