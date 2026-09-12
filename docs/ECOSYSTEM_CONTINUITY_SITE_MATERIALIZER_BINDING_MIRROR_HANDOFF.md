# Ecosystem Continuity Site Materializer Binding Mirror Handoff

Updated: 2026-09-12

```text
Goal Task ID: SITE-ECE-CURRENT-PROJECTION-MATERIALIZER-001
Parent Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
COSV: 71000000102000
Repository: StegVerse-Labs/StegVerse-Healer
State: SOURCE IMPLEMENTED / VALIDATION PENDING
Authority effect: NONE
```

## Purpose

Bind the existing completed Healer ECE cycle to the Site copy-only current-projection materializer without moving continuity interpretation or publication authority into Healer.

## Binding

`app/run_ece_periodic_evaluation.py` now invokes Site `scripts/materialize_ecosystem_continuity_current.py` only after the canonical SDK diagnostic -> ECE -> Master Records -> Healer intake -> Site-safe projection cycle has completed and written `cycle.latest.json`.

The served runtime root is optional and must be supplied as `STEGVERSE_SITE_SERVED_ROOT`.

- If absent, the cycle stays `COMPLETE` and records `site_materialization_state=NOT_BOUND` plus `site_live_publication_observed=false`.
- If explicitly supplied, missing Site source, invalid projection binding, materializer failure, or receipt drift blocks rather than serving stale data.
- A valid materialization records `MATERIALIZED_PENDING_PUBLIC_OBSERVATION`; it never sets live publication or recovery true.

## Authority boundary

The runner does not calculate continuity, rewrite the safe projection, acquire credentials, fetch source, write to the Site repository, or prove public reachability. The materializer receipt must remain `NONE_COPY_ONLY`, exact-byte preserving, non-recalculating, non-recovery, and `live_publication_observed=false`.

## Next

Pass Test Readiness and merge. Then reconcile canonical child state. Authentic materialization remains unproven until a resident ECE cycle runs with an already-local served Site root and retained materialization receipt, followed by independent public page observation.
