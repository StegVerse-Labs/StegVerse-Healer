# Healer Failure Mailbox Mirror Handoff

Updated: 2026-08-19
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: `ARA_GRAPH_AUTOMATION_INSTALLED_FIRST_LIVE_RUN_PENDING`

## Goal

`HEALER-GITHUB-FAILURE-MAILBOX-001`

Operate a Healer-owned automated failure inventory and diagnostic engine using the deterministic replay-ledger architecture demonstrated by the ARA deployment mailbox monitor, with semantics changed from deployment verification candidates to GitHub failure incidents, recurrence, episodes, coverage, dependency candidates, repair/sandbox lifecycle and evidence-qualified cleanup.

## Scoped transport authorization — 2026-08-19

The user explicitly authorized StegVerse-Healer to reuse the same proven mailbox mechanism used by `StegVerse-Labs/ara-admissibility-interop` for automated mailbox checking.

This is a scoped exception to the later TV/TVC-only transport migration requirement for this Healer intake path. It does **not** broaden Healer diagnostic, repair, repository, release, wallet, heartbeat or deployment authority.

Authorized legacy intake mechanism:

```text
GitHub Actions schedule
-> Microsoft Graph client-credentials application
-> STEGVERSE_MAIL_TENANT_ID
-> STEGVERSE_MAIL_CLIENT_ID
-> STEGVERSE_MAIL_CLIENT_SECRET
-> STEGVERSE_MONITOR_MAILBOX
-> bounded GitHub-failure observation batch
-> Healer shadow/incident engine
-> durable Actions artifact state
```

The workflow may also use `${{ github.token }}` only for the same isolated-runner artifact-state restoration role used by ARA. This exception does not make GitHub Actions or its token production/runtime/control-plane authority.

## Automated intake implementation

Installed on `main`:

```text
failure_mailbox/poll_graph_failure_mailbox.py
.github/workflows/failure-mailbox-monitor.yml
```

Source commits:

```text
Graph poller: a895efc808fa813a7d7e79c5036470ffb9ce50ff
scheduled workflow: 9c42cc3669b0307184adae3bf689519739533a85
```

Schedule:

```text
*/15 * * * *
```

Each run uses a 20-minute observation window with a 2-minute lag so adjacent runs overlap. Deterministic message identity and shadow batch state absorb overlap/replay without turning repeated observation into new incidents.

The Graph poller:

- reads the configured monitor mailbox through Microsoft Graph;
- accepts mail from `notifications@github.com` whose GitHub notification subject is `Run failed` or `PR run failed`;
- pages backward until the bounded observation interval is exhausted;
- emits a sanitized JSONL batch;
- emits an independently counted non-secret manifest;
- hashes provider message/thread/internet-message identifiers before export;
- exports timestamp, Subject and Graph body preview only;
- exports no credential value;
- performs no mailbox mutation.

Unlike ARA deployment intake, the Healer poller deliberately does **not** mark messages read. It also does not archive, delete or relabel them. Cleanup remains governed by incident resolution evidence.

## Durable isolated-runner state

The recurring workflow restores and republishes the artifact:

```text
failure-mailbox-monitor-state
```

with 90-day retention. State includes, when present:

```text
status/failure-mailbox/incident-ledger.json
status/failure-mailbox/shadow-state.json
status/failure-mailbox/latest-report.json
status/failure-mailbox/current-batch.jsonl
status/failure-mailbox/current-manifest.json
```

Artifact continuity prevents loss/duplicate processing across isolated GitHub-hosted runners. It does not grant incident-resolution, repair, release or runtime authority.

## Diagnostic engine

Developed and validated source includes:

```text
failure_mailbox/incident_engine.py
failure_mailbox/github_notification_parser.py
failure_mailbox/episode_analysis.py
failure_mailbox/dependency_analysis.py
failure_mailbox/backfill.py
failure_mailbox/coverage_monitor.py
failure_mailbox/shadow.py
failure_mailbox/benchmark.py
```

Implemented semantics include:

