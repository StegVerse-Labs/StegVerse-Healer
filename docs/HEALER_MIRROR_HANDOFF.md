# StegVerse-Healer Mirror Handoff

Updated: 2026-08-26

## Canonical state

```text
repository: StegVerse-Labs/StegVerse-Healer
branch: main
primary_goal: HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_token_production_authority: NONE
github_actions_production_role: NONE
heartbeat_owner: StegVerse-Labs/.github independent oscillator reference; G18 not downstream scheduler gate
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
wallet_signing_and_broadcast: USER_ONLY
state: SOURCE_CONTROL_RELEASED_LIVE_SCHEDULER_ACTIVATION_MACHINE_OWNED
```

Canonical organization/runtime continuations are `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`, and `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`.

Detailed scoped handoffs supersede older summary prose for their lanes:

```text
docs/HEALER_GITHUB_ROOT_WORKFLOW_HYGIENE_MIRROR_HANDOFF.md
docs/SITE_ERL_SOVEREIGN_SYNC_MIRROR_HANDOFF.md
docs/HEALER_SITE_B27_VALIDATION_MIRROR_HANDOFF.md
docs/HEALER_SITE_HEARTBEAT_RESPONSE_CARRIER_MIRROR_HANDOFF.md
docs/HEALER_STEGFIN_PUBLICATION_OBSERVER_MIRROR_HANDOFF.md
```

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

### Current physical result — reconciled live state

The imported baseline was 18 `.github` workflows: 12 automatic-push and 6 PR/manual-only. Healer #34 has now executed seven parity-proven consolidations.

```text
baseline: 18 total / 12 automatic-push / 6 PR-manual-only
current: 11 total / 8 automatic-push / 3 PR-manual-only
removed: 7 / 18 = 38.89%
stable dispatchers explicitly established: 2
remaining non-dispatchers: 9
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
| `activate-host-self-attest-worker.yml` | heartbeat worker | #257 | `1240cc0087f5777b08c1913561d4b7125df74cbf` | 32591396135 PASS | 32591396122 PASS |

Parity/safety results:

- handoff rendering and generated projection parity preserved;
- archive-readiness validator/test preserved;
- heartbeat source validation preserved without restoring routine state/receipt main-push fanout;
- watchdog remains manually invocable only and was not added to automatic execution;
- native canary and host self-attest handoffs are terminal `COMPLETED`, successor policy `NONE`; only retained evidence validation remains;
- external-timing source/validation is complete/released; fixed-cadence and zero-authority checks remain, while `.github#122` retains live producer ownership;
- all seven exact heads passed both retained validator families before merge;
- TV/TVC remains credential authority; no NON-TV/TVC secrets/tokens, GitHub-token runtime authority, Render, runtime authority, wallet authority, deployment authority, or provider authority were introduced.

Canonical current evidence:

```text
StegVerse-Labs/.github/control/workflow-surface-registry.json
StegVerse-Labs/.github/control/actions-fanout-workflow-inventory-2026-08-18.json
StegVerse-Labs/.github/docs/ACTIONS_FANOUT_REPAIR_MIRROR_HANDOFF.md
docs/HEALER_GITHUB_ROOT_WORKFLOW_HYGIENE_MIRROR_HANDOFF.md
StegVerse-Labs/StegVerse-Healer#34
```

Healer #34 remains open. Nine non-dispatcher workflow surfaces still require owner-safe classification as consolidation/transfer/elimination, active-owner blocked, or evidence-backed standalone exception. Count >2 cannot be treated as terminal without technical exception evidence.

Issue creation, assignment, evaluation admission, workflow success, or source merge alone does not satisfy the hygiene goal. Actual accepted consolidation/transfer/elimination and parity evidence remain required.

## Released source integrations

