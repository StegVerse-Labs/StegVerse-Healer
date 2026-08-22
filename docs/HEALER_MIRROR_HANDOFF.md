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
execution issue: #34 OPEN
```

### Current physical result

The imported baseline was 18 `.github` workflows: 12 automatic-push and 6 PR/manual-only. Healer #34 has now executed six parity-proven consolidations.

```text
baseline: 18 total / 12 automatic-push / 6 PR-manual-only
current: 12 total / 9 automatic-push / 3 PR-manual-only
removed: 6 / 18 = 33.33%
stable dispatchers explicitly established: 2
preferred final target: 0/1/2 where technically sufficient
```

Stable dispatcher surfaces:

```text
StegVerse-Labs/.github/.github/workflows/org-control-plane-validate.yml
StegVerse-Labs/.github/.github/workflows/heartbeat-worker-project.yml
```

Validated Healer tranches:

| Removed workflow | Destination | PR | Merge | Heartbeat validation | Org-control validation |
| --- | --- | ---: | --- | ---: | ---: |
| `org-handoff-render.yml` | org control | #251 | `82a5909aa37ea228e9c00dd55fc1e11ab706850b` | 32590490975 PASS | 32590490904 PASS |
| `archive-readiness-validate.yml` | org control | #252 | `fae7f6a1edc4d54dd67134773faf76acc87eae59` | 32590584716 PASS | 32590584788 PASS |
| `org-heartbeat.yml` | heartbeat worker | #253 | `2236df65a495975ca9bc7d9c8fad7d863934617f` | 32590794869 PASS | 32590794862 PASS |
| `org-heartbeat-watchdog.yml` | heartbeat worker/manual only | #254 | `c3256be218dbabdf4fb82e877e71d2884925c904` | 32590947641 PASS | 32590947607 PASS |
| `native-process-worker-canary.yml` | heartbeat worker | #255 | `856d1823283f3ade54ac95094d73ec149c245d74` | 32591051012 PASS | 32591050991 PASS |
| `external-timing-match-validation.yml` | heartbeat worker | #256 | `278299617d17a4f410b0ef0e2d1da1a609b67fc4` | 32591188347 PASS | 32591188133 PASS |

Parity/safety results:

- handoff rendering and generated projection parity preserved;
- archive-readiness validator/test preserved;
- heartbeat source validation preserved without restoring routine state/receipt main-push fanout;
- watchdog remains manually invocable only and was not added to automatic execution;
- native canary handoff is terminal `COMPLETED`, successor policy `NONE`; only retained evidence validation remains;
- external-timing source/validation is complete/released; fixed-cadence and zero-authority checks remain, while `.github#122` retains live producer ownership;
- all six exact heads passed both retained validator families before merge;
- TV/TVC remains credential authority; no NON-TV/TVC secrets/tokens, GitHub-token runtime authority, Render, runtime authority, wallet authority, deployment authority, or provider authority were introduced.

Canonical current evidence:

```text
StegVerse-Labs/.github/control/workflow-surface-registry.json
StegVerse-Labs/.github/control/actions-fanout-workflow-inventory-2026-08-18.json
StegVerse-Labs/.github/docs/ACTIONS_FANOUT_REPAIR_MIRROR_HANDOFF.md
StegVerse-Labs/StegVerse-Healer#34
```

Healer #34 remains open. Ten non-dispatcher workflow surfaces still require independent classification as consolidation/transfer/elimination, active-owner blocked, or evidence-backed standalone exception. Count >2 cannot be treated as terminal without technical exception evidence.

Issue creation, assignment, evaluation admission, workflow success, or source merge alone does not satisfy the hygiene goal. Actual accepted consolidation/transfer/elimination and parity evidence remain required.

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
remote_checkout_required: false
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

Workflow hygiene for `StegVerse-Labs/.github` continues under Healer #34 from the current 12-workflow denominator. Child-safety observer source continuation remains canonical in Healer #13 and Site #268/B26. Ordinary scheduler activation belongs to `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; broader Site workflow/token remediation remains at Site #268. Future work must reuse established Healer handlers/scheduler rather than create a second scheduler/heartbeat.