- deterministic incident IDs `GF-000001`, `GF-000002`, ...;
- duplicate message `duplicate_noop`;
- recurring same-signature incident history;
- distinct notification outcome vs semantic failure family;
- failure episodes/amplification without destroying incident identity;
- source-to-intake self-coverage monitoring;
- dependency candidates and counterevidence without causality claims;
- lifecycle `OPEN`, `TRIAGED`, `REPAIRING`, `RETESTING`, `SANDBOX_REQUIRED`, `RESOLVED`, `UNRESOLVED`;
- `UNABLE_TO_REPAIR` / `IMPOSSIBLE_TO_REPAIR` -> `SANDBOX_REQUIRED`;
- durable resolution evidence required before archive eligibility;
- authority effect and heartbeat effect false.

## Benchmark evidence

Current deterministic benchmark: `stegverse.healer.failure-mailbox-benchmark/v0.4`.

Validated historical/diagnostic evidence includes:

```text
July bounded window: 137 distinct GitHub failure emails
August bounded window: 24 distinct GitHub failure emails
combined distinct measured benchmark emails: 161
```

The smaller 47/50-message, 21-message and related regression fixtures are subsets of those bounded windows and must not be added again to the reviewed-email denominator.

Current benchmark evidence also includes:

- deterministic v0.4 PASS;
- 66/66 shadow-core tests PASS on the validated tranche;
- July 137-message window partitioned into 96 `NO_JOBS_RUN` vs 41 unsuccessful-job notifications;
- August 24-message window across 9 repositories reconstructed into 15 incidents;
- coverage discontinuity detection where source activity continued but the legacy label intake was zero.

## Authority boundary

The authorized ARA-derived mailbox transport is **observation transport only**.

```text
mailbox intake grants repair authority: false
mailbox intake grants repository mutation authority: false
mailbox intake grants deployment/release authority: false
mailbox intake grants wallet/trade authority: false
mailbox intake grants heartbeat authority/effect: false
mailbox mutation by Healer monitor: false
```

The independent heartbeat oscillator remains unaffected by email arrival, polling cadence, incident state or lack of transitions.

The separately developed TV/TVC-native mailbox path may continue as a hardening/migration target, but it is no longer a prerequisite for running Healer diagnostics because this scoped ARA-derived transport has been explicitly authorized.

## Current execution state

```text
ARA-derived Graph poller source: INSTALLED
15-minute workflow source: INSTALLED
Healer shadow/incident engine: IMPLEMENTED_VALIDATED
historical benchmark: ACTIVE / 161 DISTINCT MEASURED EMAILS
mailbox mutation: DISABLED
first scheduled Healer monitor run observed: false
Healer repository access to required Graph secrets observed: false
first automated live batch observed: false
first automated diagnostic report observed: false
continuous automation activation: PENDING_FIRST_SUCCESSFUL_RUN
```

Do not infer live automation merely from workflow installation. Activation requires an actual `Healer Failure Mailbox Monitor` run that obtains the configured Graph settings, produces a bounded batch/manifest, executes the shadow engine and retains `failure-mailbox-monitor-state`.

## Remaining work

1. Observe the first scheduled or dispatched `Healer Failure Mailbox Monitor` run.
2. If the ARA Graph settings are not available to this repository, grant this Healer workflow access to the same existing organization/repository secret configuration rather than inventing new credentials.
3. Consume the first batch/report and verify source coverage, parser quality, incident/episode output and artifact-state continuity.
4. Continue historical backfill beyond the currently measured 161-email benchmark corpus.
5. Connect live incident lifecycle to canonical repair/retest/sandbox worker outcomes.
6. Archive/cleanup mail only after durable `RESOLVED` evidence; the intake monitor itself performs no mailbox cleanup.
7. Benchmark live recurrence, amplification, MTTR and cross-repository diagnostic value before package release.

## Completion gate

Automated diagnostic intake is active only after a real scheduled run succeeds and produces retained diagnostic state. Full Healer diagnostic/remediation maturity additionally requires live worker/sandbox lifecycle integration and evidence-qualified cleanup.

Current status: `DO NOT ARCHIVE — FIRST LIVE AUTOMATED MAILBOX DIAGNOSTIC RUN AND DOWNSTREAM LIFECYCLE REMAIN.`
