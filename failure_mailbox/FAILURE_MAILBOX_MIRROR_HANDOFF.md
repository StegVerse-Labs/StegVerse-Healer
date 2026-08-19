# Healer Failure Mailbox Mirror Handoff

Updated: 2026-08-19T18:22:00-05:00  
Repository: `StegVerse-Labs/StegVerse-Healer`  
Branch: `main`  
State: `ACTIVE — CREDENTIAL-NEUTRAL TVC CLIENT IMPLEMENTED; SOVEREIGN SCHEDULER AND LIVE PROVIDER PROOF PENDING`

## Goal

`HEALER-GITHUB-FAILURE-MAILBOX-001`

Maintain an automated operational-failure inventory while keeping mailbox secret/key processing inside TV/TVC. Failure includes repository workflow failures and organization/account-level GitHub Actions capacity conditions capable of preventing jobs from reaching step 1.

## Supported observations

```text
repository Run failed / PR run failed -> existing repository workflow observation
90% included minutes -> ACTIONS_INCLUDED_MINUTES_WARNING
100% included minutes -> ACTIONS_INCLUDED_MINUTES_EXHAUSTED
75% budget -> ACTIONS_BUDGET_APPROACHING
90% budget -> ACTIONS_BUDGET_HIGH
100% budget -> ACTIONS_BUDGET_EXHAUSTED
```

Capacity events normalize to `github-account:<account>` and `GitHub Actions included minutes` or `GitHub Actions budget`. At 100%, `notification_result_class=OPERATIONAL_CAPACITY_EXHAUSTED`; these are OPEN operational failure incidents. 75% and 90% remain warning/high-risk observations.

## Credential-neutral TVC intake

Implemented:

- `failure_mailbox/sovereign_tvc_intake.py`
- `tests/test_sovereign_tvc_mailbox_intake.py`

The client calls only:

`http://127.0.0.1:8766/v1/mailbox-failure-observation`

It sends:

```text
schema
capability_id
policy_id
caller_repository = StegVerse-Labs/StegVerse-Healer
consumer_task = HEALER-GITHUB-FAILURE-MAILBOX-001
window_start
window_end
maximum_messages
```

It sends no authorization header, mailbox credential, token, secret reference or provider identifier. Non-loopback endpoints are rejected.

The client requires the TVC response to prove:

```text
mailbox_mutated=false
credential_authority=TV/TVC
credential_value_exposed=false
credential_value_persisted=false
consumer_credential_exported=false
provider_message_ids_exported=false
partial_materialization=false
authority_effect=false
secret_material_returned=false
secret_material_logged=false
secret_material_retained=false
```

Unexpected protected response keys fail closed.

Sanitized runtime state is stored under `$XDG_STATE_HOME/stegverse/healer/failure-mailbox` by default, not committed into repository source. A returned 100% budget fixture is deterministically admitted into the existing incident engine as an OPEN `ACTIONS_BUDGET_EXHAUSTED` incident for `github-account:StegVerse-Labs`.

## Credential ownership

```text
credential authority: TV/TVC ONLY
credential processor: StegVerse-Labs/TVC sovereign mailbox runtime
consumer credential access: NONE
Healer direct mailbox secret processing: NONE
GitHub Actions runtime authority: NONE
```

TV policy: `StegVerse-Labs/TV:policies/mailbox_failure_observation_capability_policy.json`  
TVC execution handoff: `StegVerse-Labs/TVC:docs/MAILBOX_FAILURE_OBSERVATION_MIRROR_HANDOFF.md`

## Corrected carrier state

The earlier claimed 15-minute GitHub-hosted carrier does not exist on current ARA main and is not to be recreated. The TVC reusable hosted mailbox secret path and manual live probe are now explicitly retired. The canonical ordinary scheduler remains:

`SHWP-HEALER-SOVEREIGN-SCHEDULER-001`

Do not create another timer or hosted poller.

## Current execution state

```text
Healer workflow-failure parser: IMPLEMENTED
Healer Actions-capacity parser: IMPLEMENTED
Healer account-level incident compatibility: IMPLEMENTED
Healer credential-neutral TVC client: IMPLEMENTED
TVC sovereign mailbox runtime source: IMPLEMENTED
TV mailbox policy: IMPLEMENTED
TVC runtime service active: NOT OBSERVED
TVC vault mailbox package resolvable: NOT OBSERVED
sovereign scheduler target binding: PENDING
first real Graph materialization: NOT OBSERVED
continuous mailbox activation: NOT PROVEN
```

## Exact next execution order

1. On the sovereign TVC host, materialize the TV/TVC-owned mailbox package under `vault://tvc/mailbox/github-operational-observation/microsoft-graph-package` without exposing its value.
2. Install/activate `stegtvc-mailbox-observation.service` and verify loopback health.
3. Add `failure_mailbox/sovereign_tvc_intake.py` as a target of the **existing** `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; do not add a second scheduler.
4. Observe the first real bounded Graph materialization and consume it into the incident ledger.
5. Verify real 100% Actions budget/included-minute mail becomes an OPEN `github-account:<account>` failure incident.
6. Backfill the bounded historical GitHub operational-alert corpus.
7. Connect diagnostic/topology results to repair/retest/sandbox lifecycle and only archive source mail after durable resolution evidence.

## Authority boundary

Mailbox observation grants no repair, repository mutation, deployment/release, wallet/trade, heartbeat, publication or general runtime authority. TV/TVC remains credential authority.

Current status: `DO NOT ARCHIVE — TVC HOST ACTIVATION, VAULT PACKAGE, SOVEREIGN SCHEDULER BINDING, AND FIRST LIVE MATERIALIZATION REMAIN.`
