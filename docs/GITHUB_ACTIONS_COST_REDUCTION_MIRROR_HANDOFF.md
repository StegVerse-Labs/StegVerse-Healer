# GitHub Actions Cost Reduction Mirror Handoff

Updated: 2026-08-20T07:44:00-05:00

## Goal

Reduce StegVerse GitHub-hosted workflow spend without reducing validation capability or moving runtime, credential, publication, custody, wallet, or execution authority into GitHub Actions.

```text
goal_id: HEALER-GITHUB-ACTIONS-COST-REDUCTION-001
repository: StegVerse-Labs/StegVerse-Healer
branch: feat/actions-cost-reduction-enforcer-20260820
pull_request: 32
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_actions_production_role: NONE
scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
state: SOURCE_IMPLEMENTED_QUIET_ENFORCER_INTEGRATED_VALIDATION_PENDING
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

Source commits on the branch:

```text
handoff creation: 9edcfb91041bb95feb56ff6c09bde16f9f465dc1
policy: b458fd2fa01a35bcf40fd220b276308345f82720
analyzer: 32646bff235872c0791f864666310c2cb6999bf6
analyzer tests: 5fd8250b811f0d513a5755bf2ed5daa3696b136d
Quiet Enforcer integration: 9fadbc0b49996281807a8438eef78a8491c27d5f
integration tests: 10e6a1306217e828e4880fd910708dc814b8a4c5
```

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

## Deterministic test coverage installed

`tests/test_actions_cost_reducer.py` covers:

- hourly, six-hourly, daily, and weekday cron estimation;
- hourly migration ranking;
- path-filtered push/PR with concurrency cancellation;
- matrix fanout and artifact-custody detection;
- manual-only low-recurring-cost classification;
- report ranking and enforcement threshold behavior;
- fail-closed missing-root behavior.

`tests/test_quiet_enforcer_cost_integration.py` covers:

- Quiet Enforcer v3 embedding of ranked cost analysis while preserving a COMPLETE schedule-audit result;
- detection/ranking of a broad unfiltered push surface;
- preservation of the existing fail-closed repository-local schedule invariant;
- expected 744 monthly starts for an hourly single-job schedule.

These tests are installed but no hosted workflow result is treated as source or runtime proof while GitHub-hosted execution is admission/billing constrained.

## Activation boundary

Source implementation and test installation do not prove ecosystem savings. Goal activation requires the existing sovereign Quiet Enforcer to execute against current locally materialized StegVerse repositories, persist a ranked cost-analysis receipt, and then at least one evidence-preserving migration must reduce expected GitHub-hosted runner starts without reducing capability.

## Exact next actions

1. Validate PR #32 through the strongest credential-clean available source path.
2. Merge only after source validation is satisfied and the branch remains current.
3. Allow the existing `quiet_enforcer.yml` Healer target to produce the first v3 receipt on the sovereign scheduler.
4. Select the highest-ranked candidate that is not actively claimed by another workstream.
5. Migrate that candidate to an existing canonical validation surface or the existing Healer scheduler while preserving semantics.
6. Record before/after runner-start pressure and continue iteratively until recurring hosted validation is exceptional rather than default.

No billing-limit increase, GitHub token installation, Render deployment, automatic purchase, or authority expansion is authorized by this handoff.
