# Ecosystem Continuity Periodic Cycle Mirror Handoff

Updated: 2026-09-11

```text
Parent Goal Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
COSV: 71000000100111
Repository: StegVerse-Labs/StegVerse-Healer
Branch: feature/ece-periodic-sovereign-schedule-001
State: CYCLE_SOURCE + HOURLY REUSABLE SCHEDULE BINDING IMPLEMENTED / VALIDATION PENDING
Authority effect: NONE
Scheduler owner: existing StegVerse-Healer sovereign reusable-task scheduler extension
Cross-repo reusable identity: StegVerse-Labs/.github RT-ECOSYSTEM-CONTINUITY-EVALUATION-001
```

## Purpose

Provide one bounded periodic continuity cycle that consumes already-local ECE, Site, Healer, and Master Records source, evaluates resident observations, retains exact evaluation bytes, reconstructs them, creates immutable Healer intake, and produces the Site-safe projection without source-repository writeback or a second scheduler.

## Source

```text
app/ece_periodic_evaluation.py
app/run_ece_periodic_evaluation.py
data/reusable_task_schedule.json
tests/test_ece_periodic_evaluation.py
tests/test_ece_reusable_schedule.py
README.md
```

## Schedule binding

The existing Healer reusable-task scheduler now contains one enabled row for `RT-ECOSYSTEM-CONTINUITY-EVALUATION-001`, tracked by canonical task `ECOSYSTEM-CONTINUITY-EVALUATOR-001` / COSV `71000000100111`. The initial cadence is hourly UTC, using the existing deterministic UTC-hour slot ID, 15-minute retry interval, and maximum four attempts per slot. This adds no scheduler, timer, heartbeat, polling service, or WorkerCoordinator.

The cross-repository `.github` reusable-task definition and runner bridge are being implemented under the same parent ECE goal. The schedule is executable only when that canonical identity/runner and all required already-local source roots are materialized.

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

If no observation bundle is present, the cycle uses an empty observation set. The canonical evaluator therefore emits `NOT_OBSERVED` findings and an appropriately degraded continuity classification instead of synthesizing PASS evidence.

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
- Scheduling reuses the existing reusable-task scheduler extension and creates no second scheduler.

## Current proof boundary

Source implementation and schedule configuration are not runtime activation evidence. No authentic ECE schedule slot, resident evaluation, Master Records runtime custody, Healer runtime intake, Site runtime projection, or recovery loop is claimed until retained resident evidence exists.

## Next

Pass exact-head Healer validation; merge only together with a validated canonical `.github` reusable identity/runner contract. Then observe the existing resident scheduler consuming one ECE slot before claiming periodic execution.
