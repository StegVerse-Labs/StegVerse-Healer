# Failure Mailbox Benchmark Mirror Handoff

Updated: 2026-08-18
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: `DETERMINISTIC_V0_4_VALIDATED_HISTORICAL_ACTIVE_SHADOW_CORE_VALIDATED_SOVEREIGN_INPUT_PENDING`

## Goal

Develop and benchmark a transport-neutral Healer failure-intelligence package that reconstructs GitHub failure observations into durable incidents, recurrence, failure episodes, bounded dependency candidates, coverage state, repair/sandbox lifecycle and evidence-qualified archival without giving mail transport, GitHub, runtime, release or heartbeat authority to the analysis core.

Package release remains prohibited until the historical corpus benchmark is sufficiently complete, a live incremental shadow batch is executed on the sovereign runtime with independently measured source coverage, and retained release evidence satisfies the package gate.

## Current product layers

```text
source-stream coverage
-> notification transport result
-> semantic incident
-> recurrence/history
-> failure episode / amplification
-> temporal neighbor
-> declared dependency candidate + counterevidence
-> governed repair / sandbox lifecycle
-> evidence-qualified archival
```

Required distinctions:

- email != incident
- incident != episode
- episode != cause
- temporal neighbor != dependency
- declared dependency + temporal proximity != causality
- notification result != semantic failure family
- source coverage != parser quality
- source validation != sovereign execution != release

## Developed source

- `failure_mailbox/incident_engine.py`
- `failure_mailbox/github_notification_parser.py`
- `failure_mailbox/episode_analysis.py`
- `failure_mailbox/dependency_analysis.py`
- `failure_mailbox/dependency_edges.json`
- `failure_mailbox/backfill.py`
- `failure_mailbox/coverage_monitor.py`
- `failure_mailbox/shadow.py`
- `failure_mailbox/benchmark.py`
- versioned schemas, fixtures and deterministic tests under `failure_mailbox/` and `tests/`

These are developed implementation surfaces, not placeholders.

## Parser semantics

GitHub notification transport result and semantic failure family are separate fields.

Examples:

- `notification_result_class=WORKFLOW_JOB_FAILURE` may remain `failure_class=UNKNOWN_FAILURE` until stronger evidence exists.
- `Validate chain continuation` may be classified as `CONTINUITY_FAILURE` because its workflow semantics support that family.
- `No jobs were run` remains a distinct `NO_JOBS_RUN` class.

Generic GitHub status wording must never be promoted into an unsupported semantic root cause.

## Incident and episode semantics

Incident identity preserves repository/workflow/job/context and semantic fingerprint. Different workflow surfaces are not collapsed merely because they share a commit.

Failure episodes provide the higher-level reduction needed for fanout/amplification analysis while retaining all constituent incident IDs. Episode objects remain non-causal and non-authorizing.

## Coverage monitor

`failure_mailbox/coverage_monitor.py` evaluates independently measured source activity against accepted shadow intake over the same bounded interval.

Typed states:

- `COMPLETE_COVERAGE`
- `PARTIAL_COVERAGE`
- `COVERAGE_GAP`
- `NO_SOURCE_ACTIVITY`
- `INVALID_COVERAGE_EVIDENCE`

Invariant:

```text
source_count > 0 and ingested_count == 0
=> COVERAGE_GAP
```

A monitor that stops ingesting while the source stream continues must therefore become visibly unhealthy instead of silently appearing idle.

## Incremental shadow processor

`failure_mailbox/shadow.py` consumes already-materialized JSONL batches and persists an incremental ledger and shadow state.

Properties validated:

- deterministic `batch_id` + input hash;
- same batch/hash replay => `DUPLICATE_BATCH_NOOP`;
- same batch ID with conflicting hash => fail closed;
- source coverage is measured using source count vs delivered input rows;
- parse/quarantine quality is measured separately;
- malformed-but-delivered mail is not mislabeled as a transport outage;
- source-count greater than delivered rows produces partial/gap coverage;
- no mailbox mutation, authority, heartbeat or package-release effect.

## Deterministic benchmark v0.4

Current benchmark schema:

`stegverse.healer.failure-mailbox-benchmark/v0.4`

