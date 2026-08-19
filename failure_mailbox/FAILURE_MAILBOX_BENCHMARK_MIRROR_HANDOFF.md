# Failure Mailbox Benchmark Mirror Handoff

Updated: 2026-08-18
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: DETERMINISTIC_BENCHMARK_VALIDATED_HISTORICAL_BENCHMARK_ACTIVE_LIVE_SHADOW_PENDING

## Goal

Benchmark the expanded Healer failure-mailbox package against the proven ARA deterministic replay-ledger baseline, fine-tune only from measured evidence, then package the transport-neutral product only after benchmark gates pass.

## Installed benchmark surfaces

- `failure_mailbox/benchmark_fixtures.json`
- `failure_mailbox/benchmark.py`
- `failure_mailbox/github_notification_parser.py`
- `failure_mailbox/episode_analysis.py`
- `failure_mailbox/benchmarks/historical-tranche-001.json`
- `failure_mailbox/benchmarks/deterministic-v0.2-validation.json`
- `tests/test_github_notification_parser.py`
- `tests/test_failure_episode_analysis.py`
- `handoffs/HEALER-FAILURE-MAILBOX-SOVEREIGN-BENCHMARK-001.json`
- `docs/FAILURE_MAILBOX_BENCHMARK_PLAN.md`

## Deterministic benchmark validation

PR #22 exact-head validation succeeded for head `ab925f6133e221634f3b5d5141a772ff732add23`; validated changes were squash-merged to main as `150c48ced79f05bcf3c91ad7337a19fb3b11e57e`.

Validation evidence:

- workflow: `Test Readiness`
- run ID: `32213145668`
- job ID: `95949591259`
- result: `SUCCESS`
- deterministic tests: 44 / 44 PASS
- benchmark schema: `stegverse.healer.failure-mailbox-benchmark/v0.2`
- benchmark result: `PASS`
- deterministic core gate: PASS
- package release gate: CLOSED

Measured synthetic metrics in that run:

- input notifications: 8
- unique observations: 8
- distinct incidents: 6
- notification-to-incident ratio: 1.3333333333333333
- duplicate replays: 2
- repeated incidents: 2
- neighbor candidates: 6
- failure episodes: 8
- amplification episodes: 0
- archive-eligible messages after durable resolution evidence: 2
- observed microbenchmark throughput: ~13094 observations/second; this is not a production-capacity claim

The zero synthetic amplification-episode count is a benchmark-fixture gap, not an episode-engine failure: the v0.1 fixture does not yet include a same-commit, multi-workflow fanout burst. The historical corpus does. The next deterministic tuning step must add such a fixture and require positive amplification detection.

## Measured historical result

The first bounded historical Gmail tranche measured one `StegVerse-Labs/StegVerse-SCW` branch/commit cluster:

- branch: `repair-repo-alignment-check-v2`
- commit fragment: `86971ef`
- labeled failure notifications: 50
- `No jobs were run` notifications: 48
- other failure notifications: 2
- no-jobs share: 0.96

This establishes notification amplification in the historical corpus. It does not by itself establish 50 incidents, one incident, or causality.

## Fine-tuning correction derived from the historical tranche

The incident ledger intentionally includes workflow/job identity. Distinct workflows must not be merged merely because they share a commit and failure class. To measure systemic fanout without corrupting incident identity, the package has a second deterministic layer:

```text
notification -> incident -> failure episode -> cross-repo neighbor/propagation candidate
```

`failure_mailbox/episode_analysis.py` groups incidents by repository + branch/PR context + commit + failure class. It preserves every incident ID while measuring notification count, workflow count, incident count, duration and amplification candidacy. Episode records never claim causality or authority.

## Real-mail parser hardening

`failure_mailbox/github_notification_parser.py` was derived from actual connected-mailbox examples and supports:

- `[repo] Run failed: workflow - branch (sha)`;
- `[repo] PR run failed: workflow - PR context (sha)`;
- `No jobs were run` classification;
- `All jobs have failed` / `Some jobs were not successful` classification;
- GitHub Actions run-ID extraction from message body;
- branch versus PR context preservation;
- observation-only authority and heartbeat effects.

The parser is credential-neutral and performs no mailbox mutation.

## Validation/runtime distinction

The existing GitHub-hosted `Test Readiness` lane successfully fetched and validated the exact private-source PR head with an empty credential-bearing environment and `permissions: {}`. That hosted success is valid source/behavior validation evidence only. It is not sovereign runtime execution, mailbox processing, activation, or release authority.

A separate one-shot sovereign task is registered in `StegVerse-Labs/.github` as `HEALER-FAILURE-MAILBOX-SOVEREIGN-BENCHMARK-001` with WorkerCoordinator process adapter `process:healer-failure-mailbox-benchmark-v1`. It requires an already-materialized `STEGVERSE_HEALER_SOURCE_ROOT`, a sovereign node declaration, a scheduler claim, no GitHub token, no remote checkout, and TV/TVC authority.

The last inspected WorkerCoordinator runtime state remained `CARRIER_REFERENCE_ONLY_NO_TASK_EXECUTION` with no assignment packets seen. Therefore sovereign benchmark execution remains pending and must not be inferred from hosted validation.

## Benchmark phases

1. Deterministic synthetic benchmark: PASS at v0.2; next tuning adds a positive multi-workflow amplification fixture and revalidates.
2. Historical unread GitHub-failure corpus benchmark: active; measure real notification-to-incident compression, failure-episode amplification, recurrence history, failure-family frequency, repository frequency, propagation candidates, false splits/false merges, throughput, and state growth.
3. Live incremental shadow benchmark on the admitted sovereign runtime before package release.

## Fine-tuning targets

Tune only from measured evidence:

- failure fingerprint normalization;
- incident identity fields;
- branch/PR treatment;
- recurrence thresholds;
- failure-episode grouping fields;
- temporal neighbor window;
- dependency-edge and shared-commit weights;
- intentional/fail-closed/no-jobs-run classifications;
- archive safeguards.

No tuning may regress deterministic replay, lifecycle safety, sandbox routing, resolution-evidence requirements, authority boundaries, or heartbeat independence.

## Packaging gate

Package release remains prohibited until:

- the tuned deterministic benchmark passes, including positive amplification detection;
- historical-corpus benchmark completes and tuning decisions are recorded;
- live shadow benchmark demonstrates stable incremental classification;
- core remains transport-neutral and credential-free;
- adapters remain separable;
- API/schema is versioned;
- install/run documentation and sample deployment are validated;
- benchmark reports are retained as release evidence.

## Current boundary

Validated source != sovereign execution != historical benchmark complete != live shadow complete != packaged != released.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
