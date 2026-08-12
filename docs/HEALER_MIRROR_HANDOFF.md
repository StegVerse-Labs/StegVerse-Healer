# StegVerse-Healer Mirror Handoff

## Authority and active goal

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Branch: `main`
- Goal ID: `HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001`
- Originating session goal: remove GitHub-token production/control-plane authority, preserve TV/TVC as credential/admission authority, and bind Healer scheduling/maintenance to the single resident sovereign heartbeat.
- Canonical organization continuation: `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`
- Canonical worker continuation: `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`
- Repository-local continuation: this handoff plus `data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json` and `data/summary/single_scheduler_migration.json`.
- Current repository state: `SOVEREIGN_SOURCE_COMPLETE_LIVE_CARRIER_MACHINE_OWNED`.
- Chat-session role: `MERGED_INTO_CANONICAL_WORKSTREAM`.

## Governing invariants

```text
credential_authority: TV/TVC
github_token_production_authority: NONE
github_actions_production_role: NONE
production_clock: single resident StegVerse heartbeat
arbitrary_target_command_authority: NONE
remote_source_checkout_required_for_production: false
missing local capability: FAIL_CLOSED
hosted validation: non-authorizing
```

GitHub Actions may validate source when useful, but it is not a production scheduler, heartbeat carrier, credential authority, repository mutator, relay, deployment authority, or activation proof.

## Authoritative files

```text
docs/HEALER_MIRROR_HANDOFF.md
data/orchestrator_targets.json
data/summary/single_scheduler_migration.json
data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json
data/session_consolidation/stegdb-healer-canonical-import.json
app/sovereign_scheduler.py
app/dispatch_orchestrators.py
app/audit_schedules.py
app/relay_stegdeploy_publication.py
```

Cross-repository authority/evidence:

```text
StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
StegVerse-Labs/.github/authorizations/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
StegVerse-Labs/.github/control/worker-registry.d/healer-sovereign-scheduler-001.json
StegVerse-Labs/.github/control/process-worker-adapters.json
StegVerse-Labs/TV/scripts/sovereign_self_heal.py
StegVerse-Labs/TVC/policies/local_repository_mutation/tv_self_heal.v1.json
StegVerse-Labs/SCW/scw/local_health.py
StegVerse-Labs/SCW/scw/scw_core.py
StegVerse-Labs/Continuity/scripts/guardian.py
StegVerse-org/core-node-runtime-demo/tools/stegdeploy_runtime_intake_local.py
```

## Execution ownership and claims

### MACHINE_OWNED — do not compete

```yaml
- task_id: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
  execution_owner: resident sovereign heartbeat + healer-sovereign-scheduler-worker
  claim_state: MACHINE_OWNED
  worker_registry_ref: StegVerse-Labs/.github/control/worker-registry.d/healer-sovereign-scheduler-001.json
  manual_execution_allowed: false
  manual_allowed_role: observation
  collision_scope: scheduler claim/fence, process-adapter invocation, live target execution, scheduler receipt persistence
  release_condition: admitted heartbeat execution emits the no-token scheduler receipt and current target state
  next_executable_action: resident heartbeat executes the worker under its current admitted claim/fence
```

### COMPLETED / SUPERSEDED

- GitHub API workflow-dispatch scheduler transport: `SUPERSEDED`.
- `HEALER_GH_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`, `HEALER_PAT`, `GH_STEGVERSE_AI_TOKEN` as production authority: `SUPERSEDED`.
- duplicate `quiet-enforcer.yml` hosted scheduler: `SUPERSEDED`.
- GitHub-hosted `supercheck_core.yml` mutation/PR transport: `SUPERSEDED`.
- token-bearing `forward-to-bridge.yml` repository dispatch: `SUPERSEDED`.
- broad scheduled `sync-to-canonical.yml` generic StegDB overwrite path: `SUPERSEDED`; durable record `data/session_consolidation/stegdb-healer-canonical-import.json`.
- Healer source implementation for fixed local scheduling: `COMPLETE`.
- heartbeat handoff/authorization/registry/process-adapter binding: `COMPLETE`.

No chat/session implementation claim remains on machine-owned runtime paths.

## Installed sovereign scheduler

`app/sovereign_scheduler.py`:

