# Native Email Reusable Schedule Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-Labs/StegVerse-Healer`
Parent scheduler: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`
Upstream task: `StegVerse-Labs/.github:STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream COSV: `10100000100000`
Upstream reusable identity: `RT-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream scoped handoff: `StegVerse-Labs/.github:docs/NATIVE_EMAIL_REUSABLE_HOURLY_MIRROR_HANDOFF.md`

## Purpose

Schedule canonical reusable-task identities through the already-existing sovereign Healer scheduler. The first scheduled reusable identity is the native email action monitor, hourly, without introducing another scheduler, mailbox monitor, polling loop, heartbeat, WorkerCoordinator, or credential route.

## Installed source

- `data/reusable_task_schedule.json` — data-driven reusable-task schedule registry.
- `app/reusable_task_scheduler.py` — extends the existing scheduler invocation with reusable-task slots.
- `app/dispatch_orchestrators.py` — compatibility entrypoint now enters the extended scheduler path.
- `tests/test_reusable_task_scheduler.py` — proves hourly binding and same-slot idempotency.
- `README.md` — documents reusable-task scheduling responsibility and timer semantics.

## Hourly contract

`RT-NATIVE-EMAIL-ACTION-MONITOR-001` is eligible in every UTC hour. Its deterministic invocation id includes the UTC `YYYYMMDDTHH` slot. If the matching retained reusable-task receipt already exists, the scheduler records `ALREADY_RAN_THIS_SCHEDULE_SLOT` and does not invoke the task again.

The schedule invokes `.github/scripts/trigger_reusable_task.py` using the existing tracking Task ID `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` and COSV `10100000100000`. The local `.github` repository root is bound as source/runtime root; `STEGVERSE_REPO_ROOTS_JSON` is passed so the existing consumer can resolve already-materialized TVC and StegOps provider-owner repositories.

## Evidence boundary

Source merge and deterministic tests prove schedule construction only. Authentic live hourly operation requires a retained runtime reusable-task receipt produced by the resident Healer scheduler. Provider authorization, mailbox access, corrective-task completion, and downstream execution retain their existing independent evidence predicates.

## Current state

Source implementation is on `feat/native-email-reusable-hourly-20260909`; validation/merge are pending. No live schedule receipt is claimed yet.
