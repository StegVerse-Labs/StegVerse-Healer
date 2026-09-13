# Ecosystem Continuity Periodic Cycle Mirror Handoff

Updated: 2026-09-12

```text
Parent Goal Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
Child Goal Task ID: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001
Parent COSV: 71000000100111
Child COSV: 71000000101000
Repository: StegVerse-Labs/StegVerse-Healer
Branch: main
State: SOURCE MERGED / AUTHENTIC RESIDENT LIFECYCLE EVIDENCE PENDING
Authority effect: NONE
Scheduler owner: existing StegVerse-Healer sovereign reusable-task scheduler extension
Cross-repo reusable identity: StegVerse-Labs/.github RT-ECOSYSTEM-CONTINUITY-EVALUATION-001
```

## Purpose

Provide one bounded periodic continuity cycle that routes registered ecosystem diagnostic tests through the installed StegVerse SDK `ecosystem_diagnostic` processor before ECE interprets continuity. The SDK returns diagnostic observations only; ECE remains the sole continuity interpreter; Master Records retains/reconstructs the resulting ECE evaluation; Healer consumes findings; Site receives a safe projection.

## Runtime chain

```text
existing Healer hourly reusable slot
-> canonical ECE registry + optional resident observation bundle
-> SDK diagnostic request
-> stegverse.ingress-manifest.v1
-> processing.capability = ecosystem_diagnostic
-> stegverse.route.ecosystem-diagnostic.v1
-> exact SDK diagnostic result bytes + SHA-256 retained in resident runtime
-> SDK result translated to ECE observation input
-> canonical ECE continuity evaluation
-> exact ECE Master Records custody/reconstruction
-> Healer intake
-> Site-safe projection
-> manifest-bound reusable runner result
-> runner expiry observation
-> residual non-executing reusable construct
-> reusable lifecycle Master Records request
-> destination-owned lifecycle custody + exact request reconstruction
-> entropy-recovery receipt
-> scheduler slot satisfied by ENTROPY_RECOVERY_RECORDED
```

## Required already-local source roots

```text
StegVerse-Labs/.github
StegVerse-Labs/Site
StegVerse-Labs/StegVerse-Healer
StegVerse-org/StegVerse-SDK
master-records/orchestration
```

No source is fetched from GitHub/network during resident execution. Missing required local source blocks fail-closed.

## Diagnostic request construction

The cycle expands every registered ECE component/predicate into one SDK diagnostic test with stable identity `ece:<component_id>:<predicate_id>`. Existing resident observations are carried as source observation packets; missing observations remain `null` and therefore become SDK `NOT_OBSERVED` results. The request pre-registers expected evidence fields:

```text
evidence_refs
observed_at
```

The SDK v1 request always declares `mutation_permitted=false`.

## Exact SDK-result binding

The exact SDK diagnostic result bytes are retained under the resident continuity receipt directory:

```text
receipts/ecosystem-continuity/sdkdiag_<sha-prefix>.result.json
receipts/ecosystem-continuity/sdk-diagnostic-result.latest.json
```

The cycle computes the exact SHA-256 of those bytes. Every translated ECE observation preserves its underlying SDK evidence references and also carries a result-envelope provenance reference:

```text
sdk-diagnostic-result-sha256:<exact-result-sha256>
```

This binds the ECE finding/evaluation chain back to the exact SDK diagnostic artifact without treating the envelope hash as proof that the underlying predicate passed.

## Fail-closed SDK boundary

Before ECE executes, the cycle rejects an SDK result when any of the following occurs:

- result schema is not `stegverse.ecosystem-diagnostic-result.v1`;
- processing capability is not `ecosystem_diagnostic`;
- route is not `stegverse.route.ecosystem-diagnostic.v1`;
- `authority_effect` is not `NONE_DIAGNOSTIC_ONLY`;
- `mutation_performed` is not false;
- `continuity_state_present` is not false;
- any `continuity_state` value is supplied by the SDK result.

The SDK diagnoses; ECE interprets continuity. That boundary is structural, not advisory.

