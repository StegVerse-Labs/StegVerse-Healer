# StegVerse-Healer Mirror Handoff

## Canonical state

```text
repository: StegVerse-Labs/StegVerse-Healer
branch: main
primary_goal: HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_token_production_authority: NONE
github_actions_production_role: NONE
heartbeat_owner: StegVerse-Labs/.github G18
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
wallet_signing_and_broadcast: USER_ONLY
state: SOURCE_CONTROL_RELEASED_LIVE_SCHEDULER_ACTIVATION_MACHINE_OWNED
```

Canonical organization/runtime continuations are `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`, and `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`.

## Workflow hygiene responsibility — StegVerse-Labs/.github

StegVerse-Healer is the canonical owner for repository hygiene and workflow-surface minimization affecting `StegVerse-Labs/.github`.

Accepted evaluation source:

```text
document: docs/GITHUB_ROOT_WORKFLOW_HYGIENE_EVALUATION_REQUEST.md
admission PR: #33
exact validated head: b150868c9d6083a6c032fb0d8a2f747f7e142283
Test Readiness: 32577928955 SUCCESS
merge commit: 9090dde4b38795226f3179e03dcbf1ad8592dc64
execution issue: #34
```

Imported fanout evidence currently describes 18 `.github` workflow files: 12 automatic-push and 6 PR/manual-only after recent containment repairs. The proposed 18→2 structure is an evaluation hypothesis, not an already-authorized deletion set.

Healer #34 owns the next execution tranche:

- independently classify every current `.github` workflow;
- target the established 0/1/2 stable-entry-surface policy where technically sufficient;
- preserve source/schema/config/test validation parity and meaningful PR coverage;
- preserve manual dispatch for intentionally expensive checks;
- transfer recurring/operational behavior to existing StegVerse-owned scheduler/workers where appropriate;
- reconcile active owners before absorbing owner-sensitive surfaces;
- preserve TV/TVC-only credential authority, no NON-TV/TVC secrets/tokens, no GitHub-token production/runtime authority, and no Render;
- record exact-current-main validation, final workflow count, exceptions, migrations, and blockers before claiming completion.

Issue creation, assignment, evaluation admission, or workflow success does not satisfy this hygiene goal. Actual accepted consolidation/transfer/elimination and parity evidence remain required.

## Released source integrations

- `HEALER-G18-PRE-CARRIER-ASSIST-001`: PR #5 merge `571b6a86737173a89235110294025f9808695531`.
- `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`: PR #7 merge `ecf96188348c097dfdea3ce55c47db9dff6e84ef`.
- `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`: source/integration COMPLETE_RELEASED; issue #8 closed.
- `HEALER-RSTD-ST018-LOCAL-TASK-MANAGER-001`: source/integration COMPLETE_RELEASED; issue #11.
- `HEALER-SITE-CHILD-SAFETY-PUBLIC-OBSERVER-001`: source/integration COMPLETE_RELEASED; issue #13 pending closeout record only.

## Child-safety sovereign public-route observer

Purpose: replace Site's hourly GitHub-hosted child-safety deployment observer with a fixed handler on the existing sovereign Healer scheduler while preserving public HTTPS/status/content verification.

Installed surfaces:

```text
data/orchestrator_targets.json::StegVerse-Labs/Site/child-safety-public-deployment-observer
app/sovereign_scheduler.py::_execute_target
tests/test_site_child_safety_public_observer.py
```

Fixed execution contract:

```text
local dependency: STEGVERSE_REPO_ROOTS_JSON::StegVerse-Labs/Site
command: python scripts/check_child_safety_public_deployment.py
receipt env: STEGVERSE_CHILD_SAFETY_REPORT=<ephemeral/local path>
schedule: hourly through existing SHWP-HEALER-SOVEREIGN-SCHEDULER-001
missing Site root: BLOCKED
missing observer script: BLOCKED
nonzero observer result: BLOCKED
non-VERIFIED_PUBLICLY_REACHABLE receipt: BLOCKED
github_token_required: false
artifact_custody_required: false
remote checkout required: false
```

