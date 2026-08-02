# StegVerse-Healer Mirror Handoff

## Active goal

- Goal ID: `SV-HEALER-SINGLE-SCHEDULER-001`
- Goal: make `StegVerse-Labs/StegVerse-Healer` the sole approved clock for managed repositories while preserving repository-specific event entrypoints, deterministic receipts, and fail-closed continuation.
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Branch: `main`
- State: `MULTI_TARGET_IMPLEMENTED_PENDING_HOSTED_VALIDATION`

## Authoritative records

- `docs/HEALER_MIRROR_HANDOFF.md`
- `docs/HEALER_ACTIVATION_PLAN.md`
- `registry/managed_repos.yml`
- `data/orchestrator_targets.json`
- `data/summary/single_scheduler_migration.json`
- `data/summary/quiet_enforcer_latest.json` when generated
- `.github/workflows/healer_scheduler.yml`
- `.github/workflows/quiet_enforcer.yml`
- `app/dispatch_orchestrators.py`
- `app/audit_schedules.py`

## Durable policy

1. Healer is the only approved repository containing managed `schedule:` triggers.
2. Downstream workflows retain `workflow_dispatch`, bounded push/workflow events, or repository dispatch as required by existing architecture.
3. Existing verified entrypoints are adapted instead of adding duplicate generic orchestrators.
4. Missing runtime evidence never becomes successful activation.
5. Cross-repository dispatch does not imply mutation, deployment, release, custody, or provider authority.
6. Obsolete workflows are stubbed or deleted only after retained behavior and provenance are durably mapped.
7. `data/orchestrator_targets.json` owns ordinary cadence configuration; dedicated evidence relays may exist when dispatch inputs must be derived from verified upstream receipts.
8. Audit-only repositories remain visible to the quiet enforcer without being assigned nonexistent dispatch workflows.

## Implemented central components

- `.github/workflows/healer_scheduler.yml`: hourly clock with manual scope selection and scheduled/manual event-mode propagation.
- `app/dispatch_orchestrators.py`: enabled-target filtering, aliases, cadence hours, deterministic inputs, aggregated failure reporting, and manual cadence bypass.
- `.github/workflows/quiet_enforcer.yml`: fail-closed managed-repository schedule audit, stable receipt persistence, artifact upload, commit-on-material-change, and job summary.
- `app/audit_schedules.py`: GitHub API workflow inventory, SHA-256 capture, unauthorized-schedule detection, explicit five-state classification, next-task output, and duplicate-state suppression.
- `data/orchestrator_targets.json`: active target and audit-only registry.
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
- `data/site-orchestration-state.json` currently records an `OBSERVED_BLOCKED` active sequence, no admitted tasks, external tasks disallowed, and external session ownership disallowed.
- State: central coverage configured; local schedule removal blocked until Site orchestration admits the task or reaches its terminal idle state.

### CosDen

- `docs/COSDEN_MIRROR_HANDOFF.md` created in commit `0d90757f738ac165cb99ad7e1b38f7faab91eb0f` and reconciled in commit `b90916883e4a25a260184eebb542e2472389fedd`.
- `StegVerse-Labs/StegDB` is the canonical owner for CosDen content under `canonical/cosden`.
- `StegVerse-Labs/StegDB/docs/architecture/decisions/CosDen-Submodule-Retirement-v1.md` establishes that the former external/submodule bridge is retired and superseded.
- The nonexistent `ingestion-orchestrator.yml` placeholder was removed from dispatch semantics.
- Registry commit `072e5aca80406e44bdbea6f8b1c81c690eaf9848` classifies CosDen as `audit_only: true`, `enabled: false`, with canonical owner `StegVerse-Labs/StegDB`.
- State: developed and integrated as audit-only; hosted workflow inventory validation pending.

## Quiet-enforcer receipt automation