## Resident outputs

```text
receipts/ecosystem-continuity/sdkdiag_<sha-prefix>.result.json
receipts/ecosystem-continuity/sdk-diagnostic-result.latest.json
receipts/ecosystem-continuity/<evaluation_id>.evaluation.json
receipts/ecosystem-continuity/evaluation.latest.json
master-records/ecosystem-continuity/<evaluation_id>.evaluation.json
master-records/ecosystem-continuity/<evaluation_id>.custody.json
receipts/ecosystem-continuity/healer-intake.latest.json
receipts/ecosystem-continuity/site-projection.latest.json
receipts/ecosystem-continuity/cycle.latest.json
receipts/reusable-task/<invocation>.manifest.json
receipts/reusable-task/<invocation>.runner-result.json
receipts/reusable-task/<invocation>.runner-expiry.json
receipts/reusable-task/<invocation>.residual-recording.json
receipts/reusable-task/<invocation>.master-records-request.json
receipts/reusable-task/<invocation>.entropy-recovery.json
```

`cycle.latest.json` records the SDK diagnostic request ID, deterministic result ID, exact result ref/SHA-256, and `sdk_diagnostic_result_bound_into_ece=true` when the ECE chain completes. The reusable-task receipt chain must remain bound to the same deterministic UTC-hour invocation ID.

## Scheduler terminal-state reconciliation

The reusable-task scheduler historically treated only `AUTOMATABLE_STEPS_EXHAUSTED` as a successful idempotency terminal. That remains valid for bounded reusable tasks that finish at evidence reconciliation.

The reusable lifecycle closure merged in StegVerse-Labs/.github now has a stronger successful terminal: `ENTROPY_RECOVERY_RECORDED`. If the scheduler failed to recognize that state, a fully completed ECE lifecycle would be misclassified as retryable and could be executed again within the same UTC-hour slot.

The scheduler therefore recognizes both successful states:

```text
AUTOMATABLE_STEPS_EXHAUSTED
ENTROPY_RECOVERY_RECORDED
```

`BOUNDARY_RECORDED`, `FAILED`, missing receipts, and other nonterminal states remain unsatisfied and subject only to the existing bounded retry policy.

## Invariants

- Source repositories remain read-only during a cycle.
- Missing required local source blocks rather than fetching from GitHub/network.
- SDK diagnostic mutation is forbidden in v1.
- SDK diagnostic results cannot supply continuity state.
- Missing observation stays `NOT_OBSERVED`; unsupported claimed evidence remains subject to SDK `PROBE_REQUIRED` semantics.
- Exact SDK diagnostic result identity is retained into ECE evidence provenance.
- Master Records custody/reconstruction must round-trip exact ECE evaluation bytes before downstream intake/projection completes.
- Reusable lifecycle Master Records custody/reconstruction must round-trip the exact lifecycle request bytes before entropy recovery.
- Healer intake remains non-authorizing and cannot verify recovery.
- Site projection remains read-only/fail-closed.
- `recovery_verified` is always false for this cycle; a later independent ECE PASS is required.
- Scheduling reuses the existing reusable-task scheduler extension and creates no second scheduler.
- A successful `ENTROPY_RECOVERY_RECORDED` receipt closes the UTC-hour slot and must not be retried.

## Current proof boundary

The SDK diagnostic processor, ECE bridge, reusable lifecycle closure, resident Master Records lifecycle round trip, and scheduler terminal-state compatibility are source-level integrations. No authentic post-merge resident invocation is claimed until retained evidence exists for the same invocation across SDK diagnostic output, ECE evaluation, Master Records custody/reconstruction, Healer intake, Site projection, reusable runner evidence, runner expiry, residual recording, lifecycle custody/reconstruction, and entropy recovery.

## Next

Validate and merge the scheduler terminal-state compatibility change. Then observe one authentic resident `RT-ECOSYSTEM-CONTINUITY-EVALUATION-001` UTC-hour slot using the merged source and retain the complete same-invocation chain. Only after that chain exists should the reusable-task performance/load assessment be repeated.
