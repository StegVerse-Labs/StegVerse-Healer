# StegVerse-Healer Mirror Handoff

## Authority and active goal

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-Labs/StegVerse-Healer`
- Branch: `main` after merge of `feat/g18-pre-carrier-healer-assist`
- Primary goal ID: `HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001`
- Active integration goal ID: `HEALER-G18-PRE-CARRIER-ASSIST-001`
- Originating goal: keep Healer scheduling/repair local and sovereign, preserve TV/TVC as the only credential/admission authority, and assist canonical heartbeat recovery without creating a second heartbeat or scheduler.
- Canonical organization continuation: `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`
- Canonical heartbeat continuation: `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`
- Canonical Healer scheduler continuation: `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`
- Repository-local continuation: this handoff, `data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json`, `data/session_consolidation/g18-pre-carrier-assist.json`, and `data/summary/single_scheduler_migration.json`.

## Governing invariants

```text
credential_authority: TV/TVC
credential_requirement_for_pre_carrier_assist: NONE
non_tv_tvc_secret_or_token_allowed: false
github_token_production_authority: NONE
github_actions_production_role: NONE
heartbeat_owner: StegVerse-Labs/.github G18
healer_pre_carrier_authority_effect: NONE
healer_may_execute_hb29_to_hb30_transition: false
healer_may_synthesize_hb30: false
arbitrary_target_command_authority: NONE
remote_source_checkout_required_for_production: false
missing local capability: FAIL_CLOSED
hosted validation: non-authorizing
```

Healer may inspect and diagnose the canonical heartbeat source before HB30 exists. It does not own the heartbeat transition, worker claim/fence/lease, carrier state, provider/wallet state, or TV/TVC authority.

## Authoritative files

```text
docs/HEALER_MIRROR_HANDOFF.md
app/sovereign_scheduler.py
app/pre_carrier_assist.py
tests/test_pre_carrier_assist.py
data/orchestrator_targets.json
data/session_consolidation/g18-pre-carrier-assist.json
data/session_consolidation/tv-tvc-no-github-token-dispatch-migration.json
data/summary/single_scheduler_migration.json
.github/workflows/test-readiness.yml
```

Cross-repository authority/evidence:

```text
StegVerse-Labs/.github/management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
StegVerse-Labs/.github/authorizations/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json
StegVerse-Labs/.github/control/worker-registry.d/healer-sovereign-scheduler-001.json
StegVerse-Labs/.github/control/process-worker-adapters.json
StegVerse-Labs/TV/scripts/sovereign_self_heal.py
StegVerse-Labs/TVC/policies/local_repository_mutation/tv_self_heal.v1.json
StegVerse-Labs/SCW/scw/local_health.py
StegVerse-Labs/Continuity/scripts/guardian.py
```

## Execution ownership and claims

### MACHINE_OWNED — do not compete

`SHWP-DURABLE-RUNTIME-ACTIVATION / G18 / fencing token 18` owns the real HB29→HB30+ transition and subsequent independent WorkerCoordinator observation.

`SHWP-HEALER-SOVEREIGN-SCHEDULER-001` owns ordinary post-carrier Healer scheduling and fixed local target execution.

Neither machine path may be replaced by a chat session, GitHub Actions, Render, Vercel, Cloudflare, hosted inference, or another scheduler/process host.

### Session implementation claim

```yaml
task_id: HEALER-G18-PRE-CARRIER-ASSIST-001
issue: StegVerse-Labs/StegVerse-Healer#4
claimant: current-session-healer-pre-carrier-integration-lane
role: CLAIMED_FOR_IMPLEMENTATION
claim_created_at: 2026-08-17T14:39:58Z
files:
  - app/pre_carrier_assist.py
  - tests/test_pre_carrier_assist.py
  - .github/workflows/test-readiness.yml
  - data/session_consolidation/g18-pre-carrier-assist.json
  - docs/HEALER_MIRROR_HANDOFF.md
