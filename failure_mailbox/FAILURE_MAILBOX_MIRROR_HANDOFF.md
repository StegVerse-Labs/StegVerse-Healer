# Healer Failure Mailbox Mirror Handoff

Updated: 2026-08-19T18:10:00-05:00  
Repository: `StegVerse-Labs/StegVerse-Healer`  
Branch: `main`  
State: `SOURCE_CLASSIFIER_EXPANDED_ACTIONS_CAPACITY_TRANSPORT_PENDING`

## Goal

`HEALER-GITHUB-FAILURE-MAILBOX-001`

Maintain an automated failure inventory/diagnostic intake while keeping mailbox secret/key processing inside TV/TVC. Failure now includes not only repository workflow-failure notifications but also organization/account-level GitHub Actions capacity conditions that can prevent jobs from reaching step 1.

## Supported observations

```text
repository Run failed / PR run failed -> existing repository workflow observation
90% included minutes -> ACTIONS_INCLUDED_MINUTES_WARNING
100% included minutes -> ACTIONS_INCLUDED_MINUTES_EXHAUSTED
75% budget -> ACTIONS_BUDGET_APPROACHING
90% budget -> ACTIONS_BUDGET_HIGH
100% budget -> ACTIONS_BUDGET_EXHAUSTED
```

Capacity events normalize to repository identity `github-account:<account>` and workflow identity `GitHub Actions included minutes` or `GitHub Actions budget`. They therefore enter the existing incident ledger without pretending to be a repository workflow run.

At 100%, `notification_result_class=OPERATIONAL_CAPACITY_EXHAUSTED`; these are operational failure incidents. 75% and 90% remain warning/high-risk observations so the system can act before admission stops.

The parser fails closed if a TVC-supplied capacity `signal_class` disagrees with the class derived from the subject.

## Credential ownership

```text
credential authority: TV/TVC ONLY
credential processor: StegVerse-Labs/TVC
consumer credential access: NONE
Healer direct mailbox secret processing: NONE
```

TV policy: `StegVerse-Labs/TV:policies/mailbox_failure_observation_capability_policy.json`  
TVC execution handoff: `StegVerse-Labs/TVC:docs/MAILBOX_FAILURE_OBSERVATION_MIRROR_HANDOFF.md`

## Corrected carrier state

The previous handoff claimed a 15-minute `.github/workflows/failure-mailbox-monitor.yml` existed. It does not exist on current `main`. The canonical Healer task and handoff require:

```text
github_actions_runtime_authority: NONE
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
```

Do **not** recreate the private GitHub-hosted 15-minute poller. The next integration is a TVC-owned secret-processing boundary invoked through the existing sovereign scheduler without making Healer a mailbox credential processor.

## Current execution state

```text
Healer parser: SOURCE IMPLEMENTED
workflow-failure parsing: IMPLEMENTED
Actions capacity parsing: IMPLEMENTED
incident engine account-level compatibility: IMPLEMENTED via github-account:<account>
TVC classifier: SOURCE IMPLEMENTED
TV policy: SOURCE IMPLEMENTED
first live TVC Graph materialization: NOT YET PROVEN
sovereign TVC transport binding: PENDING
continuous automation activation: PENDING
```

## Remaining work

1. Bind TVC-owned mailbox processing to `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` without passing protected values through Healer source/process arguments/durable state.
2. Observe the first successful TVC Graph materialization.
3. Consume the first sanitized batch and verify workflow + capacity incident creation.
4. Backfill the bounded historical GitHub operational-alert corpus.
5. Connect returned diagnostic/topology observations to Healer repair/retest/sandbox lifecycle.
6. Perform mailbox cleanup only after durable `RESOLVED` evidence.

## Authority boundary

Mailbox observation grants no repair, repository mutation, deployment/release, wallet/trade, heartbeat, publication or runtime authority. TV/TVC remains credential authority.

Current status: `DO NOT ARCHIVE — LIVE TVC TRANSPORT BINDING AND FIRST AUTOMATED DIAGNOSTIC RUN REMAIN.`
