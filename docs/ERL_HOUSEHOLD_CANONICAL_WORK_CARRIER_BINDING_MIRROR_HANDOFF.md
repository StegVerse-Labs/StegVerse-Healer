# ERL Household Economic Conditions Canonical Work Carrier Binding

Goal Task ID: `ERL-HOUSEHOLD-ECONOMIC-CONDITIONS-SITE-001`  
COSV: `10100000100000`  
Reusable task: `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001`  
Repository: `StegVerse-Labs/StegVerse-Healer`  
State: `SOURCE_BINDING_READY / AUTHENTIC_RESIDENT_INVOCATION_PENDING`

## Purpose

Bind the exact ERL household Goal to the already-existing neutral reusable-task scheduler and standing sovereign Healer carrier. This repairs only task-scoped addressability. It creates no scheduler, runtime, dispatcher, request identity, WorkerCoordinator, Interlock/InTr authority, credential route, device dependency, or publication authority.

## Exact binding

- tracking task: `ERL-HOUSEHOLD-ECONOMIC-CONDITIONS-SITE-001`
- COSV `task.v1`: `10100000100000`
- source repository: `StegVerse-Labs/.github`
- invocation key: exact Goal Task ID
- selector: `canonical_work_coordination`
- retry: every 15 minutes, at most four attempts per UTC-hour slot
- source/runtime roots: injected by the existing neutral scheduler
- provider credentials: none passed by this schedule

## Authority chain

```text
standing Healer carrier
-> RT-REUSABLE-TASK-SCHEDULER-001
-> RT-CANONICAL-WORK-PORTABLE-DISPATCH-001
-> scripts/refresh_and_dispatch_resident_requests.py
-> exact canonical_work_coordination
-> Task Registry collision/check-in
-> Interlock/InTr ingress
-> fresh WorkerCoordinator claim/fence
-> ERL household worker
-> TV/TVC metadata-only BEA readiness
-> BEA single-use operation only if authentic decision=READY
-> Master Records custody/reconstruction
```

Source presence, scheduler selection, GitHub Actions, and the COSV pointer do not prove any runtime transition. The first authentic progression evidence remains the resident child/dispatch chain for this exact Goal. BEA remains UNKNOWN until an authentic resident readiness result is retained. Site public activation remains false.

## Validation

`tests/test_erl_household_canonical_work_schedule.py` requires one exact schedule row, the exact COSV/task binding, minimal bridge-compatible parameters, hourly bounded retry, reuse of the existing neutral scheduler/source refresh, and no device/credential parameters.