Exact-head validation:

- PR: `#28` validation marker, closed without merge
- workflow: `Test Readiness`
- run: `32214501733`
- job: `95953368889`
- deterministic tests: `60/60 PASS`
- benchmark: `PASS`

v0.4 package gates now require:

- deterministic incident/replay/lifecycle behavior;
- episode/amplification behavior;
- `fixture_intake_complete_coverage`;
- positive `coverage_gap_self_detection`;
- coverage monitor grants no mailbox/authority/heartbeat power;
- historical corpus benchmark;
- live incremental benchmark.

`package_release_allowed=false` remains mandatory.

Retained evidence:

- `failure_mailbox/benchmarks/deterministic-v0.4-validation.json`
- `failure_mailbox/benchmarks/intake-coverage-discontinuity-001.json`

## Historical corpus evidence

### July bounded window

Measured connected-mailbox interval: approximately 17 minutes on 2026-07-08.

Exact source denominator: `137` GitHub failure notifications.

Repository distribution:

- StegVerse-SCW: `109`
- Site: `16`
- admissibility-wiki: `10`
- Publisher: `1`
- Standing-Proof-Engine: `1`

Execution-result distribution:

- `NO_JOBS_RUN`: `96`
- unsuccessful executed jobs: `41`

All 96 no-job notifications were in the SCW share. Therefore SCW generated 109 notifications: 96 non-executing workflow surfaces plus 13 actual job-failure notifications.

A sanitized SCW regression preserves 47 workflow incidents and reduces them to two episode-level conditions, including a dominant 45-workflow `NO_JOBS_RUN` episode.

Validation:

- PR #25 marker, closed without merge
- Test Readiness run `32213618964`
- job `95950934196`
- `48/48 PASS`

### Dependency-aware historical regression

Only declared repository relationships may raise dependency candidates. The initial declared edge set is grounded in Publisher's canonical succession contract:

```text
Site -> Publisher -> admissibility-wiki
```

A bounded sanitized multi-repo fixture reconstructed 21 observations into 7 incidents and 13 episodes. It produced:

- 6 direction-matching Site -> Publisher candidates;
- 5 Publisher -> admissibility-wiki candidates whose observed ordering opposed the declared direction.

The opposing ordering is retained as counterevidence; no candidate is a causality claim.

Validation:

- PR #26 marker, closed without merge
- run `32213979768`
- job `95951919538`
- `53/53 PASS`

### Recent August window

Measured connected-mailbox interval: 2026-08-18 19:00-19:20 PDT.

- direct GitHub failure notifications: `24`
- repositories: `9`
- Healer `Test Readiness` notifications: `10`
- old `StegVerse/GitHub Failures/New` label intake: `0`

The sanitized recent-window regression parsed 24/24 with zero quarantine, preserved 9 repositories, reconstructed 15 incidents, and correctly reduced the 10 Healer `Test Readiness` notifications to one recurring incident with `occurrence_count=10`.

Validation:

- PR #29 marker, closed without merge
- run `32214594137`
- job `95953619321`
- `61/61 PASS`

### Legacy intake discontinuity

Newest observed GitHub failure carrying the legacy failure label:

`2026-07-08T09:10:43-07:00`

Recent August window:

```text
direct source notifications: 24
legacy labeled intake:       0
coverage state:              COVERAGE_GAP
```

This demonstrates an observed ~41-day label/intake discontinuity. It does **not** establish why the prior automation stopped.

Product consequence: failure monitoring must monitor its own bounded source-to-intake coverage.

## Shadow-core validation

PR #30 marker, closed without merge.

- run: `32214695207`
- job: `95953889359`
- deterministic tests: `66/66 PASS`
- benchmark v0.4 remained PASS.

Validated behavior includes complete recent-window coverage, duplicate no-op, conflicting replay fail-closed, partial transport coverage, parser quarantine separated from transport coverage, persistent shadow state and zero mailbox mutation/authority effect.

## Sovereign WorkerCoordinator integration

Two Healer-owned tasks are registered centrally in `StegVerse-Labs/.github`.

### Deterministic sovereign benchmark

Task: `HEALER-FAILURE-MAILBOX-SOVEREIGN-BENCHMARK-001`

