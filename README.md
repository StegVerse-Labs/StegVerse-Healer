# StegVerse-Healer

StegVerse-Healer is the ecosystem's central scheduling, observation, repair-dispatch, and continuity service.

## Authority boundary

This repository is the only managed StegVerse repository permitted to own scheduled GitHub Actions workflows. Downstream repositories expose manual or bounded event-driven entrypoints and retain their own repository-specific logic and evidence.

Healer dispatch does not itself grant provider execution, deployment, custody, publication, release, Site activation, admissibility, or receipt-minting authority.

## Current capabilities

- Central hourly scheduler driven by `data/orchestrator_targets.json`.
- Data-driven reusable-task scheduling through `data/reusable_task_schedule.json` inside that same sovereign scheduler path; schedule slots are receipt-idempotent so an hourly reusable task runs at most once per UTC hour.
- `RT-NATIVE-EMAIL-ACTION-MONITOR-001` is scheduled hourly through the existing reusable-task trigger and canonical `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` path; no second mailbox monitor or scheduler is created.
- Unauthorized downstream schedule auditing.
- Configured cross-repository workflow dispatch.
- YAML correction and reusable repair workflows.
- Evidence-derived StegDeploy publication relay.
- Durable machine-readable migration, dispatch, blocker, and continuity records.

## Continuation records

Read these before modifying scheduling or dispatch behavior:

- `docs/HEALER_MIRROR_HANDOFF.md`
- `docs/HEALER_ACTIVATION_PLAN.md`
- `data/orchestrator_targets.json`
- `data/reusable_task_schedule.json`
- `data/summary/single_scheduler_migration.json`

## Validation

Repository validation is performed by the `Test Readiness` workflow. Runtime activation claims require observed resident/runtime evidence and retained receipts; configuration or source merge alone is not activation proof.
