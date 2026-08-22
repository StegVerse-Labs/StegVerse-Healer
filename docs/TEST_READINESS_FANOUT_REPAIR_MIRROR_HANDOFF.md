# Test Readiness Fanout Repair Mirror Handoff

Updated: 2026-08-22

## Goal

Reduce redundant hosted validation in `StegVerse-Labs/StegVerse-Healer/.github/workflows/test-readiness.yml` without reducing automatic source/schema/config/test validation.

```text
goal_id: HEALER-TEST-READINESS-FANOUT-037
repository: StegVerse-Labs/StegVerse-Healer
branch: fix/test-readiness-fanout-37
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_actions_production_role: NONE
render_required: false
state: IMPLEMENTATION_IN_PROGRESS
```

## Proven current-main fanout

Before this repair, Test Readiness has unfiltered `push:` and `pull_request:` triggers and no concurrency cancellation. Every qualifying repository change launches the full credential-clean validation job: anonymous exact-source fetch, baseline JSON/repository smoke, the complete deterministic unittest suite, failure-mailbox benchmark, and authority-boundary validation.

This run itself demonstrated avoidable duplication: source-changing PR #36 required exact-head validation, while evidence-only handoff updates also started the same full 87-test + benchmark lane despite not changing executable/config/schema/test surfaces.

## Safe repair boundary

- Keep automatic `push` and `pull_request` validation for all repository content except documentation-only `docs/**` and root `README.md` changes.
- Keep `workflow_dispatch` for intentional full validation.
- Add per-PR/ref concurrency with `cancel-in-progress: true` so superseded runs on the same change stream do not consume full hosted runner time.
- Preserve `permissions: {}`, credential refusal, anonymous exact-source fetch, full deterministic tests, benchmark, and validation-only authority boundary.
- Do not move runtime/control-plane authority into Actions.

Documentation-only commits can still be intentionally checked through `workflow_dispatch`; code, actions, data/config, failure-mailbox, handoff JSON, registry, schema, scripts, templates, tests, and root source files continue to trigger automatically.

## Completion gate

Requires real workflow mutation, exact changed-head validation, merge to main, and evidence that source/schema/config/test automatic coverage and manual dispatch remain present. A workflow pass is validation evidence only, not runtime activation.
