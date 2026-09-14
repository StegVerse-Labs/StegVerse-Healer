# StegBrowser Runtime Consumption Carrier Binding Mirror Handoff

Updated: 2026-09-14
Repository: `StegVerse-Labs/StegVerse-Healer`
Goal Task ID: `STEG-BROWSER-RUNTIME-CONSUMPTION-001`
COSV: `40000100100000`
Status: `SOURCE_BINDING_READY / RESIDENT-ROOT BOOTSTRAP CIRCULARITY REPAIRED IN SOURCE / RUNTIME EVIDENCE PENDING`

## Purpose

Bind the already-registered reusable task `RT-STEGBROWSER-RUNTIME-CONSUMPTION-001` into the existing sovereign Healer carrier and neutral reusable-task scheduler without creating a new scheduler, runtime, WorkerCoordinator, credential path, device path, or authority owner.

## Reused execution surface

```text
standing Healer resident request
-> existing WorkerCoordinator targeted execution
-> existing Healer sovereign scheduler worker
-> existing Healer reusable-task carrier
-> RT-REUSABLE-TASK-SCHEDULER-001
-> RT-SOVEREIGN-SOURCE-REFRESH-001 when resident source must be materialized
-> scripts/trigger_reusable_task.py
-> RT-STEGBROWSER-RUNTIME-CONSUMPTION-001
-> scripts/run_stegbrowser_runtime_consumption_reusable.py
-> SovereignLocalEventRuntimeAdapter
-> ADMITTED-EPHEMERAL-STEGOS-NODE
-> Canonical Work / Interlock-InTr / resident-consumption chain
```

## Resident-root bootstrap circularity

Post-binding investigation found a concrete source defect in `app/reusable_task_scheduler.py`.

Before this repair, the Healer carrier required `_resident_runtime_root()` to already return a valid resident root before it would invoke `RT-REUSABLE-TASK-SCHEDULER-001`. The same neutral scheduler carries `RT-SOVEREIGN-SOURCE-REFRESH-001`, whose existing canonical implementation can create the resident runtime directory and copy the already-local static WorkerCoordinator/control source into it. The result was a circular materialization gate:

```text
no valid resident root
-> neutral scheduler not invoked
-> RT-SOVEREIGN-SOURCE-REFRESH-001 cannot run
-> resident root cannot be populated
```

The narrow repair preserves the existing architecture:

1. If a valid resident root already exists, behavior is unchanged.
2. If no root is valid, bootstrap materialization is permitted only when the existing schedule explicitly enables `RT-SOVEREIGN-SOURCE-REFRESH-001`.
3. The carrier passes an existing canonical resident-root candidate path as a non-authorizing materialization target to the existing neutral scheduler.
4. The existing local-only source-refresh task remains responsible for directory creation and static source population.
5. After neutral scheduler delegation, Healer re-runs resident-root discovery and classifies the actual resulting markers.
6. If no authentic resident markers exist after delegation, the Healer receipt remains `BLOCKED`.
7. A source checkout is never treated as resident runtime proof.

Schedules that do not enable `RT-SOVEREIGN-SOURCE-REFRESH-001` retain the original fail-closed `RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED` boundary.

## Authority invariants

- Task Registry: coordination only.
- Healer carrier / neutral reusable scheduler: scheduling and invocation transport only.
- Source refresh: already-local static source materialization only; no network fetch or credential acquisition.
- WorkerCoordinator: claim/fence authority.
- Interlock/InTr: governed admission/state-transition authority.
- TV/TVC: credential/provider authority.
- Master Records: observed-reality/custody/reconstruction authority.
- HeartBeat: timing/freshness/observation only.
- GitHub/CI: source validation and evidence transport only; runtime authority `NONE`.
- no second user-operated device is introduced.

## Authentic completion boundary

This source repair does not itself satisfy `RESIDENT_CUSTODY_ROOT_AUTHENTICALLY_OBSERVED_FOR_STEGBROWSER` or `CANONICAL_WORK_RESIDENT_CONSUMPTION_OBSERVED`.

Required runtime evidence remains an actual Healer resident cycle whose post-delegation `resident_custody_root_observation.state` is `RESIDENT_CUSTODY_ROOT_OBSERVED`, with retained root identity/markers, followed by the exact resident-consumption receipt:

```text
receipts/sovereign-host/canonical-work-stegbrowser-runtime-consumption-request-consumption.latest.json
```

Source merge, CI, scheduler configuration, or unit-test materialization is not runtime proof.

## Validation

`tests/test_resident_runtime_root_bootstrap.py` verifies that a schedule containing the existing `RT-SOVEREIGN-SOURCE-REFRESH-001` can use the canonical local runtime path as a materialization target and that post-delegation discovery observes the resident marker. Existing `tests/test_reusable_task_scheduler.py` continues to verify that schedules without source refresh fail closed when no resident root exists.

## Next sequence

```text
exact-head Test Readiness validation
-> merge narrow Healer carrier repair if green
-> observe the next authentic existing Healer resident cycle
-> require post-delegation resident_custody_root_observation
-> if RESIDENT_CUSTODY_ROOT_OBSERVED, classify retained receipt reachability
-> hand the same authentic root to STEGAGENTS-GOVERNED-RUNTIME-001
-> run existing steagents_governed_runtime_targeted selector
```

Manual work: none.
