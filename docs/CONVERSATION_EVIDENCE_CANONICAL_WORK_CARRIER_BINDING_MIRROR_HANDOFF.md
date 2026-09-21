# Conversation Evidence Canonical Work Carrier Binding Mirror Handoff

Updated: 2026-09-21
Repository: `StegVerse-Labs/StegVerse-Healer`
Goal Task ID: `CONVERSATION-EVIDENCE-INGESTION-CUSTODY-001`
COSV ID: `20011000100000`
Reusable task: `RT-CANONICAL-WORK-PORTABLE-DISPATCH-001`
Status: `SOURCE BINDING STAGED / AUTHENTIC INVOCATION PENDING`

## Purpose

Bind the already-registered conversation-evidence ingestion Goal to the existing neutral reusable-task scheduler and standing sovereign Healer carrier so its already-admitted state-triggered Canonical Work successor can be invoked with the exact Goal Task context.

## Existing path only

```text
RT-REUSABLE-TASK-SCHEDULER-001
-> RT-CANONICAL-WORK-PORTABLE-DISPATCH-001
-> scripts/refresh_and_dispatch_resident_requests.py
-> exact canonical_work_coordination selector
-> goal_task_id=CONVERSATION-EVIDENCE-INGESTION-CUSTODY-001
-> existing Canonical Work registry cycle
-> existing targeted WorkerCoordinator one-shot
```

No scheduler, runtime, dispatcher, WorkerCoordinator, custody plane, request identity, credential path, or device prerequisite is created.

## Schedule binding

The existing schedule receives one additional task-scoped row:
- tracking task: `CONVERSATION-EVIDENCE-INGESTION-CUSTODY-001`
- COSV: `20011000100000`
- invocation key: exact Goal Task ID
- cadence: every UTC hour
- retry: 15 minutes, maximum 4 attempts per slot
- parameters: only `only_consumer=canonical_work_coordination` and exact `goal_task_id`

The neutral scheduler injects local source/runtime roots through its existing contract.

## Authority boundary

Healer remains carrier-only.
WorkerCoordinator remains claim/fence authority.
Interlock/InTr remains governed transition authority.
Master Records remains custody/reconstruction authority.
TV/TVC remains credential authority.
GitHub/CI/source success proves no resident execution.

## Completion boundary

This binding is complete only as source configuration after exact-head Healer validation and merge. The parent Goal remains incomplete until an authentic resident invocation produces a fresh WorkerCoordinator claim/fence and `CONVERSATION_EVIDENCE_INGESTED` closes in Master Records with RECORDED + reconstruction PASS + required-evidence PASS + exact digest equality.


## Source-refresh ordering repair — 2026-09-21

The first deterministic post-binding invocation defect was schedule ordering when no resident runtime root was yet materialized. The neutral scheduler evaluates schedule rows in document order, and `CONVERSATION-EVIDENCE-INGESTION-CUSTODY-001` was positioned before `RT-SOVEREIGN-SOURCE-REFRESH-001`. In that state the conversation-evidence Goal necessarily hit `RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED` before the same already-existing scheduler reached the existing local-only source refresh child.

This repair changes only schedule ordering: the existing `RT-SOVEREIGN-SOURCE-REFRESH-001` row now precedes the existing conversation-evidence portable-dispatch row. The source-refresh child retains the same reusable identity, runner, scheduler, local-only source contract, and authority boundaries. No scheduler, runtime, dispatcher, WorkerCoordinator, custody plane, credential path, device prerequisite, or source transport is added.
