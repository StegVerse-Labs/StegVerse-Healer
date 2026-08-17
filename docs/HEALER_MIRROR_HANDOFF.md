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

## Released source integrations

- `HEALER-G18-PRE-CARRIER-ASSIST-001`: PR #5 merge `571b6a86737173a89235110294025f9808695531`.
- `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`: PR #7 merge `ecf96188348c097dfdea3ce55c47db9dff6e84ef`.
- `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`: source/integration COMPLETE_RELEASED; issue #8 closed.
- `HEALER-RSTD-ST018-LOCAL-TASK-MANAGER-001`: source/integration COMPLETE_RELEASED; issue #11.

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
initial consolidation record: d6d60f7e661ea9a871bd0f8593327a08e019f005
released consolidation record: 937b6ab2ef29d3b459f78fff67993a22ce21de14
```

Validation:

```text
Test Readiness 32053936357: SUCCESS
repo-smoke: SUCCESS
credential refusal: PASS
anonymous exact-source validation fetch: PASS
deterministic Healer tests: PASS
Validate Session Consolidation 32053936480: SUCCESS
```

Canonical ST-018 semantics remain owned by `StegVerse-Labs/repo-standards#28`; Healer supplies only the bounded local execution carrier. No second scheduler or heartbeat was created.

## Marketplace projection integration

Healer PR #9 merge `b280025ed0007d10fdbb377cdf77cfd74443565c` binds fixed target `marketplace-coinbase-local-projection-import`. Site PR #352 merged `218fee91a7d2214fec328f74247e079292c45ce0`; Site consumes local Publisher evidence only, refuses credential-bearing environments, and fails closed when local evidence is absent.

## Activation boundary

Source/CI integration is complete, but ordinary live Healer execution remains `MACHINE_OWNED`. Activation requires `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`. No source merge, CI run, chat session, GitHub Action, publication, or deployment substitutes for that receipt.

TV/TVC remains credential authority. No NON-TV/TVC secret/token, provider credential, wallet authority, publication authority, release authority, custody authority, or financial authority is introduced. USER_ONLY remains the sole StegFin signing/broadcast authority. Do not use Render.

## Continuation

The repo-standards ST-018 carrier is archive-safe as a chat-owned source implementation. Future ST-018 task semantics belong to `StegVerse-Labs/repo-standards#28`; ordinary scheduler activation belongs to `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; broader Site workflow/token remediation remains at Site #268.
