# Failure Mailbox Benchmark Mirror Handoff

Updated: 2026-08-18
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: HISTORICAL_BENCHMARK_ACTIVE_SOVEREIGN_EXECUTION_BINDING_PENDING

## Goal

Benchmark the expanded Healer failure-mailbox package against the proven ARA deterministic replay-ledger baseline, fine-tune only from measured evidence, then package the transport-neutral product only after benchmark gates pass.

## Installed benchmark surfaces

- `failure_mailbox/benchmark_fixtures.json`
- `failure_mailbox/benchmark.py`
- `failure_mailbox/github_notification_parser.py`
- `failure_mailbox/episode_analysis.py`
- `failure_mailbox/benchmarks/historical-tranche-001.json`
- `tests/test_github_notification_parser.py`
- `tests/test_failure_episode_analysis.py`
- `handoffs/HEALER-FAILURE-MAILBOX-SOVEREIGN-BENCHMARK-001.json`
- `docs/FAILURE_MAILBOX_BENCHMARK_PLAN.md`

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

The incident ledger intentionally includes workflow/job identity. Therefore distinct workflows must not be merged merely because they share a commit and failure class. To measure systemic fanout without corrupting incident identity, the package now has a second deterministic layer:

```text
notification -> incident -> failure episode -> cross-repo neighbor/propagation candidate
```

`failure_mailbox/episode_analysis.py` groups incidents by repository + branch/PR context + commit + failure class. It preserves every incident ID while measuring notification count, workflow count, incident count, duration and amplification candidacy. Episode records never claim causality or authority.

The benchmark runner is now schema `stegverse.healer.failure-mailbox-benchmark/v0.2` and requires episode-layer correctness in addition to the original incident/lifecycle checks.

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

## Sovereign execution state

`HEALER-FAILURE-MAILBOX-SOVEREIGN-BENCHMARK-001` is `HANDOFF_READY` with command:

```text
python3 failure_mailbox/benchmark.py
```

The existing sovereign scheduler currently has no registered failure-mailbox benchmark target/handler. This is the concrete remaining execution binding gap. The hosted Test Readiness route was tested and rejected for this purpose because private-source anonymous checkout cannot satisfy the current TV/TVC_ONLY / no-GitHub-token boundary. No hosted validation success is being substituted for sovereign execution.

## Benchmark phases

1. Deterministic synthetic benchmark: replay safety, incident compression, duplicate no-op, recurrence, sandbox routing, resolution-evidence gating, temporal neighbor detection, failure-episode amplification, throughput, and ledger size.
2. Historical unread GitHub-failure corpus benchmark: real notification-to-incident compression, failure-episode amplification, recurrence history, failure-family frequency, repository frequency, propagation candidates, false splits/false merges, throughput, and state growth.
3. Live incremental shadow benchmark on the existing sovereign Healer scheduler before package release.

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

- deterministic sovereign benchmark passes;
- historical-corpus benchmark completes and tuning decisions are recorded;
- live shadow benchmark demonstrates stable incremental classification;
- core remains transport-neutral and credential-free;
- adapters remain separable;
- API/schema is versioned;
- install/run documentation and sample deployment are validated;
- benchmark report is retained as release evidence.

## Current boundary

Source installed != benchmark executed != tuned != packaged != released.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
