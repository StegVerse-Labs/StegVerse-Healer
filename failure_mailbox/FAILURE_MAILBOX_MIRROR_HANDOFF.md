# Healer Failure Mailbox Mirror Handoff

Updated: 2026-08-19T10:51:00-05:00
Repository: `StegVerse-Labs/StegVerse-Healer`
Branch: `main`
State: `TVC_SECRET_BOUNDARY_INSTALLED_FIRST_LIVE_RUN_PENDING`

## Goal

`HEALER-GITHUB-FAILURE-MAILBOX-001`

Operate an automated Healer failure inventory/diagnostic intake while keeping all mailbox secret/key processing inside TV/TVC.

## Credential ownership rule

GitHub may physically store the Microsoft Graph configuration for now, but storage location is not credential authority.

```text
credential authority: TV/TVC ONLY
credential processor: StegVerse-Labs/TVC
consumer credential access: NONE
Healer direct secrets.* mailbox references: NONE
Healer Graph OAuth/client-secret processor: REMOVED
```

TV policy:

```text
StegVerse-Labs/TV:policies/external_secret_processing_authority_policy.json
policy_id: tv.external-secret-processing-authority.v1
```

TVC execution handoff:

```text
StegVerse-Labs/TVC:docs/MAILBOX_FAILURE_OBSERVATION_MIRROR_HANDOFF.md
```

## Automated intake

Healer schedule:

```text
.github/workflows/failure-mailbox-monitor.yml
cron: */15 * * * *
```

The first job calls the pinned TVC reusable workflow:

```text
StegVerse-Labs/TVC/.github/workflows/mailbox-failure-observation-reusable.yml
ref: 4fd185494edf4e47edbf913cd227851e11ff2418
```

The TVC job owns Microsoft Graph credential processing and emits artifact:

```text
tvc-mailbox-failure-observation/
  batch.jsonl
  manifest.json
```

Healer downloads only those sanitized outputs and refuses them unless the manifest proves:

```text
credential_authority=TV/TVC
credential_processed_by=StegVerse-Labs/TVC
credential_value_exposed=false
credential_value_persisted=false
consumer_credential_exported=false
mailbox_mutated=false
provider_message_ids_exported=false
partial_materialization=false
```

## Consumer processing

After TVC materialization, Healer runs the existing credential-neutral stack:

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

The former local Graph credential processor `failure_mailbox/poll_graph_failure_mailbox.py` was removed after the TVC boundary was installed.

## Durable state

Healer retains diagnostic state through provider-managed Actions cache/artifact transport; no Healer script receives a GitHub or mailbox credential value for diagnostic processing.

Retained state includes:

```text
status/failure-mailbox/incident-ledger.json
status/failure-mailbox/shadow-state.json
status/failure-mailbox/latest-report.json
status/failure-mailbox/current-batch.jsonl
status/failure-mailbox/current-manifest.json
```

## Benchmark evidence

Current non-duplicated measured benchmark denominator:

```text
July bounded window: 137 distinct GitHub failure emails
August bounded window: 24 distinct GitHub failure emails
combined: 161 distinct emails
```

Validated core evidence includes deterministic benchmark v0.4 PASS and 66/66 shadow-core tests PASS on the validated tranche.

## Authority boundary

```text
mailbox intake grants repair authority: false
repository mutation authority: false
deployment/release authority: false
wallet/trade authority: false
heartbeat authority/effect: false
mailbox mutation: false
```

## Current execution state

```text
15-minute Healer schedule: INSTALLED
TVC reusable Graph processor: INSTALLED
Healer direct mailbox secret processing: REMOVED
TVC environment required: tvc-mailbox-observation
TVC environment Graph secret provisioning observed: false
first successful TVC Graph observation: false
first TVC-sanitized Healer batch consumed: false
first automated diagnostic report: false
continuous automation activation: PENDING_FIRST_SUCCESSFUL_RUN
```

## Remaining work

1. Make the existing Graph configuration available to the TVC GitHub environment `tvc-mailbox-observation` without exposing values to Healer.
2. Observe the first successful TVC-owned Graph materialization.
3. Consume the first TVC artifact through Healer and verify complete coverage/parser state.
4. Continue automated/backfill processing beyond the 161-message measured corpus.
5. Route canonical observation/vector data to the appropriate analysis subsystem rather than making Healer own matrix/topology analysis.
6. Connect returned diagnostic/topology observations to Healer repair/retest/sandbox lifecycle.
7. Perform mailbox cleanup only after durable `RESOLVED` evidence.

## ARA relationship

ARA remains the proven behavioral mailbox baseline, but its current direct `secrets.*` mail functions are now legacy credential surfaces under the new TV/TVC rule. They should remain operational until equivalent TVC-owned execution is proven, then be migrated without losing continuity.

Current status: `DO NOT ARCHIVE — TVC SECRET-SCOPE PROVISIONING AND FIRST LIVE AUTOMATED DIAGNOSTIC RUN REMAIN.`
