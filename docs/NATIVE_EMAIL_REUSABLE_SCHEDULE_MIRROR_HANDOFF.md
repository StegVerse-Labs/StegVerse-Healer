# Native Email Reusable Schedule Mirror Handoff

Updated: 2026-09-10
Repository: `StegVerse-Labs/StegVerse-Healer`
Parent scheduler: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`
Upstream task: `StegVerse-Labs/.github:STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream COSV: `10100000100000`
Upstream reusable identity: `RT-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream scoped handoff: `StegVerse-Labs/.github:docs/NATIVE_EMAIL_REUSABLE_HOURLY_MIRROR_HANDOFF.md`
State: `HOURLY_SOURCE_MERGED / RESIDENT_RUNTIME_SEPARATION_MERGED / KV_PATH_FORWARDING_MERGED / FAILED_SLOT_RETRY_SEMANTICS_MERGED / BOUNDED_RETRY_BACKOFF_IN_VALIDATION / LIVE_SCHEDULE_AND_KV_RECEIPT_PENDING`

## Merged chain

- PR #57 / `ef5d90a8c215056e055385a04534e16c49d9a3d5`: hourly reusable-task schedule.
- PR #58 / `a0f6daeaf33198f26e358c7b124fc9f80aad8b6b`: source/runtime separation and resident receipt placement.
- PR #59 / `93b637ddcc48777900e3804f994b22036d507571`: non-secret KV path forwarding; Test Readiness `34363810591` SUCCESS.
- PR #60 / `cd74e971ee54344c2f772fe2fd35827174914e66`: only `AUTOMATABLE_STEPS_EXHAUSTED` satisfies a UTC-hour slot; failed/boundary receipts remain retryable. Corrected exact head `d64c83454f0e86fa732ac3d1ab8ae748cc682c11`, Test Readiness `34551667188` SUCCESS.
- Upstream `.github` #1357 / `05c1250c91b6b09d54def657c37de5c77bd89c15`: KV wrapper returns nonzero for pre-execution/KV-proof pending states; exact head `3bc48019106386dc066d0dc1cd7148530d20e762` passed org-control `34551629855`, deterministic suite `34551629876`, and Heartbeat `34551629899`.

## Hourly success and retry contract

`RT-NATIVE-EMAIL-ACTION-MONITOR-001` receives a deterministic UTC-hour invocation ID. A retained reusable-task receipt closes that slot only when its state is `AUTOMATABLE_STEPS_EXHAUSTED`; a failed or `BOUNDARY_RECORDED` receipt is not a successful hourly execution.

The current bounded-retry repair adds schedule-local limits:

```text
retry_interval_minutes: 15
max_attempts_per_slot: 4
```

Failed attempts retain a non-secret resident attempt-state sidecar beside the reusable-task receipt. Before another provider-capable invocation, Healer checks the sidecar. It performs no retry before 15 minutes have elapsed and performs no more than four failed attempts for one UTC-hour slot. A new UTC-hour invocation ID receives fresh retry state. Backoff checks themselves perform no Gmail or KV provider operation.

This preserves recovery within an hour without turning a transient KV/provider failure into a tight resident-cycle loop.

## KV persistence relationship

The upstream native-email task requires normalized GitHub failure observations to reach an already-materialized KnowledgeVault with exact-byte readback before the corresponding live Gmail IDs may be archived. Healer forwards only already-present non-secret KV path bindings; the upstream wrapper may additionally resolve a validated resident KV materialization receipt. Healer does not mount KV or acquire provider credentials.

## Evidence boundary

Source construction and retry semantics do not prove resident operation. Authentic completion still requires a retained resident reusable-task receipt, the native-email monitor/KV evidence for observed failure incidents, corresponding TV/TVC Gmail provider evidence, bounded mailbox progression, and durable downstream reconciliation. No second scheduler, monitor, heartbeat, WorkerCoordinator, provider route, or user-operated machine is introduced.
