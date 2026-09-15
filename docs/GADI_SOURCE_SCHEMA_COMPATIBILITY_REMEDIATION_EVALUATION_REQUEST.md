# StegVerse-Healer Remediation Evaluation Request — GADI Source Schema Compatibility

Date: 2026-09-14

## Request identity

- Request ID: `GADI-SOURCE-SCHEMA-COMPATIBILITY-MISMATCH-001`
- Originating Goal: `STEG-BROWSER-RUNTIME-MATERIALIZATION-REMEDIATION-001`
- Originating COSV: `40000100100000`
- Owning domain: `GADI`
- Out of scope for originating Goal: `true`
- Blocks originating transition: `false`
- Interrupted GC transition: `none`
- Authority transfer: `NONE`
- Decision state: `REMEDIATION EVALUATION REQUESTED — HEALER NOT TRIGGERED BY THIS DOCUMENT`

## Observed broken condition

During repository-wide deterministic validation initiated while working on the StegBrowser Goal, GADI tests referenced `retained_projector.SOURCE_SCHEMA` while the GADI retained-node projector exposed `SOURCE_SCHEMAS` as the accepted-schema set.

This is classified as a GADI-owned source/test compatibility mismatch. It is not part of the StegBrowser transport problem and does not block the StegBrowser-specific transport-boundary assertions.

## Why this request exists

The originating Goal observed a real defect but does not own the GADI subsystem. It therefore must not absorb the GADI repair into StegBrowser scope.

The originating Goal retains the evidence, classifies the foreign owner, emits this evaluation request, and continues unrelated StegBrowser work.

## Requested Healer action

Independently evaluate whether this observed GADI defect satisfies an existing authorized remediation trigger.

Possible dispositions:

- `AUTHORIZED_TRIGGER_MATCHED_APPLY_BOUNDED_REMEDY`
- `NO_AUTHORIZED_TRIGGER_MATCH_RETAIN_OR_ROUTE_WITHOUT_REMEDY`
- `INSUFFICIENT_EVIDENCE_REQUEST_MORE_EVIDENCE`

If a trigger is matched, apply only the bounded GADI-owned remedy and retain remediation evidence. Do not claim originating-Goal completion.

## Explicit non-authorizations

This request does not:

- trigger Healer by itself;
- transfer GADI authority to the originating Goal;
- transfer WorkerCoordinator, Interlock/InTr, TV/TVC, KV/SKAP, or Master Records authority;
- authorize a repair merely because a repository-wide test failed;
- make Healer a normal stage owner, scheduler, carrier, or prerequisite;
- classify the defect as a StegBrowser transport failure;
- block unrelated StegBrowser GC transitions.

## Originating Goal continuation

```text
OUT_OF_SCOPE_FOR_CURRENT_GOAL = true
BLOCKS_ORIGINATING_TRANSITION = false
AUTHORITY_TRANSFER = NONE
ORIGINATING_GOAL_ACTION = RETAIN_EVIDENCE_EMIT_REQUEST_CONTINUE_STEGBROWSER_SPECIFIC_VALIDATION
```

## Evidence lineage

Observed validation failure class:

`GADI_SOURCE_SCHEMA_TEST_API_MISMATCH`

Observed mismatch:

`tests use retained_projector.SOURCE_SCHEMA`

versus projector accepted-schema API:

`SOURCE_SCHEMAS = {LEGACY_SOURCE_SCHEMA, GENERIC_SOURCE_SCHEMA}`

This request records the observed defect and asks for independent evaluation only. It does not claim that the evidence is sufficient for an authorized remedy until StegVerse-Healer evaluates it.
