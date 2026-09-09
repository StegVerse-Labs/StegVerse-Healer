# Native Email Reusable Schedule Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-Labs/StegVerse-Healer`
Parent scheduler: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`
Upstream task: `StegVerse-Labs/.github:STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream COSV: `10100000100000`
Upstream reusable identity: `RT-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream scoped handoff: `StegVerse-Labs/.github:docs/NATIVE_EMAIL_REUSABLE_HOURLY_MIRROR_HANDOFF.md`
Source merge: PR `#57` / merge `ef5d90a8c215056e055385a04534e16c49d9a3d5`
Upstream merge: `StegVerse-Labs/.github#1252` / merge `700f959dca0160f0d71d92fc391c9f262f27feea`
State: `SOURCE_INTEGRATION_MERGED / HOURLY_SLOT_CONFIGURATION_MERGED / LIVE_SCHEDULE_RECEIPT_PENDING`

## Purpose

Schedule canonical reusable-task identities through the already-existing sovereign Healer scheduler. The first scheduled reusable identity is the native email action monitor, hourly, without introducing another scheduler, mailbox monitor, polling loop, heartbeat, WorkerCoordinator, or credential route.

## Installed source

- `data/reusable_task_schedule.json` — data-driven reusable-task schedule registry.
- `app/reusable_task_scheduler.py` — extends the existing scheduler invocation with reusable-task slots.
- `app/dispatch_orchestrators.py` — compatibility entrypoint enters the extended scheduler path.
- `tests/test_reusable_task_scheduler.py` — proves hourly binding and same-slot idempotency.
- `README.md` — documents reusable-task scheduling responsibility and timer semantics.

## Hourly contract

`RT-NATIVE-EMAIL-ACTION-MONITOR-001` is eligible in every UTC hour. Its deterministic invocation id includes the UTC `YYYYMMDDTHH` slot. If the matching retained reusable-task receipt already exists, the scheduler records `ALREADY_RAN_THIS_SCHEDULE_SLOT` and does not invoke the task again.

The schedule invokes `.github/scripts/trigger_reusable_task.py` using the existing tracking Task ID `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` and COSV `10100000100000`. The local `.github` repository root is bound as source/runtime root; `STEGVERSE_REPO_ROOTS_JSON` is passed so the existing consumer can resolve already-materialized TVC and StegOps provider-owner repositories.

## Validation evidence

PR #57 exact head `99e63e6e01962232125f70becec5e21eac11ae30` passed Test Readiness run `34332190725`. The earlier run `34332041418` exposed only a test-fixture aliasing defect: the mocked base scheduler returned the same mutable receipt object for two invocations, causing the first result to appear overwritten by the second same-slot result. The test was corrected to provide a fresh base receipt per invocation; scheduler production semantics were unchanged.

The coordinated `.github` PR #1252 exact head passed Heartbeat Worker Project run `34332023132`, organization-control run `34332023277`, and Deterministic Repository Suite run `34332023168` before merge.

## Evidence boundary

Source integration, hourly schedule configuration, same-slot idempotency, tests, README maintenance, and both coordinated merges are complete. Authentic live hourly operation still requires a retained runtime reusable-task receipt produced by the resident Healer scheduler. Provider authorization, mailbox access, corrective-task completion, and downstream execution retain their existing independent evidence predicates.
