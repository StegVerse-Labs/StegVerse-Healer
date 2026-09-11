# Native Email Reusable Schedule Mirror Handoff

Updated: 2026-09-10
Repository: `StegVerse-Labs/StegVerse-Healer`
Parent scheduler: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`
Upstream task: `StegVerse-Labs/.github:STEGVERSE-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream COSV: `10100000100000`
Upstream reusable identity: `RT-NATIVE-EMAIL-ACTION-MONITOR-001`
Upstream scoped handoff: `StegVerse-Labs/.github:docs/NATIVE_EMAIL_REUSABLE_HOURLY_MIRROR_HANDOFF.md`
State: `HOURLY_SOURCE_MERGED / RESIDENT_RUNTIME_SEPARATION_MERGED / KV_PATH_FORWARDING_MERGED / FAILED_SLOT_RETRY_SEMANTICS_MERGED / BOUNDED_RETRY_BACKOFF_MERGED / GOVERNED_ARCHIVE_SOURCE_ROOT_REUSE_IN_VALIDATION / LIVE_SCHEDULE_GOVERNANCE_KV_RECEIPT_PENDING`

## Merged chain

- PR #57 / `ef5d90a8c215056e055385a04534e16c49d9a3d5`: hourly reusable-task schedule.
- PR #58 / `a0f6daeaf33198f26e358c7b124fc9f80aad8b6b`: source/runtime separation and resident receipt placement.
- PR #59 / `93b637ddcc48777900e3804f994b22036d507571`: non-secret KV path forwarding; Test Readiness `34363810591` SUCCESS.
- PR #60 / `cd74e971ee54344c2f772fe2fd35827174914e66`: only `AUTOMATABLE_STEPS_EXHAUSTED` satisfies a UTC-hour slot; failed/boundary receipts remain retryable. Corrected exact head `d64c83454f0e86fa732ac3d1ab8ae748cc682c11`, Test Readiness `34551667188` SUCCESS.
- PR #61 / `9c1661476ff1eadbe8c6ba300519a0c3f925d2e9`: failed-slot retry is no sooner than 15 minutes and no more than four failed attempts per UTC-hour slot; exact head `6c17cec579c19e67053578030cf7efd2e1c9edaf`, Test Readiness `34551986643` SUCCESS.
- Upstream `.github` #1357 / `05c1250c91b6b09d54def657c37de5c77bd89c15`: KV wrapper returns nonzero for pre-execution/KV-proof pending states; exact head `3bc48019106386dc066d0dc1cd7148530d20e762` passed org-control `34551629855`, deterministic suite `34551629876`, and Heartbeat `34551629899`.
- Upstream `.github` #1375 / `53175dadad4de762299a9c3be1ac67cbed71998e`: exact reviewed IDs and KV-before-archive receipts are now bound into the archive governance context.
- StegOps #18 / `0d3768a7f8575af18c67b01a40f6745f35b93c0f`: Gmail `ARCHIVE_IDS` now executes only as a canonical SDK/StegCore bounded consequence; Guardrails `34555040293`, Test Readiness `34555040405`, BCAT `34555040586` SUCCESS.

## Hourly success and retry contract

`RT-NATIVE-EMAIL-ACTION-MONITOR-001` receives a deterministic UTC-hour invocation ID. A retained reusable-task receipt closes that slot only when its state is `AUTOMATABLE_STEPS_EXHAUSTED`; a failed or `BOUNDARY_RECORDED` receipt is not a successful hourly execution.

```text
retry_interval_minutes: 15
max_attempts_per_slot: 4
```

Failed attempts retain a non-secret resident attempt-state sidecar beside the reusable-task receipt. Before another provider-capable invocation, Healer checks the sidecar. It performs no retry before 15 minutes have elapsed and performs no more than four failed attempts for one UTC-hour slot. A new UTC-hour invocation ID receives fresh retry state. Backoff checks themselves perform no Gmail or KV provider operation.

## KV persistence relationship

The upstream native-email task requires normalized GitHub failure observations to reach an already-materialized KnowledgeVault with exact-byte readback before the corresponding live Gmail IDs may be archived. Healer forwards only already-present non-secret KV path bindings; the upstream wrapper may additionally resolve a validated resident KV materialization receipt. Healer does not mount KV or acquire provider credentials.

## Governed archive source relationship

The governed `ARCHIVE_IDS` path reuses the existing generic SDK/StegCore bounded-consequence architecture. It therefore needs already-local SDK, StegCore, Core-Lite, and Master Records sources. Those roots are not re-materialized by Healer.

The current repair consumes only the existing SV-DN1 production-source-preparation v2 receipt, normally at:

```text
~/.stegverse/state/sv-dn1-production-source-prep/receipts/latest.json
```

A non-secret alternate receipt path may be supplied through `STEGVERSE_SV_DN1_SOURCE_PREP_RECEIPT`.

Healer augments `STEGVERSE_REPO_ROOTS_JSON` only when the receipt proves all of the following:

- schema `stegverse.sv-dn1.production-source-prep-receipt/v2`;
- state `COMPLETE` and transition `SV_DN1_PRODUCTION_SOURCE_PREPARATION_COMPLETE`;
- exactly the four canonical source components;
- a `sha256:<64 hex>` identity for every component;
- `migration_anchors_verified=true`;
- no network source fetch, GitHub platform dependency, credential use, GitHub token use, or repository writeback;
- each declared root is still materialized with its required runtime marker file.

An absent, incomplete, stale, or malformed receipt contributes zero roots. Healer does not fetch source or substitute a different component. Existing repository-map roots remain preferred through `setdefault` semantics.

This matches the existing SDK authority model: caller manifests keep `external_consequence_enabled=false`; the bounded consequence executor is installed outside caller authority payload and remains unreachable until canonical StegGate and commit coherence allow execution.

## Evidence boundary

Source construction, source-root reuse, governance binding, and retry semantics do not prove resident operation. Authentic completion still requires a retained resident reusable-task receipt, the native-email monitor/KV evidence, canonical SDK/StegCore governance and commit-coherence evidence, corresponding TV/TVC Gmail provider evidence, route/transaction/Master Records custody, bounded mailbox progression, and durable downstream reconciliation. No second scheduler, monitor, heartbeat, WorkerCoordinator, provider route, source installer, or user-operated machine is introduced.
