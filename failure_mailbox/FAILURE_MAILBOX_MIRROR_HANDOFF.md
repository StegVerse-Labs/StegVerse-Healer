# Healer Failure Mailbox Mirror Handoff

Updated: 2026-08-18
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: SOURCE_IMPLEMENTED_VALIDATION_PENDING

## Goal

`HEALER-GITHUB-FAILURE-MAILBOX-001`

Build a Healer-owned failure inventory and correlation engine using the deterministic replay-ledger architecture demonstrated by the ARA deployment mailbox monitor, with semantics changed from deployment verification candidates to GitHub failure incidents.

## Governing boundaries

- StegVerse is primary.
- Third-party runtime is fallback-only.
- TV/TVC is sole credential/secret/token authority.
- NON-TV/TVC secrets/tokens are prohibited.
- GitHub Actions is validation-only and has no production/runtime/control-plane authority.
- Do not create a second heartbeat or ordinary scheduler; use the existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` execution surface when transport is admitted.
- Email receipt is an observation only; it grants no repair, repository, deployment, release, credential, wallet, or runtime authority.
- Heartbeat progression remains oscillator-only and is unaffected by email arrival, incident state, repair state, or lack of state transition.

## Implemented source surfaces

```text
failure_mailbox/README.md
failure_mailbox/incident_engine.py
failure_mailbox/failure-observation.schema.json
tests/test_failure_mailbox_incident_engine.py
```

Source commits:

```text
README / architecture: 4cd900f96225fad2b0a114a4ae875b9cb64a6eb0
incident engine: dfc267d026a970b1ec69e424a54a960754232bd8
deterministic tests: b252b55db202ba3a665cbf6a46584efdb447c153
observation schema: 056808c03e9c3608cebed45431e5581407744222
```

## Implemented semantics

- deterministic incident inventory IDs: `GF-000001`, `GF-000002`, ...;
- email/message identity deduplication (`duplicate_noop`);
- repeated notifications of the same failure signature accumulate into one incident history across commits;
- normalized failure-family classification including module/import, route-unreachable, fail-closed, no-jobs-run, dependency, schema, continuity, authority-boundary and timeout classes;
- per-incident first/last seen, occurrence count, message IDs, commits, run IDs and observations;
- lifecycle states: `OPEN`, `TRIAGED`, `REPAIRING`, `RETESTING`, `SANDBOX_REQUIRED`, `RESOLVED`, `UNRESOLVED`;
- worker returns `UNABLE_TO_REPAIR` or `IMPOSSIBLE_TO_REPAIR` are normalized directly to `SANDBOX_REQUIRED` rather than ordinary retry;
- `RESOLVED` requires durable evidence before associated notification message IDs become archive-eligible;
- cross-repository temporal neighbor candidates are calculated without claiming causality;
- summary reports failure-family incident frequency, observation frequency, repository frequency, repeated incidents, unresolved/sandbox-required incidents and resolution-qualified archive candidates;
- authority effect and heartbeat effect are explicitly false.

## ARA engine relationship

The engine reuses the architectural pattern, not the deployment semantics:

```text
ARA:
mail -> deterministic notification identity -> replay ledger -> verification candidate / duplicate_noop

Healer:
mail -> normalized failure observation -> deterministic failure identity -> incident ledger -> lifecycle / frequency / neighbor analysis / archive plan
```

The ARA Graph/mailbox poller is not copied into Healer because its Microsoft Graph credential path predates the current TV/TVC_ONLY boundary. Healer's incident engine is transport-neutral. A future mailbox adapter must obtain mailbox access only through an admitted TV/TVC path and feed normalized observations into this engine.

## Validation status

Focused deterministic tests are committed but no exact-head validation result has yet been observed for current main. Source presence is not validation, runtime activation, or mailbox processing.

Required validation:

1. repeated messages with the same failure signature update one incident;
2. identical message ID produces `duplicate_noop`;
3. unable/impossible-to-repair transitions to `SANDBOX_REQUIRED`;
4. resolution without evidence fails closed;
5. resolution with evidence produces archive-eligible message IDs;
6. cross-repository temporal candidates are recorded without authority/causality claims;
7. ledger persistence round-trip is deterministic;
8. no GitHub token or NON-TV/TVC credential is required.

## Remaining work

1. run/observe exact-head focused tests and repository validation;
2. define and implement a TV/TVC-authorized Gmail/GitHub-notification transport adapter that converts unread GitHub failure notifications into `failure-observation.schema.json` without giving email action authority;
3. bind the adapter/engine to the existing sovereign Healer scheduler, not GitHub Actions;
4. backfill the existing unread GitHub failure corpus into the incident ledger while preserving source message IDs and timestamps;
5. correlate incident history with known repository dependency edges to improve neighbor/propagation candidate scoring without asserting causality from time alone;
6. connect repair task state so `REPAIRING`/`RETESTING`/`SANDBOX_REQUIRED` reflect canonical worker registry outcomes;
7. perform mailbox archive only for notifications whose incident is durably `RESOLVED`, retaining the incident ledger and resolution evidence;
8. produce pre/post metrics for distinct incidents, notification amplification, recurrence after claimed resolution, mean time to resolution, and cross-repo propagation candidates.

## Completion gate

This goal is not complete until source is validated, transport is admitted under TV/TVC, the current unread failure corpus is inventoried, live incremental ingestion is operating on the sovereign Healer scheduler, worker/sandbox lifecycle is connected, and resolution-qualified mailbox cleanup is evidenced.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