- `HEALER-G18-PRE-CARRIER-ASSIST-001`: PR #5 merge `571b6a86737173a89235110294025f9808695531`.
- `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`: PR #7 merge `ecf96188348c097dfdea3ce55c47db9dff6e84ef`.
- `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`: source/integration COMPLETE_RELEASED; issue #8 closed.
- `HEALER-RSTD-ST018-LOCAL-TASK-MANAGER-001`: source/integration COMPLETE_RELEASED; issue #11.
- `HEALER-SITE-CHILD-SAFETY-PUBLIC-OBSERVER-001`: source/integration COMPLETE_RELEASED; issue #13 pending closeout record only.
- `HEALER-SITE-ERL-SOVEREIGN-SYNC-039`: source/integration COMPLETE_RELEASED through issue #39 / PR #40; live execution pending scheduler receipt.

## Executive Rhetoric Ledger sovereign Site sync — source RELEASED / live execution pending

Canonical scoped handoff:

`docs/SITE_ERL_SOVEREIGN_SYNC_MIRROR_HANDOFF.md`

```text
canonical_issue: #39
source_pull_request: #40
validated_head: aca5b7871e2720b0d56757e33fc2a22c10291136
Test Readiness: 32670203077 SUCCESS
repo-smoke job: 97269769966 SUCCESS
merge_commit: ff3d9985b773d91dce0d90351a7a8a04a499c59b
source_state: COMPLETE_RELEASED
live_execution_state: MACHINE_OWNED_PENDING_SCHEDULER_RECEIPT
site_github_workflow_retirement_authorized: false
```

The fixed target `executive-rhetoric-ledger-local-sync` runs at 14 UTC on the existing sovereign scheduler only. `app/site_erl_sync.py` requires already-materialized Site + Executive_Rhetoric_Ledger roots, validates source JSON, mirrors exact bytes, verifies SHA-256 identity, emits a destination-owned acknowledgment, refuses GitHub credentials, and has no remote checkout, artifact custody, GitHub writeback, runtime, provider, publication, or activation authority.

The resident `.github` scheduler registry/handoff already consumes #40 evidence; no duplicate worker was created.

Do not remove Site `.github/workflows/sync-executive-rhetoric-ledger.yml` until the live scheduler receipt proves the fixed target COMPLETE/PASS.

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

Source/CI integration is complete for the scheduler and its released handlers, but ordinary live Healer execution remains `MACHINE_OWNED`.

Required live receipt:

`StegVerse-Labs/.github/receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`

Live inspection on 2026-08-26 still reports that receipt absent. No source merge, CI run, chat session, GitHub Action, publication, or deployment substitutes for it.

Canonical machine handoff:

`StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`

Current scheduler task state remains `HANDOFF_READY`, executor `AUTHORIZED`, worker available. The scheduler is independently admitted and does not depend on G18 terminalization or `SHWP-DURABLE-RUNTIME-ACTIVATION` as a downstream gate.

The upstream physical heartbeat handoff `StegVerse-Labs/.github/handoffs/SHWP-IPHONE-HB30-INLINE-CAPSULE-002.json` is source-released but remains at `HUMAN_PHYSICAL_EXECUTION_BOUNDARY` / `PHYSICAL_RECEIPT_NOT_YET_OBSERVED` on the current iPhone. No credential is required for that physical step; G18 and WorkerCoordinator own subsequent materialization and observation.

TV/TVC remains credential authority. No NON-TV/TVC secret/token, provider credential, wallet authority, publication authority, release authority, custody authority, or financial authority is introduced. USER_ONLY remains the sole StegFin signing/broadcast authority. Do not use Render.

## Continuation

Workflow hygiene for `StegVerse-Labs/.github` continues under Healer #34 from the current **11-workflow** denominator, not the superseded 12-workflow summary. Nine non-dispatcher surfaces remain owner-sensitive.

Site cost continuation remains Site #268. The VA Claims Guide lane is already released and must not be recreated. Current Site dependencies include the merged-but-not-task-observed VA governed-surface observer, Thought Experiments B27, the active StegFin `validate.yml` publication claim, and eventual retirement of the legacy ERL GitHub carrier only after a real sovereign scheduler receipt.