release_condition: merge validated source, record the G18 continuation, then mark COMPLETE_RELEASED
collision_boundary: no live heartbeat/worker claim/fence/lease/carrier-state mutation and no credential/provider/wallet authority
```

There is no separate validation claimant. Hosted Test Readiness is validation-only and non-authorizing.

## Installed pre-carrier G18 assist

`app/pre_carrier_assist.py` is a bounded local diagnostic/readiness producer for the already-materialized `StegVerse-Labs/.github` repository.

It:

- requires `STEGVERSE_REPO_ROOTS_JSON`; no remote checkout is a production fallback;
- rejects GitHub/provider/wallet credential variables because this assist requires no credentials;
- verifies immutable legacy HB29 and generation 29;
- verifies the canonical v12 carrier and independent WorkerCoordinator source files;
- verifies `management/SHWP_STATE_TRANSITION_CONTINUITY_CONTRACT.json` semantics, including first successor HB30, no extra-machine requirement, no always-on-host requirement, TV/TVC authority, and prohibition of NON-TV/TVC secret/token authority;
- verifies G18 remains `MACHINE_OWNED_BOUND_G18` at fencing token 18 and live activation has not already been claimed;
- emits `READY_FOR_G18_TRANSITION`, `BLOCKED`, `REVIEW_REQUIRED`, or `FAILED` plus an exact next action;
- hashes legacy HB29 as evidence but does not mutate it;
- does not invoke `scripts/advance_heartbeat_transition.py`;
- does not create `control/heartbeat-carrier-runtime-state.json` and does not synthesize HB30.

This breaks the prior circular dependency at the diagnostic/repair-assist layer: Healer can now evaluate the prerequisites needed by G18 before the ordinary Healer scheduler itself is admitted by the heartbeat.

The authority path is:

```text
materialized StegVerse source
-> Healer pre-carrier inspection/diagnosis (authority_effect NONE)
-> READY_FOR_G18_TRANSITION or exact fail-closed blocker
-> existing G18 claim/fence
-> scripts/advance_heartbeat_transition.py
-> HB30+
-> independent WorkerCoordinator observation
-> ordinary Healer scheduler may later execute under its own admitted worker
```

## Existing sovereign scheduler

`app/sovereign_scheduler.py` remains the ordinary Healer scheduler. It rejects GitHub credential variables, operates on already-materialized repositories, uses fixed code-defined handlers, fails closed on missing repositories/capabilities, and grants no GitHub/provider/wallet/release/deployment authority.

Managed local targets remain Site, SCW, SCW uptime, TV self-heal through TVC authority, Continuity, Quiet Enforcer, and StegDeploy relay. CosDen remains audit-only under StegDB canonical ownership.

## Completed source/control work

- GitHub workflow-dispatch as production scheduler transport: `SUPERSEDED`.
- GitHub token/PAT production scheduler authority: `SUPERSEDED`.
- SCW local scanner/runtime binding: `COMPLETE`.
- Continuity local guardian binding: `COMPLETE`.
- TV self-heal through TVC local mutation policy/grant: `COMPLETE` at source/control layer.
- Quiet Enforcer local audit: `COMPLETE`.
- StegDeploy local relay/intake: `COMPLETE` at source/control layer.
- unsafe generic StegDB overwrite path: `SUPERSEDED`.
- Healer scheduler worker authorization/registry/process-adapter binding: `COMPLETE`.
- bounded G18 pre-carrier diagnostic source and deterministic tests: implemented on issue #4 branch; merge/validation evidence required before release claim.

Earlier source/control history remains preserved in Git history and the migration records; this handoff is the canonical current continuation rather than a duplicate historical ledger.

## Validation

Required commands:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python app/pre_carrier_assist.py
```

For production-like pre-carrier inspection, `STEGVERSE_REPO_ROOTS_JSON` must map `StegVerse-Labs/.github` to an already-materialized local root. No credential is required.

`.github/workflows/test-readiness.yml` performs JSON/smoke validation and deterministic unit tests. A passing hosted run proves source/test consistency only. It does not prove HB30, WorkerCoordinator runtime observation, scheduler activation, provider execution, wallet readiness, or trade execution.

## Machine-observable incomplete work

### Heartbeat activation

Owner: `StegVerse-Labs/.github / SHWP-DURABLE-RUNTIME-ACTIVATION / G18`.

Release condition:

```text
receipts/heartbeat-transition-continuity/latest.json = valid CARRIER_TRANSITION_COMPLETE at HB30+
control/heartbeat-carrier-runtime-state.json = HB30+
control/heartbeat-state.json = unchanged legacy HB29
control/worker-runtime-state.json = independently observes carrier epoch
worker-control-plane evidence present
reconstruction PASS
no duplicate claim/fence
no NON-TV/TVC credential authority
```

### Ordinary Healer scheduler activation

Owner: `SHWP-HEALER-SOVEREIGN-SCHEDULER-001`.

Release condition: admitted post-carrier execution emits `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json` with current target outcomes and no forbidden credential authority.

### Downstream product activation

Sovereign inference remains owned by `.github#60` and its TVC → LLM-adapter → Master Records chain. StegFin remains owned by its canonical worker/task state and must stop at `WALLET_HANDOFF_READY` before USER_ONLY signing/broadcast.

## Cross-repository propagation

No propagation is inferred from source completion. After immutable activation evidence and applicable consumer gates, evidence may propagate to Site, Publisher, admissibility-wiki, stegguardian-wiki, and passive Master Records custody where their canonical contracts require it.

## Session consolidation

Session-specific Healer requirements are durably represented by this handoff, issue #4, and `data/session_consolidation/g18-pre-carrier-assist.json`. Once issue #4 source is merged, Test Readiness is green, the claim record is `COMPLETE_RELEASED`, and the canonical G18 continuation references the assist path, no unique chat implementation responsibility remains for this Healer integration.

MERGED INTO after release:

```text
StegVerse-Labs/StegVerse-Healer/docs/HEALER_MIRROR_HANDOFF.md
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github#65
```

## Completion accounting

Current denominator for this integration goal:

- required developed/source-control surfaces: 5;
- deterministic validation groups: 2 (unit tests + Test Readiness workflow);
- integration groups: 3 (Healer source/handoff, G18 durable continuation, claim release);
- live activation groups: 2 (HB30+ carrier; independent WorkerCoordinator observation);
- session transfer groups: 1.

Current pre-merge state:

- developed files/control surfaces: 5/5;
- scaffolding or production stubs: 0;
- missing source/control files: 0;
- deterministic validation: 1/2 pending hosted workflow evidence;
- integration: 1/3 pending G18 continuation and claim release;
- live activation: 0/2;
- session consolidation: 0/1 until merge/claim release.

## Archive condition

Do not treat this source implementation as HB30 activation. This Healer integration becomes archive-safe only after the branch is merged/validated, issue #4 and the claim record are released, and the canonical G18 continuation durably references the pre-carrier assist. Product activation may remain machine-owned after that transfer, but no chat-only requirement may remain.
