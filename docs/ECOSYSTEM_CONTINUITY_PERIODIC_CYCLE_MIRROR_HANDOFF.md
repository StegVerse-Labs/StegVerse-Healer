# Ecosystem Continuity Periodic Cycle Mirror Handoff

Updated: 2026-09-12

```text
Parent Goal Task ID: ECOSYSTEM-CONTINUITY-EVALUATOR-001
Child Goal Task ID: SDK-ECOSYSTEM-DIAGNOSTIC-PROCESSOR-001
Parent COSV: 71000000100111
Child COSV: 71000000101000
Repository: StegVerse-Labs/StegVerse-Healer
Branch: feature/ece-sdk-diagnostic-bridge-001
State: SDK DIAGNOSTIC BRIDGE SOURCE IMPLEMENTED / VALIDATION PENDING
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
-> exact Master Records custody/reconstruction
-> Healer intake
-> Site-safe projection
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
```

`cycle.latest.json` records the SDK diagnostic request ID, deterministic result ID, exact result ref/SHA-256, and `sdk_diagnostic_result_bound_into_ece=true` when the chain completes.

## Invariants

- Source repositories remain read-only during a cycle.
- Missing required local source blocks rather than fetching from GitHub/network.
- SDK diagnostic mutation is forbidden in v1.
- SDK diagnostic results cannot supply continuity state.
- Missing observation stays `NOT_OBSERVED`; unsupported claimed evidence remains subject to SDK `PROBE_REQUIRED` semantics.
- Exact SDK diagnostic result identity is retained into ECE evidence provenance.
- Master Records custody/reconstruction must round-trip exact ECE evaluation bytes before downstream intake/projection completes.
- Healer intake remains non-authorizing and cannot verify recovery.
- Site projection remains read-only/fail-closed.
- `recovery_verified` is always false for this cycle; a later independent ECE PASS is required.
- Scheduling reuses the existing reusable-task scheduler extension and creates no second scheduler.

## Current proof boundary

The SDK processor source is merged+validated, and this bridge source is implemented on the current Healer branch. No authentic resident SDK diagnostic request/result, resident ECE evaluation, Master Records runtime custody, Healer runtime intake, Site runtime projection, or recovery loop is claimed until retained resident evidence exists.

## Next

Pass exact-head Healer validation and merge this bridge only if green. Then reconcile the child SDK task and parent ECE handoffs. After merge, observe one authentic resident `RT-ECOSYSTEM-CONTINUITY-EVALUATION-001` slot producing the SDK diagnostic result + ECE + custody/intake/projection chain before claiming the SDK diagnostic continuity lane operational.
