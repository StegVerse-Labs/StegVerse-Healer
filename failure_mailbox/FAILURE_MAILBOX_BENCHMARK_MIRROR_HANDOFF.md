# Failure Mailbox Benchmark Mirror Handoff

Updated: 2026-08-18
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: DETERMINISTIC_AND_BOUNDED_HISTORICAL_REGRESSIONS_VALIDATED_BROADER_CORPUS_ACTIVE_LIVE_SHADOW_PENDING

## Goal

Benchmark the expanded Healer failure-mailbox package against the proven ARA deterministic replay-ledger baseline, fine-tune only from measured evidence, then package the transport-neutral product only after benchmark gates pass.

## Current implemented surfaces

```text
failure_mailbox/incident_engine.py
failure_mailbox/github_notification_parser.py
failure_mailbox/episode_analysis.py
failure_mailbox/dependency_analysis.py
failure_mailbox/dependency_edges.json
failure_mailbox/backfill.py
failure_mailbox/failure-observation.schema.json
failure_mailbox/benchmark.py
failure_mailbox/benchmark_fixtures.json
failure_mailbox/benchmarks/historical-tranche-001.json
failure_mailbox/benchmarks/historical-tranche-001-sanitized.jsonl
failure_mailbox/benchmarks/historical-tranche-001-regression-validation.json
failure_mailbox/benchmarks/historical-multirepo-window-001-sanitized.jsonl
failure_mailbox/benchmarks/historical-multirepo-window-001-validation.json
failure_mailbox/benchmarks/deterministic-v0.2-validation.json
failure_mailbox/benchmarks/deterministic-v0.3-validation.json
failure_mailbox/benchmarks/backfill-v0.1-validation.json
tests/test_failure_mailbox_incident_engine.py
tests/test_github_notification_parser.py
tests/test_failure_episode_analysis.py
tests/test_failure_dependency_analysis.py
tests/test_failure_mailbox_backfill.py
tests/test_failure_mailbox_historical_tranche.py
tests/test_failure_mailbox_multirepo_window.py
```

## Layering contract

```text
mail notification
-> transport notification result
-> semantic failure incident
-> failure episode
-> temporal neighbor candidate
-> declared-dependency candidate
-> governed repair / sandbox lifecycle
```

These are intentionally distinct abstractions:

```text
email != incident
incident != episode
episode != cause
neighbor candidate != causality
declared dependency + temporal proximity != causality
```

## Deterministic benchmark

Benchmark schema `stegverse.healer.failure-mailbox-benchmark/v0.3` is validated PASS. It requires deterministic replay, duplicate no-op, incident recurrence, sandbox routing for unable/impossible repair, evidence-gated archive eligibility, temporal neighbor detection, incident preservation, positive multi-workflow amplification detection, and explicit non-causality.

Latest retained deterministic evidence: `failure_mailbox/benchmarks/deterministic-v0.3-validation.json`.

## Historical single-repository tranche

Connected Gmail initially measured one bounded `StegVerse-Labs/StegVerse-SCW` branch/commit cluster:

```text
branch: repair-repo-alignment-check-v2
commit: 86971ef
failure notifications by ID search: 50
No jobs were run notifications by ID search: 48
other notifications: 2
no-jobs share: 0.96
```

A sanitized 47-observation topology was retained without raw mailbox IDs because the detailed content retrieval returned 47 visible records while the ID-only search measured 50; the 47-record regression is therefore not represented as the complete 50-message source set.

Validated regression:

```text
Test Readiness run: 32213618964
job: 95950934196
tests: 48/48 PASS
sanitized observations: 47
distinct incidents: 47
failure episodes: 2
largest NO_JOBS_RUN episode: 45 workflow surfaces
mailbox mutation: false
causality claimed: false
```

This established that the correct reduction layer for that burst is episode, not incident. Distinct workflow incidents remain distinct.

## Transport result versus semantic failure family

The observation schema is now `stegverse.healer.github-failure-observation/v0.2`.

GitHub mail transport result is recorded separately as `notification_result_class`. Generic text such as `All jobs have failed` or `Some jobs were not successful` no longer becomes a semantic failure family by itself. Semantic classification is added only when supported by the observed surface or later evidence.

