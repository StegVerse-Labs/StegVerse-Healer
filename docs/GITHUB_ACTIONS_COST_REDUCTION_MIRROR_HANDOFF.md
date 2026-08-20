# GitHub Actions Cost Reduction Mirror Handoff

Updated: 2026-08-20T09:31:00-05:00

## Goal

Reduce StegVerse GitHub-hosted workflow spend without reducing validation capability or moving runtime, credential, publication, custody, wallet, or execution authority into GitHub Actions.

```text
goal_id: HEALER-GITHUB-ACTIONS-COST-REDUCTION-001
repository: StegVerse-Labs/StegVerse-Healer
branch: main
pull_request: 32
merge_commit: 49f0debee90ac3addffa262c1e495c9e803367cb
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_actions_production_role: NONE
scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
state: SOURCE_VALIDATED_MERGED_SOVEREIGN_CENSUS_PENDING
```

This work reuses the existing sovereign Healer scheduler and Quiet Enforcer. It creates no second scheduler or heartbeat.

## Existing evidence and integration boundary

Site already has an active cost-containment program under `StegVerse-Labs/Site#268` and `docs/ACTIONS_COST_CONTAINMENT_MIRROR_HANDOFF.md`. That program reduced the Site workflow census from 131 audit-start surfaces to 98 current-main surfaces and has already retired standalone hourly GitHub-hosted loops by moving recurring observation to the existing Healer scheduler.

TV has also removed a local daily schedule in favor of the existing Healer scheduler. This Healer goal does not duplicate those migrations. It supplies the cross-repository deterministic cost-analysis layer used to choose the next highest-value migration.

## Installed surfaces

```text
docs/GITHUB_ACTIONS_COST_REDUCTION_MIRROR_HANDOFF.md
data/actions_cost_policy.json
app/actions_cost_reducer.py
app/audit_schedules.py integration
tests/test_actions_cost_reducer.py
tests/test_quiet_enforcer_cost_integration.py
```

## Released source evidence

```text
PR: #32
validated head: c9152bb0efa5f08f0e73defa21155476446ea7de
Test Readiness run: 32380280789
repo-smoke job: 96461518129
result: SUCCESS
merge commit: 49f0debee90ac3addffa262c1e495c9e803367cb
```

The first Test Readiness run exposed an actual validation defect in this tranche: the newly added tests were written in pytest-function style while the repository's deterministic validation lane uses `python3 -m unittest discover`. They were therefore installed but not executed. That defect was repaired before merge by converting the new test suites to unittest-discoverable classes.

The successful exact-head validation then executed the new tests directly. The log records 82 deterministic tests PASS, including all seven `ActionsCostReducerTests` and both `QuietEnforcerCostIntegrationTests`. Credential refusal, anonymous exact-source fetch, repository readiness, the failure-mailbox benchmark, and validation-only authority checks also passed.

## Installed behavior

The analyzer works from locally materialized repository roots and requires no GitHub credential, network call, provider secret, or hosted Actions execution. It inventories `.github/workflows/*.yml` and `*.yaml`, estimates common cron start pressure, counts jobs and literal matrix fanout, detects broad push/PR triggers, missing concurrency cancellation, artifact custody, manual-only diagnostics, and ranks remediation candidates.

Policy is explicit and machine-readable at `data/actions_cost_policy.json`. The analyzer is advisory by default and may fail closed under `--enforce` only at the configured high scheduled-start threshold. It never mutates another repository automatically.

The existing `app/audit_schedules.py` Quiet Enforcer now embeds a compact cost-analysis projection in `stegverse.healer.quiet-enforcer-receipt.v3`. This means the already-established `quiet_enforcer.yml` sovereign scheduler target becomes the execution carrier for ranked cost-pressure analysis; no new scheduled GitHub workflow and no new Healer target are required.

The Quiet Enforcer retains its stronger invariant: repository-local `schedule:` triggers in managed repositories remain violations. The added cost analysis additionally ranks non-scheduled cost pressure such as unfiltered push/PR triggers, missing cancellation, matrices, and artifact custody.

## Cost-control principles

```text
capability_preservation_required: true
cost_reduction_without_capability_loss: preferred
cost_reduction_with_capability_gain: strongest preference
hosted_schedule_for_non_authoritative_observation: migration_candidate
manual_only_diagnostic: low recurring cost
push_or_pr_without_path_filter: review_candidate
missing_concurrency_cancel: review_candidate
literal_matrix_fanout: cost_multiplier
artifact_custody_for_ephemeral_validation: review_candidate
github_token_or_secret_workaround: prohibited
render_workaround: prohibited
automatic_cross_repo_mutation: prohibited
```

## Activation boundary

Source implementation, exact-head deterministic validation, and merge are complete. They do not prove ecosystem savings.

Goal activation requires the existing sovereign Quiet Enforcer to execute against current locally materialized StegVerse repositories, persist a ranked v3 cost-analysis receipt, and then at least one evidence-preserving migration must reduce expected GitHub-hosted runner starts without reducing capability.

## Exact next actions

1. Existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` executes the already-bound `quiet_enforcer.yml` target against current locally materialized StegVerse repository roots.
2. Persist/inspect the resulting `stegverse.healer.quiet-enforcer-receipt.v3` ranked census.
3. Select the highest-ranked candidate that is not actively claimed by another workstream.
4. Read that repository's applicable `*_MIRROR_HANDOFF.md` before mutation.
5. Migrate the candidate to an existing canonical validation surface or the existing Healer scheduler while preserving semantics.
6. Record before/after runner-start pressure and capability evidence.
7. Continue iteratively until recurring hosted validation is exceptional rather than default.

No billing-limit increase, GitHub token installation, Render deployment, automatic purchase, or authority expansion is authorized by this handoff.
