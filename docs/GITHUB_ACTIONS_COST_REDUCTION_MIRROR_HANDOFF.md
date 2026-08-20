# GitHub Actions Cost Reduction Mirror Handoff

Updated: 2026-08-20T07:35:00-05:00

## Goal

Reduce StegVerse GitHub-hosted workflow spend without reducing validation capability or moving runtime, credential, publication, custody, wallet, or execution authority into GitHub Actions.

```text
goal_id: HEALER-GITHUB-ACTIONS-COST-REDUCTION-001
repository: StegVerse-Labs/StegVerse-Healer
branch: feat/actions-cost-reduction-enforcer-20260820
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_actions_production_role: NONE
scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
state: SOURCE_IMPLEMENTATION_IN_PROGRESS
```

This work reuses the existing sovereign Healer scheduler. It must not create a second scheduler or heartbeat.

## Existing evidence and integration boundary

Site already has an active cost-containment program under `StegVerse-Labs/Site#268` and `docs/ACTIONS_COST_CONTAINMENT_MIRROR_HANDOFF.md`. That program reduced the Site workflow census from 131 audit-start surfaces to 98 current-main surfaces and has already retired standalone hourly GitHub-hosted loops by moving recurring observation to the existing Healer scheduler.

TV has also removed a local daily schedule in favor of the existing Healer scheduler. This Healer goal does not duplicate those migrations. It supplies the missing cross-repository deterministic cost-analysis layer used to choose the next highest-value migration.

## Installed surfaces

```text
app/actions_cost_reducer.py
data/actions_cost_policy.json
tests/test_actions_cost_reducer.py
docs/GITHUB_ACTIONS_COST_REDUCTION_MIRROR_HANDOFF.md
```

## Required behavior

The analyzer must work without GitHub credentials, network access, provider secrets, or hosted Actions. Given one or more locally materialized repository roots, it must:

1. inventory `.github/workflows/*.yml` and `*.yaml`;
2. identify scheduled workflows and estimate minimum scheduled starts per day/month for common cron forms;
3. count literal job and matrix fanout surfaces;
4. identify missing `concurrency`/`cancel-in-progress` protection;
5. identify unfiltered `push`/`pull_request` triggers;
6. identify artifact upload/download custody surfaces;
7. distinguish manual-only workflows from recurring/push/PR workflows;
8. rank remediation candidates by avoidable hosted-run pressure;
9. recommend reuse of the sovereign Healer scheduler for recurring validation/observation that has no GitHub-hosted authority requirement;
10. emit deterministic JSON suitable for replay and later repository-specific migration receipts.

The analyzer is advisory by default. `--enforce` may fail only on explicit policy violations. It must never delete workflows or mutate another repository automatically.

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
```

## Activation boundary

Source implementation and deterministic tests do not prove ecosystem savings. Goal activation requires at least one analyzer-produced ranked report over current locally materialized StegVerse repositories, followed by one evidence-preserving migration that reduces expected GitHub-hosted runner starts without reducing capability.

## Next actions

1. Install analyzer, policy, and deterministic tests on this branch.
2. Validate locally or through a credential-clean source-validation carrier when available.
3. Run against locally materialized StegVerse repository roots through the existing sovereign scheduler/runtime environment.
4. Persist the ranked remediation report.
5. Select the highest-value non-colliding candidate and migrate it to an existing canonical validation surface or the existing Healer scheduler.
6. Measure before/after runner-start pressure and preserve capability evidence.

No billing-limit increase, GitHub token installation, Render deployment, or authority expansion is authorized by this handoff.