- rejects GitHub credential environment variables;
- consumes `STEGVERSE_REPO_ROOTS_JSON` and only already-materialized repositories;
- uses fixed code-defined handlers rather than commands supplied by target records;
- evaluates cadence from `data/orchestrator_targets.json`;
- returns `COMPLETE`, `BLOCKED`, `REVIEW_REQUIRED`, or `FAILED` according to actual handler outcomes;
- treats missing repositories/capabilities as fail-closed conditions;
- grants no GitHub, provider, wallet, release, deployment, or arbitrary process authority.

The canonical heartbeat binding is `process:healer-sovereign-scheduler-v1`.

## Managed target state

### SCW

Production execution is local through `scw.scw_core` and `scw/local_health.py`. Repository enumeration and required-file inspection use materialized roots rather than GitHub API credentials. Remote `autopatch` is not a fallback production mechanism. Hosted `scw_orchestrator.yml` and `uptime.yml` are compatibility/non-production surfaces.

State: `SOVEREIGN_LOCAL_HANDLERS_BOUND`.

### TV

`StegVerse-Labs/TV/scripts/sovereign_self_heal.py` is the bounded local repair executor. It requires TVC-owned exact-scope policy from `StegVerse-Labs/TVC/policies/local_repository_mutation/tv_self_heal.v1.json`, uses the existing TVC execution-grant layer, limits repair classes to the admitted normalization boundary, and validates TV's operational handoff after mutation.

State: `SOVEREIGN_LOCAL_HANDLER_BOUND_TVC_GRANT_REQUIRED`.

### Continuity

`StegVerse-Labs/Continuity/scripts/guardian.py` uses locally materialized repository roots and node-local acknowledgement evidence. GitHub issue enumeration, GitHub credentials, OIDC-for-GitHub execution, and hosted status pushing are not production dependencies. Hosted `continuity.yml` is a compatibility marker.

State: `SOVEREIGN_LOCAL_GUARDIAN_BOUND`.

### Site

The Healer scheduler has a fixed local Site handler invoking the repository-owned local orchestration checks against a materialized Site tree. Site remains authoritative for its business logic and task admission.

State: `SOVEREIGN_LOCAL_HANDLER_BOUND`.

### Quiet Enforcer

`app/audit_schedules.py` audits materialized workflow trees locally and fails closed when a required repository is absent. Hosted daily clocks and GitHub Contents API access are retired.

State: `SOVEREIGN_LOCAL_HANDLER_BOUND`.

### StegDeploy relay

`app/relay_stegdeploy_publication.py` consumes locally materialized LLM-adapter/core-node state. Core-node local intake accepts the retained publication receipt only when the exact published digest is already present in the local Docker image store. It does not log into or pull from GHCR and does not use `repository_dispatch`.

State: `SOVEREIGN_LOCAL_HANDLER_BOUND_LOCAL_IMAGE_PROOF_REQUIRED`.

### CosDen / StegDB

CosDen remains audit-only with canonical content ownership under `StegVerse-Labs/StegDB/canonical/cosden`.

The previous broad Healer `sync-to-canonical.yml` behavior is intentionally not reproduced. StegDB contains multiple package-specific authorities and does not expose a single Healer-wide package that authorizes generic overwrite of workflows/policy/schema/docs/tools. A future import requires a new exact Healer-scoped manifest plus TVC mutation authority.

Durable supersession record: `data/session_consolidation/stegdb-healer-canonical-import.json`.

## Completed mutation evidence

Key source/control commits include:

```text
d972f0c92c7f492bcf420c96056f68ff4c47f65d  SCW local scanner
06c14cbf9e9f9491532776bd241930e07083c725  SCW sovereign core
b3df5feed791c18747f06e1d1a786cbc52d4c4ea  Healer sovereign scheduler
0b07675ec2095ea3286f0fdff6553b7a55d9c37a  legacy dispatcher retirement
2b2020538aa06a275229b94b0e25c1123297155d  heartbeat worker
79f307d56127fb8490a78536c5be31452ee0b858  worker authorization
84d173ba4dd61efc66504e46895e8218add35b43  process-adapter binding
70cfd3f987783ad4c34c31b76509471c39663970  registry-fragment invariant correction
95a596df289695b7dbb09807c59fa1812d0e1511  Continuity local guardian
4bc4f7f89dc91712d337dbecab472584294d4b26  core-node local StegDeploy intake
95860c2b0a366dd17e1b98cf5b5a987ad7c49974  TVC local mutation policy
c0de3b8d057eb884aa9ed7cf09d301e761eef7a4  TV sovereign self-heal executor
5cd027b05e31720ee3213dd5fcb860b897c7deda  TV hosted self-heal retirement
f9bac0a7c0f05d9bb73a6d2783320854979a4bca  Continuity hosted production retirement
9811fec37599cf0b5a3f1f38f863fa34f31dc9cd  SCW orchestrator hosted execution retirement
6a0f081f356d24a7b5d88b945cb6d75188ea098c  SCW uptime hosted execution retirement
3a36738524e1a045d584a3a7a4231b82563b32f1  supercheck mutation transport retirement
2def997a49f77d707aa62ed5b97e333fd0a303b0  bridge token dispatch retirement
67366a29437ed213aa763307acc596ccb52cf8b2  generic StegDB hosted sync retirement
4ee44bbb996e2ca4a27ec7c072a68e6adb7911d9  target registry reconciliation
e718664136579fb339940ee282f8e56fdc4a5225  StegDB sync supersession record
a5a64d396ab811366fa0c978d6e6223beed67934  no-token migration ownership reconciliation
c44029e8fb07e2659bd47334cd15f2ede2983699  sovereign scheduler migration receipt reconciliation
```

