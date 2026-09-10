# Native Email Reusable Schedule Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-Labs/StegVerse-Healer`
Parent scheduler: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`
Upstream task: `StegVerse-Labs/.github:STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream COSV: `10100000100000`
Upstream reusable identity: `RT-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream scoped handoff: `StegVerse-Labs/.github:docs/NATIVE_EMAIL_REUSABLE_HOURLY_MIRROR_HANDOFF.md`
Source merge: PR `#57` / merge `ef5d90a8c215056e055385a04534e16c49d9a3d5`
Resident runtime-root merge: PR `#58` / merge `a0f6daeaf33198f26e358c7b124fc9f80aad8b6b`
Upstream reusable source merge: `StegVerse-Labs/.github#1252` / merge `700f959dca0160f0d71d92fc391c9f262f27feea`
Upstream standing recurrence merge: `StegVerse-Labs/.github#1259` / merge `569b6dde49cc9f568c0a24daf9fc723eee807b6f`
Upstream WorkerCoordinator rearm merge: `StegVerse-Labs/.github#1273` / merge `438aeb9a4b187419ea3a91984ed0436c89b26819`
State: `SOURCE_INTEGRATION_MERGED / HOURLY_SLOT_CONFIGURATION_MERGED / SOURCE_RUNTIME_SEPARATION_MERGED / STANDING_RECURRENCE_AND_REARM_MERGED / KV_PATH_FORWARDING_IN_VALIDATION / LIVE_SCHEDULE_AND_KV_RECEIPT_PENDING`

## Purpose

Schedule canonical reusable-task identities through the already-existing sovereign Healer scheduler. The first scheduled reusable identity is the native email action monitor, hourly, without introducing another scheduler, mailbox monitor, polling loop, heartbeat, WorkerCoordinator, or credential route.

## Installed source

- `data/reusable_task_schedule.json` — data-driven reusable-task schedule registry.
- `app/reusable_task_scheduler.py` — extends the existing scheduler invocation with reusable-task slots and forwards already-materialized non-secret KV path bindings when present.
- `app/dispatch_orchestrators.py` — compatibility entrypoint enters the extended scheduler path.
- `tests/test_reusable_task_scheduler.py` — proves hourly binding, resident-runtime separation, and same-slot idempotency.
- `tests/test_reusable_task_kv_env.py` — proves KV path forwarding into the reusable-task invocation.
- `README.md` — documents reusable-task scheduling responsibility, resident-runtime semantics, and KV path forwarding boundary.

## Hourly contract

`RT-NATIVE-EMAIL-ACTION-MONITOR-001` is eligible in every UTC hour. Its deterministic invocation id includes the UTC `YYYYMMDDTHH` slot. If the matching retained reusable-task receipt already exists in the resident heartbeat runtime, the scheduler records `ALREADY_RAN_THIS_SCHEDULE_SLOT` and does not invoke the task again.

The schedule invokes `.github/scripts/trigger_reusable_task.py` using the existing tracking Task ID `STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001` and COSV `10100000100000`. The local `.github` repository remains the source root. The resident heartbeat runtime supplied through `STEGVERSE_HEARTBEAT_ROOT` is the runtime root and receipt destination. The two roots must not collapse into the same source checkout. If the resident runtime is unavailable, the scheduled task fails closed with `RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED` instead of treating source as runtime.

`STEGVERSE_REPO_ROOTS_JSON` remains the non-secret local repository map used by the existing native-email consumer to resolve already-materialized TVC and StegOps provider-owner repositories.

## KV persistence path forwarding

The upstream native-email task now requires normalized GitHub failure observations to be persisted to an already-materialized KnowledgeVault before the corresponding live Gmail messages may be archived. Healer does not mount KV, discover provider credentials, or perform the KV write itself. It forwards only already-present non-secret local path bindings:

```text
STEGVERSE_KV_ROOT
STEGVERSE_KV_PROVIDER_MATERIALIZED_ROOT
```

The downstream `.github` consumer resolves one of those existing materialized roots and enforces the storage ordering. If neither resolves, the reusable invocation remains blocked/retryable and the live failure-email archive step is not permitted.

The intended downstream sequence is:

```text
SEARCH_MESSAGES
-> normalize failure incidents
-> exact-byte KV write + readback
-> ARCHIVE_IDS
-> StegHealth reconciliation
-> Canonical Work / InTr continuation when applicable
```

The KV path forwarding is metadata only. It adds no provider credential route, no second scheduler, and no alternate mailbox path.

## Source/runtime separation repair already merged

PR #58 repaired the initial implementation that passed the local `.github` source checkout as both `source_root` and `runtime_root`. The merged implementation now:

- resolves the runtime from `STEGVERSE_HEARTBEAT_ROOT` or one canonical local runtime location;
- passes the local `.github` checkout only as `source_root`;
- passes the resident heartbeat runtime only as `runtime_root`;
- stores `receipts/reusable-task/<slot>.latest.json` under the resident runtime;
- blocks rather than falling back when the resident runtime is absent;
- retains same-UTC-hour idempotency using the resident receipt.

## Validation evidence

- PR #57 exact head `99e63e6e01962232125f70becec5e21eac11ae30`: Test Readiness `34332190725` SUCCESS.
- PR #58 exact head `8fae4401381d7479373add148d21de6c514d2e7b`: Test Readiness `34356342498` SUCCESS.
- Upstream #1252: Heartbeat `34332023132`, organization-control `34332023277`, deterministic suite `34332023168` SUCCESS.
- Upstream #1259: Heartbeat `34352789541`, organization-control `34352789580`, deterministic suite `34352789603` SUCCESS.
- Upstream #1273: organization-control `34358206486`, Heartbeat `34358206495`, deterministic suite `34358206492` SUCCESS.
- KV forwarding validation is pending on `fix/native-email-kv-root-forwarding-20260909`.

## Evidence boundary

Reusable identity, hourly schedule construction, standing Healer recurrence, WorkerCoordinator fresh-claim rearm, source/runtime separation, same-slot idempotency, resident receipt placement, and non-secret KV path forwarding must all be merged and validated before live execution is claimed. Authentic live operation additionally requires a retained resident reusable-task receipt, a native-email monitor receipt containing exact-byte KV write/readback evidence for any observed failure incidents, and the corresponding TV/TVC Gmail provider evidence. Source merge alone is not runtime proof.