Source evidence:

```text
target binding: 81cb23510bc5cb1fc976b473a38e14113360a0f5
scheduler handler: 8575b000e7584dbe2d629236859cf0f45e85145a
deterministic tests: b17ad66c2f9c1425280b688efa579e2cdde5a8ba
Test Readiness: 32059184264 SUCCESS
repo-smoke job: 95476280369 SUCCESS
credential refusal: PASS
anonymous exact-source validation fetch: PASS
deterministic Healer tests: PASS
validation-only authority boundary: PASS
```

The handler accepts completion only when the Site observer reports `VERIFIED_PUBLICLY_REACHABLE`, `authority_effect=false`, `github_token_required=false`, and `artifact_custody_required=false`. It writes the public-route observation to an ephemeral/local receipt rather than GitHub artifact custody. No second scheduler or heartbeat was created.

Canonical Site coordination is `StegVerse-Labs/Site#268` / `SITE-WORKFLOW-SURFACE-MINIMIZATION-268-B26-20260817`. Site may retire `.github/workflows/verify-child-safety-public-deployment.yml` only after preserving its local validator/task semantics and validating the resulting exact-current-main tranche.

## Repo-standards ST-018 sovereign task-manager integration

Purpose: execute the existing `StegVerse-Labs/repo-standards` ST-018 task registry through the already-established sovereign Healer scheduler instead of depending on GitHub-hosted token/artifact/issue-write mechanics.

Installed surfaces:

```text
data/orchestrator_targets.json::StegVerse-Labs/repo-standards/st018-local-task-manager
app/sovereign_scheduler.py::_execute_target
tests/test_repo_standards_st018_task_manager.py
data/session_consolidation/repo-standards-st018-local-task-manager.json
```

Fixed execution contract:

```text
local dependency: STEGVERSE_REPO_ROOTS_JSON::StegVerse-Labs/repo-standards
command: python tools/run_st018_task_manager.py
schedule: 00/06/12/18 UTC through existing SHWP-HEALER-SOVEREIGN-SCHEDULER-001
missing repository: BLOCKED
missing task manager: BLOCKED
missing task registry: BLOCKED
non-PASS task report: BLOCKED
github token required: false
remote checkout required: false
```

Source commits:

```text
target binding: c042b8d8b70413bfd38273da80c326ee2ced557c
scheduler handler: 8b8167ddb2bb6d7385d2f0056bcd975d4f4bb7a9
deterministic tests: df6719e45abf8db9ff329d8a573389d69f51db37
released consolidation record: 937b6ab2ef29d3b459f78fff67993a22ce21de14
```

Canonical ST-018 semantics remain owned by `StegVerse-Labs/repo-standards#28`; Healer supplies only the bounded local execution carrier.

## Marketplace projection integration

Healer PR #9 merge `b280025ed0007d10fdbb377cdf77cfd74443565c` binds fixed target `marketplace-coinbase-local-projection-import`. Site PR #352 merged `218fee91a7d2214fec328f74247e079292c45ce0`; Site consumes local Publisher evidence only, refuses credential-bearing environments, and fails closed when local evidence is absent.

## Activation boundary

Source/CI integration is complete, but ordinary live Healer execution remains `MACHINE_OWNED`. Activation requires `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`. No source merge, CI run, chat session, GitHub Action, publication, or deployment substitutes for that receipt.

TV/TVC remains credential authority. No NON-TV/TVC secret/token, provider credential, wallet authority, publication authority, release authority, custody authority, or financial authority is introduced. USER_ONLY remains the sole StegFin signing/broadcast authority. Do not use Render.

## Continuation

Workflow hygiene for `StegVerse-Labs/.github` continues under Healer #34. Child-safety observer source continuation remains canonical in Healer #13 and Site #268/B26. Ordinary scheduler activation belongs to `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; broader Site workflow/token remediation remains at Site #268. Future work must reuse established Healer handlers/scheduler rather than create a second scheduler/heartbeat.
