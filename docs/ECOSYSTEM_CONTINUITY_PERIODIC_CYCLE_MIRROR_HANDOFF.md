# Ecosystem Continuity Periodic Cycle Mirror Handoff

Updated: 2026-09-11

```text
Parent Goal Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
COSV: 71000000100111
Repository: StegVerse-Labs/StegVerse-Healer
Branch: feature/ece-periodic-sovereign-schedule-001
State: CYCLE_SOURCE_IMPLEMENTED / REUSABLE_SCHEDULE_BINDING_PENDING
Authority effect: NONE
Scheduler owner: existing StegVerse-Healer sovereign reusable-task scheduler extension
```

## Purpose

Provide one bounded periodic continuity cycle implementation that consumes already-local ECE, Site, Healer, and Master Records source, evaluates resident observations, retains exact evaluation bytes, reconstructs them, creates immutable Healer intake, and produces the Site-safe projection without source-repository writeback or a second scheduler.

## Source

```text
app/ece_periodic_evaluation.py
app/run_ece_periodic_evaluation.py
tests/test_ece_periodic_evaluation.py
README.md
```

## Runtime contract

Required already-local source roots:

```text
StegVerse-Labs/.github
StegVerse-Labs/Site
StegVerse-Labs/StegVerse-Healer
master-records/orchestration
```

Required resident root:

```text
STEGVERSE_HEARTBEAT_ROOT
```

Optional authentic observation input:

```text
STEGVERSE_ECE_OBSERVATIONS
or <resident>/receipts/ecosystem-continuity/observations.latest.json
```

If no observation bundle is present, the cycle runs with an empty observation set. The canonical evaluator therefore emits `NOT_OBSERVED` findings and an appropriately degraded continuity classification instead of synthesizing PASS evidence.

## Resident outputs

```text
receipts/ecosystem-continuity/<evaluation_id>.evaluation.json
receipts/ecosystem-continuity/evaluation.latest.json
master-records/ecosystem-continuity/<evaluation_id>.evaluation.json
master-records/ecosystem-continuity/<evaluation_id>.custody.json
receipts/ecosystem-continuity/healer-intake.latest.json
receipts/ecosystem-continuity/site-projection.latest.json
receipts/ecosystem-continuity/cycle.latest.json
```

## Invariants

- Source repositories remain read-only during a cycle.
- Missing required local source blocks rather than fetching from GitHub/network.
- Master Records custody/reconstruction must round-trip exact evaluation bytes before downstream intake/projection completes.
- Healer intake remains `NONE_INTAKE_ONLY` and cannot verify recovery.
- Site projection remains read-only/fail-closed.
- `recovery_verified` is always false for this cycle; a later independent ECE PASS is required.
- The implementation creates no scheduler. Periodic invocation must be registered through the existing reusable-task schedule path.

## Next

Validate this cycle source, then register one reusable ECE identity/runner in the canonical `.github` reusable-task registry and bind it hourly in `data/reusable_task_schedule.json`. Source merge alone does not prove a resident cycle executed or that any authentic ecosystem observation has been retained.