- Script commit: `e00757db076257e2c6e5258e7c17d7b0c45c955f`.
- Workflow commit: `0ef344f703589c3fddf14539562688433dc8740a`.
- Output: `data/summary/quiet_enforcer_latest.json`.
- Artifact retention: 90 days.
- States: `COMPLETE`, `BLOCKED`, `RETRY`, `REVIEW_REQUIRED`, `FAILED`.
- Duplicate prevention: unchanged stable projections preserve the prior observation metadata and avoid a new commit.
- Fail-closed rule: any violation, blocked repository, retry state, review-required state, missing receipt, or invalid schema fails the workflow.
- Current hosted evidence: none; commit-status inspection returned no statuses for the workflow commit, so no passing audit is claimed.

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

Release condition: a controlled scheduler or quiet-enforcer run proves Actions dispatch and Contents read across configured repositories without exposing the token.

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

Release condition: `data/summary/quiet_enforcer_latest.json` exists, validates, and reports `COMPLETE` with zero violations for every configured target and audit-only repository.

### Site local clock

Owner: Site repository orchestration and `StegVerse-Labs/Site/.github/workflows/site-task-runner.yml`.

Release condition: Site orchestration admits the scheduler migration or reaches the exact terminal idle statement; then remove only the `schedule:` trigger while retaining `workflow_dispatch`, `workflow_run`, task inputs, validation, generated-state commit, deployment, and evidence paths, and update `docs/SITE_MIRROR_HANDOFF.md`.

### CosDen audit

Owner: Healer quiet enforcer.

Release condition: the hosted receipt contains the exact CosDen workflow inventory and either zero violations or a deterministic non-COMPLETE state with a next executable task.

## Automation state model

Every migration target must resolve to one of:

- `COMPLETE`: runtime and quiet-enforcer evidence persisted;
- `BLOCKED`: explicit missing authority, credential, configuration, or dependency with observable release condition;
- `RETRY`: transient hosted failure with bounded retry evidence;
- `REVIEW_REQUIRED`: behavior cannot be safely migrated without human authority or dependency reconstruction;
- `FAILED`: deterministic implementation or validation failure.

Configuration alone is `IMPLEMENTED_PENDING_RUNTIME_VALIDATION`, not `COMPLETE`.

## Next executable tasks

1. `.github/workflows/quiet_enforcer.yml`: run or observe the first hosted receipt-producing audit; inspect its jobs, logs, artifact, and committed state.
2. `data/summary/single_scheduler_migration.json`: append the quiet-enforcer run ID, result, timestamp, and exact repository states.
3. `.github/workflows/healer_scheduler.yml`: controlled manual scopes `scw`, `tv`, and `continuity` when token authority is available.
4. `StegVerse-Labs/Site/data/site-orchestration-state.json`: wait for machine admission or terminal idle state before mutating `site-task-runner.yml`.
5. `StegVerse-Labs/CosDen/docs/COSDEN_MIRROR_HANDOFF.md`: update only after the hosted audit produces exact workflow evidence.

## Release and propagation

A Healer release or tag is prohibited until configured targets are runtime-validated and the quiet-enforcer receipt is zero-violation. At genuine release readiness, verify required policy or integration propagation to:

- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `StegVerse-Labs/stegguardian-wiki`

No propagation is currently claimed.

## Archive condition

The active goal remains open. Archival is prohibited until hosted observers are active, Site is durably admitted or blocked with a machine observer, and all registered/audit-only targets have deterministic runtime or audit states.

## Progress denominator

Required deliverables: central scheduler, dispatcher, target registry, migration receipt, quiet-enforcer receipt automation, SCW migration, TV migration, Continuity migration, Site migration, CosDen migration, runtime validation evidence, release/propagation gate = 12.

- Task completion: 8/12 = 67%
- Developed files: 11/11 = 100%
- Validation completion: 4/9 = 44%
- Integration completion: 5/7 = 71%
- Goal activation: 62%
- Scaffolding or stubs: 0
- Missing required files: 1 runtime-generated quiet-enforcer receipt
