# Hygiene Canonical Work Portable Dispatch Carrier Binding

Goal Task ID: `HYGIENE-CAUSAL-ROOTS-001`  
COSV: `10100000100000`  
Reusable task: `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001`  
Repository: `StegVerse-Labs/StegVerse-Healer`  
State: `SOURCE_BINDING_READY / AUTHENTIC_RESIDENT_INVOCATION_PENDING`

## Purpose

Bind the already-registered `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001` identity to the existing standing sovereign Healer carrier and neutral reusable-task scheduler so `HYGIENE-CAUSAL-ROOTS-001` can be invoked without requiring a permanently connected or second user-operated device.

This is an invocation-reachability repair only. It creates no scheduler, runtime, dispatcher, request identity, WorkerCoordinator, Interlock/InTr authority, credential route, Site route, or execution authority.

## First proven defect

The reusable identity exists in `StegVerse-Labs/.github`, its sole runner is the existing `scripts/refresh_and_dispatch_resident_requests.py` bridge, and the Healer carrier already delegates through:

```text
standing Healer resident request
-> existing WorkerCoordinator targeted execution
-> existing Healer sovereign scheduler worker
-> app/reusable_task_scheduler.py
-> RT-REUSABLE-TASK-SCHEDULER-001
-> scripts/trigger_reusable_task.py
-> registered reusable identity
```

But `data/reusable_task_schedule.json` had no row for `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001`. Therefore the existing carrier could not select or trigger the hygiene reusable identity at all. This is the first source-level stop before an authentic Task Registry `CONTINUE` check-in can occur.

## Repair

Add one enabled hourly schedule row:

- reusable task: `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001`
- tracking task: `HYGIENE-CAUSAL-ROOTS-001`
- COSV: `10100000100000`
- repository: `StegVerse-Labs/.github`
- retry interval: 15 minutes
- maximum attempts per UTC-hour slot: 4
- `only_consumer=canonical_work_coordination`
- `goal_task_id=HYGIENE-CAUSAL-ROOTS-001`

The parameter object intentionally contains no task-extraneous scheduler metadata. The reusable bridge in `.github` rejects unknown manifest parameters and requires only `source_root`, `runtime_root`, `only_consumer`, and `goal_task_id`; the neutral scheduler already injects `source_root` and `runtime_root` before child invocation.

The existing `RT-SOVEREIGN-SOURCE-REFRESH-001` schedule row remains enabled, so the Healer carrier may use the already-canonical resident-root materialization path when no valid runtime root is initially observed. No connected Remote Desktop/device surface is required by this binding.

## Authority boundaries

- Task Registry = work identity and coordination truth.
- Healer = carrier/consumer only.
- `RT-REUSABLE-TASK-SCHEDULER-001` = neutral scheduling/idempotency/retry semantics.
- WorkerCoordinator = execution claim/fence authority.
- Interlock/InTr = governed transition/admission authority.
- TV/TVC = credential authority.
- Master Records = observed-reality/custody/reconstruction authority.
- GitHub/CI = source validation/evidence transport only; runtime authority `NONE`.
- second user-operated device required = `false`.

## Authentic completion boundary

Source merge proves only that the existing Healer carrier can select the hygiene reusable identity.

The required authentic chain remains:

```text
standing Healer resident cycle
-> RT-REUSABLE-TASK-SCHEDULER-001
-> RT-CANONICAL-WORK-PORTABLE-DISPATCH-001
-> scripts/refresh_and_dispatch_resident_requests.py
-> exact canonical_work_coordination
-> --goal-task-id HYGIENE-CAUSAL-ROOTS-001
-> retained Task Registry check-in
-> disposition == CONTINUE
-> WorkerCoordinator claim/fence
-> Interlock/InTr admission
```

No source merge, CI success, schedule presence, GitHub Action, or absent/present device connector may substitute for the retained resident `CONTINUE` receipt.

## Validation

`tests/test_hygiene_canonical_work_schedule.py` protects the exact reusable/task/COSV/repository binding, all-hours retry policy, minimal bridge-compatible parameter object, existing neutral scheduler trigger reuse, existing source-refresh bootstrap reuse, and no-second-scheduler/no-second-device invariants.


## 2026-09-17 merge and authentic runtime boundary

PR #90 merged the schedule-binding repair as `9c737c77f861a28ef55005b31812777f541af96d` from exact head `7643962d7d31cbff74c3afa45cb4727f7b097b8f`. Exact-head Healer `Test Readiness` run `35305308087` / job `105476184831` passed. The deterministic suite ran 150 tests and explicitly executed both `HygieneCanonicalWorkScheduleTests` methods, proving the exact schedule/task/COSV/minimal-parameter binding and reuse of the existing neutral scheduler/source-refresh carrier semantics.

A post-merge evidence search found no retained `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001` trigger receipt, no hygiene `CONTINUE` check-in, and no hygiene WorkerCoordinator/InTr admission evidence. This is not reclassified as a new source defect. The existing standing Healer carrier remains the first eligible authentic invocation surface; source/CI cannot substitute for its resident execution. No additional scheduler, runtime, dispatcher, browser route, Remote Desktop prerequisite, or second device is authorized.


## 2026-09-17 authentic resident-cycle observation after carrier binding

The post-merge continuation re-read the standing Healer request and the existing authorized resident-evidence seam before making any further change. `control/resident-execution-request.d/healer-sovereign-scheduler-001.json` remains a standing recurring `REQUESTED` request for `EACH_ELIGIBLE_RESIDENT_SCHEDULER_CYCLE`; it is not consumed or retired by one completed scheduler cycle.

The exact authoritative resident consumption receipt remains:

```text
<resident-root>/receipts/sovereign-host/healer-sovereign-scheduler-request-consumption.latest.json
-> execution_result
-> resident_custody_root_observation_retention
```

