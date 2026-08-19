# Failure Mailbox Benchmark and Packaging Gate

Goal: benchmark the Healer failure-mailbox package against the proven deterministic replay-ledger behavior of the ARA deployment mailbox monitor while measuring the additional Healer capabilities before packaging.

## Baseline inherited from ARA

The ARA monitor established the expected base behaviors:

- deterministic notification identity;
- replay-safe ledger continuity;
- duplicate no-op behavior;
- fail-closed handling of conflicting/invalid inputs;
- oldest-first transport processing;
- durable processing receipts/state;
- no authority derived from email receipt.

Healer must preserve those properties while adding failure-specific semantics.

## Added Healer capabilities to benchmark

1. canonical failure incident compression across repeated notifications;
2. failure-family classification and recurrence history;
3. stable incident inventory numbering;
4. lifecycle state tracking;
5. `UNABLE_TO_REPAIR` / `IMPOSSIBLE_TO_REPAIR` -> `SANDBOX_REQUIRED` routing;
6. resolution-evidence requirement before mailbox archive eligibility;
7. cross-repository temporal neighbor candidates without causal overclaim;
8. failure-family and repository frequency analysis;
9. notification amplification and incident-compression metrics;
10. bounded ledger size and processing throughput.

## Three benchmark phases

### Phase A — deterministic synthetic benchmark

Executable surfaces:

- `failure_mailbox/benchmark_fixtures.json`
- `failure_mailbox/benchmark.py`

This phase tests correctness independent of mailbox credentials and live repository state.

Acceptance requires all deterministic checks PASS.

### Phase B — historical unread GitHub-failure corpus

After an admitted TV/TVC mailbox transport exists, ingest the preserved unread GitHub-failure corpus without archiving during the benchmark.

Measure:

- total source notifications;
- distinct incidents;
- notifications per incident;
- incident count by failure family and repository;
- recurrence intervals;
- same-failure recurrence after a claimed resolution;
- temporal cross-repository neighbor candidates;
- dependency-edge-supported propagation candidates;
- fraction of messages classified as duplicate/repeated observations;
- processing throughput and ledger growth.

This historical corpus is the primary tuning dataset for fingerprinting, incident identity, neighbor windows, and propagation scoring.

### Phase C — live incremental shadow benchmark

Run the transport + engine in observation-only/shadow posture through the existing sovereign Healer scheduler. Do not auto-repair or archive as part of the benchmark.

Measure false splits, false merges, time-to-classification, repeated incident recognition, lifecycle synchronization with worker registry outcomes, and processing cost.

## Fine-tuning targets

Tune only from measured evidence. Primary tuning knobs:

- semantic failure fingerprint normalization;
- incident identity fields;
- branch/PR treatment;
- temporal neighbor window;
- dependency-edge weights;
- shared-commit and shared-artifact weights;
- recurrence threshold;
- known intentional/fail-closed/no-jobs-run classifications;
- archive eligibility safeguards.

A tuning change must improve at least one measured target without regressing deterministic replay, lifecycle safety, authority boundaries, or resolution-evidence requirements.

## Packaging gate

Do not publish/release the commercial package merely because source exists.

Packaging becomes eligible only when:

1. deterministic benchmark passes;
2. historical-corpus benchmark is complete and tuning decisions are recorded;
3. live shadow benchmark demonstrates stable incremental classification;
4. no NON-TV/TVC credential is embedded in the core package;
5. transport adapters are separable from the core engine;
6. resolution archival remains evidence-gated;
7. sandbox routing is preserved;
8. package API/schema is versioned;
9. install/run documentation and sample deployment are validated;
10. benchmark report is retained as release evidence.

## Product boundary

The deployable product should expose a transport-neutral core and optional adapters. StegVerse/COSV/HB integrations are advanced integrations, not prerequisites for a customer to use the failure-intelligence engine.

Current state: BENCHMARK_HARNESS_SOURCE_INSTALLED; execution evidence pending.
