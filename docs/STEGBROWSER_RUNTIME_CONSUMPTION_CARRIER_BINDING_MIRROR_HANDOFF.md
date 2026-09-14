# StegBrowser Runtime Consumption Carrier Binding Mirror Handoff

Updated: 2026-09-14
Repository: `StegVerse-Labs/StegVerse-Healer`
Goal Task ID: `STEG-BROWSER-RUNTIME-CONSUMPTION-001`
COSV: `40000100100000`
Status: `SOURCE_BINDING_IN_PROGRESS / RUNTIME_EVIDENCE_PENDING`

## Purpose

Eliminate the session execution-access gap by binding the already-registered reusable task `RT-STEGBROWSER-RUNTIME-CONSUMPTION-001` into the existing sovereign Healer carrier and neutral reusable-task scheduler. This is a connection to an existing authorized invocation surface; it is not a new scheduler, runtime, WorkerCoordinator, credential path, device path, or authority owner.

## Reused execution surface

```text
standing Healer resident request
-> existing WorkerCoordinator targeted execution
-> existing Healer sovereign scheduler worker
-> existing Healer reusable-task carrier
-> RT-REUSABLE-TASK-SCHEDULER-001
-> scripts/trigger_reusable_task.py
-> RT-STEGBROWSER-RUNTIME-CONSUMPTION-001
-> scripts/run_stegbrowser_runtime_consumption_reusable.py
-> SovereignLocalEventRuntimeAdapter
-> ADMITTED-EPHEMERAL-STEGOS-NODE
-> Canonical Work / Interlock-InTr / resident-consumption chain
```

The standing carrier already runs each eligible resident scheduler cycle and delegates generic reusable scheduling to `RT-REUSABLE-TASK-SCHEDULER-001`. The concrete missing connection was a schedule row for `RT-STEGBROWSER-RUNTIME-CONSUMPTION-001` in `data/reusable_task_schedule.json`.

## Binding

The schedule row binds exactly:

- reusable task: `RT-STEGBROWSER-RUNTIME-CONSUMPTION-001`
- canonical Goal: `STEG-BROWSER-RUNTIME-CONSUMPTION-001`
- COSV: `40000100100000`
- repository: `StegVerse-Labs/.github`
- selected execution substrate: `ADMITTED-EPHEMERAL-STEGOS-NODE`
- hourly eligibility through the existing neutral scheduler
- bounded same-slot retry: 15 minutes, at most 4 attempts
- Remote Desktop requirement: `false`
- second user-operated device requirement: `false`
- network source fetch allowed: `false`

No physical device class or external machine is part of task authority.

## Authority invariants

- Task Registry: coordination only.
- Healer carrier / neutral reusable scheduler: scheduling and invocation transport only.
- WorkerCoordinator: claim/fence authority.
- Interlock/InTr: governed admission/state-transition authority.
- TV/TVC: credential/provider authority.
- KV/SKAP Vault: user-verification/custody authority where applicable.
- Master Records: observed-reality/custody/reconstruction authority.
- HeartBeat: timing/freshness/observation only.
- GitHub/CI: source validation and evidence transport only; runtime authority `NONE`.

## Authentic completion boundary

This binding does not satisfy `CANONICAL_WORK_RESIDENT_CONSUMPTION_OBSERVED` by itself. The first authentic successor evidence remains:

```text
receipts/sovereign-host/canonical-work-stegbrowser-runtime-consumption-request-consumption.latest.json
```

Only a resident invocation that produces the required canonical receipt may advance the Goal. Source, CI, merge, scheduler configuration, heartbeat activity, or exit-zero must not be promoted into runtime proof.

## Validation

`tests/test_stegbrowser_runtime_consumption_schedule.py` protects:

- exact reusable-task / Goal / COSV binding;
- use of the existing `.github` reusable-task source;
- `ADMITTED-EPHEMERAL-STEGOS-NODE` selection;
- automatic advancement requirement;
- no network source fetch;
- no Remote Desktop prerequisite;
- no second user-operated device prerequisite;
- reuse of `RT-REUSABLE-TASK-SCHEDULER-001` and `scripts/trigger_reusable_task.py`;
- Healer role remains `CONSUMER_CARRIER_ONLY`.

## Next sequence

```text
exact-head repository validation
-> merge source binding if clean
-> existing resident Healer scheduler cycle selects the StegBrowser reusable slot
-> neutral scheduler invokes canonical reusable trigger
-> retain exact child trigger/boundary receipt
-> require authentic Canonical Work resident-consumption receipt
-> continue downstream Goal predicates only from authentic runtime evidence
```

Manual work: none.