Current accessible evidence does not expose an authentic resident copy of that receipt, an embedded retention pointer, or the retained resident-root packet. The canonical runtime classification already records this as `RESIDENT_CARRIER_OUTPUT_POINTER_NOT_GITHUB_VISIBLE_BUT_RUNTIME_BOUND`, with `defect_source_side_fixable=false` and `source_side_repair_required=false`. The exact GitHub checkpoint `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json` is also absent; that absence is evidence reachability only and is not a runtime-failure claim.

No authentic `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001` trigger receipt, runner receipt, hygiene Task Registry `CONTINUE`, WorkerCoordinator claim/fence, or Interlock/InTr admission was therefore observed. Because no authentic carrier boundary was recorded before `CONTINUE`, there is no newly evidenced source defect to repair in this continuation. No scheduler, runtime, dispatcher, browser route, request identity, authority plane, Site/StegCore mutation, Remote Desktop dependency, or second user-operated device was added.


## 2026-09-17 generation-32 checkpoint/CONTINUE evidence-chain correction

A concurrent canonical reconciliation in `StegVerse-Labs/.github` advanced the Task Registry to generation 32 and traced the existing Healer resident serialization boundary field-by-field. That trace corrects the earlier assumption that the outer resident request-consumption receipt directly inlines the Healer child receipt.

The first existing full pointer-bearing resident surface is instead the fenced worker checkpoint after:

```text
FENCED_PROCESS_ADAPTER_ALLOW_PROJECTION
-> <resident-root>/receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
-> child_receipt
```

The outer `receipts/sovereign-host/healer-sovereign-scheduler-request-consumption.latest.json` retains the WorkerCoordinator cycle envelope as `execution_result`; it does not structurally inline `child_receipt`. No exporter or alternate projection is required or authorized.

For this hygiene Goal, the authentic proof chain is therefore:

```text
projected Healer checkpoint
-> child_receipt.reusable_task_schedule[]
   or child_receipt.neutral_reusable_task_scheduler.runner_result.outcomes[]
-> reusable_task_id == RT-CANONICAL-WORK-PORTABLE-DISPATCH-001
-> tracking_task_id == HYGIENE-CAUSAL-ROOTS-001
-> cosv_task_vector == 10100000100000
-> receipt_ref + runtime_root
-> authentic child reusable trigger receipt at receipt_ref
-> resident-root/receipts/sovereign-host/resident-request-dispatch.latest.json
-> selection_scope == EXACT_SELECTOR
-> selected_consumers == [canonical_work_coordination]
-> current_goal_task_id == HYGIENE-CAUSAL-ROOTS-001
-> outcomes[canonical_work_coordination].result.canonical_work_request_set.task_registry_cycle.result
-> selected_task_id == HYGIENE-CAUSAL-ROOTS-001
-> considered[HYGIENE-CAUSAL-ROOTS-001].disposition == CONTINUE
```

The portable reusable trigger currently treats the bridge as a successful bounded runner without a standardized reusable `runner-result` file; that is not itself a proven runtime defect. The bridge writes the full resident refresh/dispatch and exact resident request-dispatch receipts under the same authentic runtime root, and those existing receipts carry the canonical Task Registry result. A source repair is authorized only if an authentic resident checkpoint/child receipt proves that this existing chain stops before the required `CONTINUE` evidence.

Current accessible evidence still exposes no authentic projected Healer checkpoint, child reusable trigger receipt, resident request-dispatch receipt for this invocation, or retained hygiene `CONTINUE`. The standing request remains eligible. No WorkerCoordinator claim/fence or Interlock/InTr admission is recognized for hygiene, and no scheduler, runtime, dispatcher, browser route, request, authority plane, Site/StegCore mutation, Remote Desktop dependency, or second user-operated device is introduced.


## 2026-09-17 generation-32 first-checkpoint direct re-observation

The corrected first authentic resident surface was re-observed directly rather than inferred from search indexing. Current canonical coordinates entering this observation were `.github` generation 32 and Healer main `fdbfefb15cf9ea520ca3085556b195d1fc69eccc`.

Direct authenticated repository probes found no retained copies of:

```text
receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
receipts/sovereign-host/healer-sovereign-scheduler-request-consumption.latest.json
receipts/sovereign-host/resident-request-dispatch.latest.json
receipts/sovereign-host/resident-refresh-dispatch.latest.json
```

The checkpoint and dispatch paths were checked in both `StegVerse-Labs/.github` and `StegVerse-Labs/StegVerse-Healer` where applicable. Organization-wide search resolved only source contracts, tests, handoffs, canonical classification reports, and historical records that themselves say the checkpoint is absent. No result was an authentic resident checkpoint, child reusable trigger receipt, or same-root dispatch receipt.

Therefore none of the required hygiene child predicates can yet be evaluated authentically:

```text
reusable_task_id == RT-CANONICAL-WORK-PORTABLE-DISPATCH-001
tracking_task_id == HYGIENE-CAUSAL-ROOTS-001
cosv_task_vector == 10100000100000
selection_scope == EXACT_SELECTOR
selected_consumers == [canonical_work_coordination]
current_goal_task_id == HYGIENE-CAUSAL-ROOTS-001
selected_task_id == HYGIENE-CAUSAL-ROOTS-001
considered[HYGIENE-CAUSAL-ROOTS-001].disposition == CONTINUE
```

No connected Remote Desktop surface was available during this observation. That remains evidence reachability only; it does not alter the standing recurring request, create a runtime/substrate failure, or authorize a second device/path. Because no authentic checkpoint or child receipt exposed a concrete pre-`CONTINUE` boundary, no source/runtime repair is authorized. The standing Healer request and existing neutral reusable-task carrier remain unchanged.
