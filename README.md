# StegVerse-Healer

StegVerse-Healer is the ecosystem's central scheduling, observation, repair-dispatch, and continuity service.

## Authority boundary

This repository is the only managed StegVerse repository permitted to own scheduled GitHub Actions workflows. Downstream repositories expose manual or bounded event-driven entrypoints and retain their own repository-specific logic and evidence.

Healer dispatch does not itself grant provider execution, deployment, custody, publication, release, Site activation, admissibility, or receipt-minting authority.

## Current capabilities

- Central hourly scheduler driven by `data/orchestrator_targets.json`.
- Data-driven reusable-task scheduling through `data/reusable_task_schedule.json` inside that same sovereign scheduler path; a UTC-hour slot is idempotent only after its retained reusable-task receipt records `AUTOMATABLE_STEPS_EXHAUSTED`. Failed or boundary-only receipts remain retryable instead of poisoning the slot, but retry cadence and attempts are bounded by the task's schedule record.
- Scheduled reusable tasks keep source and resident runtime distinct: task source comes from the already-materialized local repository map, execution state and reusable-task receipts live under the resident runtime identified by `STEGVERSE_HEARTBEAT_ROOT`, and a missing resident runtime blocks rather than falling back to the source checkout.
- `RT-NATIVE-EMAIL-ACTION-MONITOR-001` is scheduled hourly through the existing reusable-task trigger and canonical `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` path. A failed slot may retry no sooner than every 15 minutes and at most four times in that UTC-hour slot; a new hour receives a new deterministic slot ID. No second mailbox monitor or scheduler is created.
- The native-email reusable slot may receive the already-materialized KnowledgeVault path through `STEGVERSE_KV_ROOT` or `STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT`. These are non-secret local path bindings only; Healer does not mount a provider or acquire credentials. Missing KV materialization blocks failure-email archival rather than bypassing KV persistence; retry state suppresses tight provider loops while preserving bounded recovery.
- For governed native-email provider mutation, the scheduler may augment its already-local repository map from the existing `SV-DN1-PRODUCTION-SOURCE-PREP-001` v2 receipt. It accepts the SDK, StegCore, Core-Lite, and Master Records roots only when that receipt is `COMPLETE`, all four SHA-256 source identities are present, migration anchors were verified, no network/GitHub/credential source acquisition occurred, and required runtime marker files still exist. An absent or invalid source-prep receipt adds no roots and creates no fallback fetch.
- Unauthorized downstream schedule auditing.
- Configured cross-repository workflow dispatch.
- YAML correction and reusable repair workflows.
- Evidence-derived StegDeploy publication relay.
- Durable machine-readable migration, dispatch, blocker, and continuity records.

## Continuation records

Read these before modifying scheduling or dispatch behavior:

- `docs/HEALER_MIRROR_HANDOFF.md`
- `docs/NATIVE_EMAIL_REUSABLE_SCHEDULE_MIRROR_HANDOFF.md`
- `docs/HEALER_ACTIVATION_PLAN.md`
- `data/orchestrator_targets.json`
- `data/reusable_task_schedule.json`
- `data/summary/single_scheduler_migration.json`

## Validation

Repository validation is performed by the `Test Readiness` workflow. Runtime activation claims require observed resident/runtime evidence and retained receipts; configuration or source merge alone is not activation proof.