State: `HANDOFF_READY`

No sovereign execution receipt has been observed.

### Live shadow batch

Task: `HEALER-FAILURE-MAILBOX-LIVE-SHADOW-001`

Worker: `healer-failure-mailbox-shadow-worker`

Adapter: `process:healer-failure-mailbox-shadow-v1`

Required non-secret local locators:

- `STEGVERSE_HEALER_SOURCE_ROOT`
- `STEGVERSE_HEALER_SHADOW_BATCH_PATH`
- `STEGVERSE_HEALER_SHADOW_MANIFEST_PATH`

The shadow worker must never receive Gmail/OAuth/GitHub credentials. It consumes only an already-materialized bounded JSONL batch plus a non-secret manifest that attests:

- `batch_id`
- `source_count`
- `window_start`
- `window_end`
- `source_ref`
- `mailbox_mutated=false`
- `credential_authority=TV/TVC`

Current blockers:

- TV/TVC-owned mailbox batch + manifest not yet observed;
- canonical scheduler claim not yet bound;
- sovereign shadow execution receipt not yet observed.

Therefore registration is **not** live processing or activation.

## Central source-validation evidence

Central `.github` source-validation receipt:

`StegVerse-Labs/.github:docs/receipts/healer-failure-mailbox-shadow-source-validation-2026-08-18.md`

The complete central repository validation is currently red because of independent migration debt, but the new Healer shadow worker's four focused tests all passed inside the canonical 431-test run. Executable-handoff validation, workflow hygiene, organization control-plane invariants and active-worker invariants also produced positive evidence after bounded repairs.

Do not restore pre-independent-oscillator heartbeat semantics merely to satisfy stale tests.

## Credential-bearing mailbox transport boundary

Credential-bearing Gmail observation/materialization belongs to TV/TVC, not Healer.

The existing TVC provider-operation broker establishes the non-exportable credential authority pattern, but current admitted provider profiles are model/chain oriented and do not semantically admit Gmail mailbox observation. A narrower TVC mailbox observation/materialization capability is therefore still required unless an existing equivalent surface is discovered.

Required output from that TVC-owned transport is only:

1. sanitized bounded JSONL observations;
2. non-secret source-count/window manifest;
3. no exported provider credential;
4. evidence binding source count to the same bounded interval.

## Packaging gate

Release remains prohibited until all are true:

- deterministic benchmark v0.4 remains PASS;
- historical-corpus evaluation/tuning is sufficiently complete and retained;
- a TV/TVC-owned mailbox observation/materialization path is validated;
- live shadow processes one or more independently counted bounded source batches on sovereign runtime;
- live coverage and parse/quarantine metrics remain stable;
- core remains transport-neutral and credential-free;
- adapters remain separable;
- API/schema and install/run documentation are versioned and validated;
- release evidence is retained.

## Exact next actions

1. Discover or implement the narrow TVC mailbox observation/materialization capability under TV/TVC non-exportable credential authority.
2. Produce a bounded sanitized source batch + manifest without exposing credentials to Healer.
3. Recheck central WorkerCoordinator state and duplicate claims.
4. Bind and execute `HEALER-FAILURE-MAILBOX-LIVE-SHADOW-001` under a fresh canonical claim.
5. If a coverage gap or repairable failure occurs, repair and rerun the same predicate.
6. If the worker reports unable/impossible-to-repair, submit the governed sandbox resolution task.
7. Consume and retain the live receipt before considering package release.

## Completion accounting

```text
core_incident_parser_episode_dependency_source: COMPLETE_VALIDATED
coverage_monitor_source: COMPLETE_VALIDATED
historical_backfill_source: COMPLETE_VALIDATED
shadow_processor_source: COMPLETE_VALIDATED
benchmark_v0_4: PASS
historical_bounded_windows: ACTIVE_VALIDATED_PARTIAL_CORPUS
central_shadow_worker_registration: INSTALLED_FOCUSED_TESTS_PASS
TVC_mailbox_materialization: NOT_IMPLEMENTED_OR_NOT_DISCOVERED
sovereign_shadow_execution: NOT_OBSERVED
package_release: PROHIBITED
archive_ready: false
```

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