Examples:

```text
No jobs were run -> notification_result_class=NO_JOBS_RUN; failure_class=NO_JOBS_RUN
Validate chain continuation + generic job failure -> notification_result_class=WORKFLOW_JOB_FAILURE; failure_class=CONTINUITY_FAILURE
Test Readiness + generic job failure -> notification_result_class=WORKFLOW_JOB_FAILURE; failure_class omitted at parser boundary and may remain UNKNOWN_FAILURE
```

The parser remains credential-neutral and performs no mailbox mutation.

## Dependency-aware multi-repository historical regression

Authoritative dependency edges currently encoded from `GCAT-BCAT-Engine/Publisher:docs/PUBLISHER_MIRROR_HANDOFF.md#Cross-repository-succession`:

```text
StegVerse-Labs/Site -> GCAT-BCAT-Engine/Publisher
GCAT-BCAT-Engine/Publisher -> StegVerse-Labs/admissibility-wiki
```

No other edge is inferred merely from temporal proximity.

A sanitized bounded 21-observation window derived from the connected mailbox was validated:

```text
Test Readiness run: 32213979768
job: 95951919538
tests: 53/53 PASS
parsed observations: 21
distinct incidents: 7
failure episodes: 13
amplification episodes: 6
declared-edge candidates: 11
Site -> Publisher direction-matching candidates: 6
Publisher -> admissibility-wiki direction-opposing candidates: 5
causality claimed: false
mailbox mutation: false
benchmark v0.3: PASS
```

The direction-opposing candidates are retained as counterevidence. They are not discarded to make a propagation narrative fit the declared topology.

Retained evidence: `failure_mailbox/benchmarks/historical-multirepo-window-001-validation.json`.

## Historical backfill engine

`failure_mailbox/backfill.py` is validated for deterministic JSONL backfill, duplicate replay, quarantine of invalid/unsupported forms, incident/episode construction, and zero mailbox mutation. It reports transport-result frequency separately from semantic failure-family frequency.

Latest retained backfill validation: `failure_mailbox/benchmarks/backfill-v0.1-validation.json`.

## Validation/runtime distinction

Hosted `Test Readiness` is source/behavior validation evidence only. It grants no runtime, mailbox, repair, release, credential, or heartbeat authority.

A separate sovereign one-shot task remains registered in `StegVerse-Labs/.github`:

```text
task: HEALER-FAILURE-MAILBOX-SOVEREIGN-BENCHMARK-001
worker: healer-failure-mailbox-benchmark-worker
adapter: process:healer-failure-mailbox-benchmark-v1
```

It requires an already-materialized local Healer source, sovereign node declaration, collision-safe claim, TV/TVC authority, no GitHub token, and no remote checkout.

Last inspected WorkerCoordinator runtime state remained `CARRIER_REFERENCE_ONLY_NO_TASK_EXECUTION` with no assignment packets seen. Sovereign benchmark execution is therefore still pending and must not be inferred from hosted validation.

## Remaining benchmark work

1. Complete broader historical mailbox analysis across multiple bounded windows/pages rather than extrapolating from the first-page samples.
2. Add only authoritative repository dependency edges and preserve temporal-only neighbors where no edge is established.
3. Measure recurrence, episode frequency, amplification, false splits/false merges, parse quarantine, state growth, and cross-repository candidate stability across the broader corpus.
4. Use measured misclassifications to fine-tune fingerprint, semantic-family, episode, and dependency scoring rules.
5. Admit a TV/TVC mailbox transport for live incremental shadow processing; do not mutate mail during shadow benchmark.
6. Consume a sovereign WorkerCoordinator benchmark receipt when the registered machine task is actually executed.
7. Package only after historical and live-shadow gates pass.

## Packaging gate

```text
deterministic benchmark: PASS
positive amplification detection: PASS
historical backfill engine: PASS
single-repo historical regression: PASS
dependency-aware bounded multi-repo regression: PASS
broader historical corpus benchmark: ACTIVE / NOT COMPLETE
live incremental shadow benchmark: PENDING
sovereign machine benchmark receipt: PENDING
package release allowed: false
```

Source validated != sovereign execution != historical benchmark complete != live shadow complete != packaged != released.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
