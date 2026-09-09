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
State: `SOURCE_INTEGRATION_MERGED / HOURLY_SLOT_CONFIGURATION_MERGED / SOURCE_RUNTIME_COLLAPSE_REPAIR_IN_PROGRESS / LIVE_SCHEDULE_RECEIPT_PENDING`

## Purpose

Schedule canonical reusable-task identities through the already-existing sovereign Healer scheduler. The first scheduled reusable identity is the native email action monitor, hourly, without introducing another scheduler, mailbox monitor, polling loop, heartbeat, WorkerCoordinator, or credential route.

## Installed source

- `data/reusable_task_schedule.json` — data-driven reusable-task schedule registry.
- `app/reusable_task_scheduler.py` — extends the existing scheduler invocation with reusable-task slots.
- `app/dispatch_orchestrators.py` — compatibility entrypoint enters the extended scheduler path.
- `tests/test_reusable_task_scheduler.py` — proves hourly binding, resident-runtime separation, and same-slot idempotency.
- `README.md` — documents reusable-task scheduling responsibility and resident-runtime semantics.

## Hourly contract

`RT-NATIVE-EMAIL-ACTION-MONITOR-001` is eligible in every UTC hour. Its deterministic invocation id includes the UTC `YYYYMMDDTHH` slot. If the matching retained reusable-task receipt already exists in the resident heartbeat runtime, the scheduler records `ALREADY_RAN_THIS_SCHEDULE_SLOT` and does not invoke the task again.

The schedule invokes `.github/scripts/trigger_reusable_task.py` using the existing tracking Task ID `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` and COSV `10100000100000`. The local `.github` repository remains the source root. The resident heartbeat runtime supplied through `STEGVERSE_HEARTBEAT_ROOT` is the runtime root and receipt destination. The two roots must not collapse into the same source checkout. If the resident runtime is unavailable, the scheduled task fails closed with `RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED` instead of treating source as runtime.

`STEGVERSE_REPO_ROOTS_JSON` remains the nonsecret local repository map used by the existing native-email consumer to resolve already-materialized TVC and StegOps provider-owner repositories.

## Defect repaired in current continuation

The first merged hourly implementation passed the local `.github` source checkout as both `source_root` and `runtime_root`, and wrote reusable-task slot receipts under the source checkout. That topology could make a source tree appear to be the resident execution surface and was incompatible with the separated resident runtime model.

The current repair:

- resolves the runtime from `STEGVERSE_HEARTBEAT_ROOT`;
- passes the local `.github` checkout only as `source_root`;
- passes the resident heartbeat runtime only as `runtime_root`;
- stores `receipts/reusable-task/<slot>.latest.json` under the resident runtime;
- blocks rather than falling back when the resident runtime is absent;
- retains same-UTC-hour idempotency using the resident receipt.

## Prior validation evidence

PR #57 exact head `99e63e6e01962232125f70becec5e21eac11ae30` passed Test Readiness run `34332190725`. The earlier run `34332041418` exposed only a test-fixture aliasing defect and was repaired without weakening scheduler production semantics.

The coordinated `.github` PR #1252 exact head passed Heartbeat Worker Project run `34332023132`, organization-control run `34332023277`, and Deterministic Repository Suite run `34332023168` before merge.

## Evidence boundary

Reusable identity, hourly schedule construction, standing Healer resident recurrence, source/runtime separation, same-slot idempotency, and resident receipt placement must all be merged and validated before live execution is claimed. Authentic live hourly operation still requires a retained resident reusable-task receipt plus the corresponding native-email/TV-TVC Gmail provider evidence for a mailbox-processing claim.