Ordinary scheduler activation belongs to `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`; broader Site workflow/token remediation remains at Site #268. Future work must reuse established Healer handlers/scheduler rather than create a second scheduler/heartbeat.


## Coinbase StegDeploy sovereign Gateway activation

Canonical scoped handoff:

`docs/COINBASE_STEGDEPLOY_GATEWAY_ACTIVATION_MIRROR_HANDOFF.md`

This lane reuses the existing `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` rather than creating a second scheduler or heartbeat.

Merged source on `main` via PR #41 / `1a6dacf80b84e62b2c8709f9dcc75765cea1f5f7`:

```text
app/coinbase_stegdeploy_gateway.py
app/sovereign_scheduler.py fixed handler binding
data/orchestrator_targets.json::coinbase-stegdeploy-sovereign-gateway
tests/test_coinbase_stegdeploy_gateway.py
```

The handler consumes only already-local `StegVerse-org/LLM-adapter` + `StegVerse-Labs/TVC` roots, refuses GitHub/provider credentials, requires an authentic non-secret TVC no-value decision receipt, invokes the already-merged local StegDeploy bootstrap, and requires canonical loopback Coinbase readiness with `gateway_execution_authority=NONE`.

Source is MERGED on main. Hosted Test Readiness run `33118079568` / job `98677773520` passed the semantic implementation before a final formatting-only registry cleanup. This does not claim sovereign execution, public HTTPS reachability, TVC recipient liveness, owner ingress, provider capability, order execution, or settlement.

Next runtime boundary: the existing sovereign scheduler executes this target on the admitted resident substrate. Missing local source, missing Docker/StegDeploy prerequisites, or missing TVC decision receipt must remain BLOCKED with no fabricated readiness.


### Coinbase Gateway decision source closure

TVC PR #173 merged as `e8813e81494deb8e8563763675b5123e360397e6`, supplying the canonical non-secret no-value Gateway decision receipt. Exact-current TVC runs `33118626226` and `33118626234` passed.

Healer PR #42 merged as `a60e9d6717b4784591dffca8147b0b4afda2d468` with Test Readiness `33118760520 SUCCESS`, requiring canonical decision schema, receipt digest and SHA-256 policy/decision bindings before local StegDeploy execution.

This closes the remaining source dependency for the Gateway scheduler target. Runtime execution, loopback readiness, public HTTPS route, TVC recipient liveness and owner ingress remain separate unobserved predicates.

## 2026-08-31 resident scheduler gate correction

The current organization handoff and `.github` PR #707 supersede older Healer prose that treated `SHWP-DURABLE-RUNTIME-ACTIVATION` / G18 as an upstream scheduler dependency.

Current machine path:

```text
native resident WorkerCoordinator
-> local canonical source refresh
-> resident request sweep
-> RESIDENT-EXEC-HEALER-SOVEREIGN-SCHEDULER-001
-> fresh independent task admission / claim / fence
-> fixed Healer handlers
-> no-token scheduler receipt
```

G18/fence18 is retained only as stale housekeeping in the durable-runtime lane and must not delay the Healer scheduler. The next required goal is authentic resident consumption of the existing Healer request and production of the scheduler receipt.

## 2026-08-31 local resident source discovery closure

The canonical `.github` Healer worker now performs fail-closed local source discovery rather than requiring session-prepopulated source variables before it can attempt the scheduler.

Current behavior:

```text
explicit non-secret STEGVERSE_HEALER_ROOT / STEGVERSE_REPO_ROOTS_JSON when present
else
unique canonical local StegVerse-Healer tree + canonical local repository map discovery
-> merge safe named local roots already retained by the native WorkerCoordinator service
-> run fixed Healer targets
```

Canonical search locations are local-only and perform no clone/fetch/pull. Missing or ambiguous Healer source remains BLOCKED. The heartbeat carrier receives none of these repository locators.

This removes declaration-only source-root blockers from the resident scheduler path. The next required goal remains authentic consumption of `RESIDENT-EXEC-HEALER-SOVEREIGN-SCHEDULER-001` and production of the no-token scheduler/Gateway receipts.