## Validation evidence

Directly inspected Heartbeat Worker Project run `31624805596` executed an anonymous no-token source checkout, proved GitHub credential variables absent, compiled runtime/workers/scripts, and parsed canonical JSON. It then failed at `validate_executable_handoffs.py` because the earlier revision of `SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json` used an invalid `goal.successor_policy` value.

The current handoff on `main` uses the admitted schema value `INHERIT_OR_NARROW` and includes the required `expires_at`. A successor hosted run has not been directly observed in this handoff and is therefore not claimed as passing.

Hosted validation is not an activation gate. Live production activation requires resident-heartbeat execution evidence.

## Machine-observable remaining activation work

Owner: `StegVerse-Labs/.github` resident sovereign heartbeat.

```text
SHWP-HEALER-SOVEREIGN-SCHEDULER-001
-> admitted claim/fence
-> process:healer-sovereign-scheduler-v1
-> materialized repository roots
-> fixed target handlers
-> no-token scheduler receipt
-> current target outcomes
```

The organization-level carrier is itself still active machine work under `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`. This repository does not claim live scheduler execution until the carrier produces inspectable evidence.

No manual/session fallback is authorized for that runtime claim.

## Cross-repository propagation

Activation evidence, when present and admitted by consumer release gates, may propagate to:

```text
StegVerse-Labs/Site
GCAT-BCAT-Engine/Publisher
StegVerse-Labs/admissibility-wiki
StegVerse-Labs/stegguardian-wiki
master-records/orchestration when required by the canonical activation chain
```

No propagation is claimed from source completion alone.

## Session consolidation

All session-specific Healer requirements are either completed, superseded, or durably transferred:

1. remove GitHub-token production scheduler transport — complete;
2. bind TV/TVC credential/admission authority — complete at source/control layer;
3. bind scheduler to the resident heartbeat — complete at handoff/authorization/registry/process-adapter layer;
4. migrate SCW — complete at source/control layer;
5. migrate Continuity — complete at source/control layer;
6. migrate TV self-heal to TVC execution grants — complete at source/control layer;
7. migrate quiet-enforcer — complete at source/control layer;
8. migrate StegDeploy relay/intake — complete at source/control layer;
9. eliminate duplicate/bypass token-bearing workflows — complete/superseded;
10. retire unsafe generic StegDB sync — complete/superseded with durable record;
11. live resident execution — machine-owned by the canonical heartbeat, not a chat claim;
12. downstream propagation — machine-owned successor condition after immutable activation evidence.

MERGED INTO: `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`, and this repository handoff.

Deleting the chat does not remove an implementation requirement, credential decision, collision boundary, owner, release condition, or next executable action.

## Completion accounting

Current goal denominator:

- required developed/source-control deliverables: 24;
- source/control validation groups: 6;
- integration groups: 8;
- live activation groups: 3;
- session goals: 12.

Current state:

- developed files/control surfaces: 24/24;
- scaffolding or stubs: 0 production stubs;
- missing required source/control files: 0;
- validation: 5/6 — current successor hosted validation remains unobserved, while prior no-token checks reached the corrected handoff defect;
- integration: 8/8 at source/control ownership level;
- live activation: 1/3 — worker admission/binding installed; resident execution receipt and downstream propagation remain machine-owned;
- session consolidation: 12/12.

## Archive condition

Repository/source work from this session is archive-safe. Product activation is not complete, but its remaining work is durably machine-owned by the canonical resident heartbeat and downstream consumer lanes. Archiving this session does not assert runtime activation.
