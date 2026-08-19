# Failure Mailbox Benchmark Mirror Handoff

Updated: 2026-08-18
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: BENCHMARK_HARNESS_SOURCE_INSTALLED_EXECUTION_PENDING

## Goal

Benchmark the expanded Healer failure-mailbox package against the proven ARA deterministic replay-ledger baseline, fine-tune only from measured evidence, then package the transport-neutral product only after benchmark gates pass.

## Installed benchmark surfaces

- `failure_mailbox/benchmark_fixtures.json`
- `failure_mailbox/benchmark.py`
- `docs/FAILURE_MAILBOX_BENCHMARK_PLAN.md`

Source commits:

- fixtures: `3a167801b4fd852bb66de1b5d672c5014f944763`
- runner: `51cc655bc92e926c018489b5559b6e4feb929ec5`
- plan: `fa56c1b299faf4530e353a3cef6e0293317ac5eb`

## Benchmark phases

1. Deterministic synthetic benchmark: replay safety, incident compression, duplicate no-op, recurrence, sandbox routing, resolution-evidence gating, temporal neighbor detection, throughput, and ledger size.
2. Historical unread GitHub-failure corpus benchmark after admitted TV/TVC mailbox transport: real notification-to-incident compression, recurrence history, failure-family frequency, repository frequency, propagation candidates, false splits/false merges, throughput, and state growth.
3. Live incremental shadow benchmark on the existing sovereign Healer scheduler before package release.

## Fine-tuning targets

Tune only from measured evidence:

- failure fingerprint normalization;
- incident identity fields;
- branch/PR treatment;
- recurrence thresholds;
- temporal neighbor window;
- dependency-edge and shared-commit weights;
- intentional/fail-closed/no-jobs-run classifications;
- archive safeguards.

No tuning may regress deterministic replay, lifecycle safety, sandbox routing, resolution-evidence requirements, authority boundaries, or heartbeat independence.

## Packaging gate

Package release remains prohibited until:

- deterministic benchmark passes;
- historical-corpus benchmark completes and tuning decisions are recorded;
- live shadow benchmark demonstrates stable incremental classification;
- core remains transport-neutral and credential-free;
- adapters remain separable;
- API/schema is versioned;
- install/run documentation and sample deployment are validated;
- benchmark report is retained as release evidence.

## Current boundary

Source installed != benchmark executed != tuned != packaged != released.

The existing parent handoff `failure_mailbox/FAILURE_MAILBOX_MIRROR_HANDOFF.md` still reports validation pending. An attempted parent-handoff update in this session was blocked by the write safety layer; this dedicated benchmark handoff therefore preserves the new work durably without claiming that parent state changed.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
