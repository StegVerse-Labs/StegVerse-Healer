# Healer .github Workflow Hygiene Mirror Handoff

Updated: 2026-08-26 16:18 CDT
Repository owner: `StegVerse-Labs/StegVerse-Healer`
Target repository: `StegVerse-Labs/.github`
Canonical issue: `StegVerse-Labs/StegVerse-Healer#34`
State: ACTIVE_OWNER_RECONCILIATION_AND_COST_REDUCTION

## Authority

StegVerse-Healer owns repository hygiene/workflow-surface minimization. This lane may consolidate repository-authored GitHub validation surfaces only after preserving required validation semantics and active-owner boundaries.

```text
primary runtime/control plane: StegVerse
credential authority: TV/TVC
NON-TV/TVC secrets/tokens: PROHIBITED
GitHub-token production/runtime authority: NONE
Render: PROHIBITED
preferred workflow target: 0/1/2 where technically sufficient
count >2: requires explicit technical exception evidence
```

Workflow consolidation never grants runtime, heartbeat, claim, fence, lease, deployment, wallet, provider, publication, custody, or credential authority. Workflow success never substitutes for runtime activation.

## Accepted evaluation provenance

```text
evaluation document: docs/GITHUB_ROOT_WORKFLOW_HYGIENE_EVALUATION_REQUEST.md
admission PR: Healer #33
validated head: b150868c9d6083a6c032fb0d8a2f747f7e142283
Test Readiness: 32577928955 SUCCESS
merge: 9090dde4b38795226f3179e03dcbf1ad8592dc64
execution issue: Healer #34 OPEN
```

## Exact current result

Imported baseline:

```text
13 workflow files
12 automatic-push
6 PR/manual-only
```

Current target-repository evidence, rechecked on live `StegVerse-Labs/.github/main`:

```text
3 workflow files
8 automatic-push
2 PR/manual-only
15 standalone workflows removed with parity preservation
2 stable dispatchers established
reduction: 7/18 = 38.89%
```

Stable dispatchers:

```text
StegVerse-Labs/.github/.github/workflows/org-control-plane-validate.yml
StegVerse-Labs/.github/.github/workflows/heartbeat-worker-project.yml
```

Canonical machine/current target evidence:

```text
StegVerse-Labs/.github/control/workflow-surface-registry.json
StegVerse-Labs/.github/control/actions-fanout-workflow-inventory-2026-08-18.json
StegVerse-Labs/.github/docs/ACTIONS_FANOUT_REPAIR_MIRROR_HANDOFF.md
```

## Validated consolidation history

| Removed standalone workflow | Destination | PR | Merge | Heartbeat validation | Org-control validation |
| --- | --- | ---: | --- | ---: | ---: |
| `org-handoff-render.yml` | org control | #251 | `82a5909aa37ea228e9c00dd55fc1e11ab706850b` | 32590490975 PASS | 32590490904 PASS |
| `archive-readiness-validate.yml` | org control | #252 | `fae7f6a1edc4d54dd67134773faf76acc87eae59` | 32590584716 PASS | 32590584788 PASS |
| `org-heartbeat.yml` | heartbeat worker | #253 | `2236df65a495975ca9bc7d9c8fad7d863934617f` | 32590794869 PASS | 32590794862 PASS |
| `org-heartbeat-watchdog.yml` | heartbeat worker, manual only | #254 | `c3256be218dbabdf4fb82e877e71d2884925c904` | 32590947641 PASS | 32590947607 PASS |
| `native-process-worker-canary.yml` | heartbeat worker | #255 | `856d1823283f3ade54ac95094d73ec149c245d74` | 32591051012 PASS | 32591050991 PASS |
| `external-timing-match-validation.yml` | heartbeat worker | #256 | `278299617d17a4f410b0ef0e2d1da1a609b67fc4` | 32591188347 PASS | 32591188133 PASS |
| `activate-host-self-attest-worker.yml` | heartbeat worker | #257 | `1240cc0087f5777b08c1913561d4b7125df74cbf` | 32591396135 PASS | 32591396122 PASS |

## Parity decisions

- Handoff rendering remains deterministic and must match the committed projection.
- Archive readiness retains its validator and unittest.
- Organization-heartbeat source validation moved to the stable heartbeat dispatcher; routine heartbeat/state/receipt persistence remains excluded from automatic main fanout.
- Watchdog diagnostics remain manual-only through `workflow_dispatch`.
- Native-process canary and host self-attest are terminal `COMPLETED` tasks with successor policy `NONE`; only retained evidence checks remain.
- External timing source/validation is complete/released; focused timing and fixed-cadence zero-authority checks remain. `.github#122` remains the live timing consumer.
- All seven consolidation heads passed both retained validator families before merge.

## Remaining workflow classes

The one non-dispatcher workflow now remaining are predominantly owner-sensitive and must not be deleted for denominator pressure alone:

```text
stegfin-early-adopter-contribution-validator-source.yml — active StegFin ownership
```

Next Healer action is owner reconciliation for one bounded surface, followed by consolidation/transfer/elimination only if validation parity and runtime non-interference are proven. Otherwise record `KEEP_STANDALONE_EXCEPTION` with technical necessity.

## 2026-08-26 test-lanes consolidation

The optional Test Lanes autolaunch task remains active, but its dedicated validation workflow did not need to remain standalone. The workflow-only binding assertions were promoted into the stable deterministic unittest suite and the standalone workflow was removed.

```text
removed: .github/workflows/test-lanes-autolaunch-validation.yml
coverage replacement: tests/test_test_lanes_autolaunch_binding.py
stable dispatcher: .github/workflows/heartbeat-worker-project.yml
runtime/autolaunch source changed: false
direct Test Lanes runner changed: false
credential/runtime authority effect: NONE
current workflow count: 3
remaining non-dispatchers: 1
```

## 2026-08-27 federation and MCP consolidation

Two additional owner-safe validation surfaces were consolidated into the stable heartbeat-worker dispatcher without altering their machine-owned runtime tasks:

```text
all-org-heartbeat-federation.yml -> REMOVED
  parity: tests/test_organization_federation_binding.py + existing federation suites
  issue #81 live topology task: STILL ACTIVE / MACHINE_OWNED

mcp-activation-binding-test.yml -> REMOVED
  parity: tests/test_sdk_mcp_activation_binding.py + tests/test_sdk_mcp_canonical_validation_worker.py
  SDK MCP exact sovereign artifact task: STILL HANDOFF_READY / MACHINE_OWNED

current workflow count: 3
stable dispatchers: 2
non-dispatchers: 6
automatic-push workflows: 7
PR-only workflows: 1
```

This is hosted-validation surface reduction only. It does not constitute federation coverage, MCP runtime validation, release, activation, or sovereign-node evidence.

## 2026-08-27 sovereign runtime consolidation

The three G18/sovereign-runtime hosted validation carriers were consolidated into the stable heartbeat-worker validation dispatcher after preserving their deterministic test coverage and automatic source-change validation.

```text
activate-sovereign-runtime-worker.yml -> REMOVED
sovereign-runtime-self-bootstrap.yml -> REMOVED
sovereign-ephemeral-console.yml -> REMOVED
stable dispatcher: heartbeat-worker-project.yml
G18 machine-owned runtime task: UNCHANGED / BLOCKED ON SOVEREIGN_NODE_DECLARATION_NOT_PRESENT
native runtime source: PRESERVED
runtime claim/fence: UNCHANGED
current workflow count: 3
non-dispatchers: 3
automatic-push workflows: 4
PR-only workflows: 1
```

This is validation-surface consolidation only. It does not fabricate sovereign-node evidence or complete G18.

## 2026-08-27 inference and StegGate consolidation

The hosted inference and StegGate validation workflows were consolidated into `heartbeat-worker-project.yml` after their unique boundary assertions were made normal deterministic tests.

```text
activate-ecosystem-chat-sovereign-inference-worker.yml -> REMOVED
steggate-heartbeat-integration.yml -> REMOVED
stable dispatcher: heartbeat-worker-project.yml
inference runtime task: UNCHANGED / LIVE EXECUTION PENDING
StegGate rendezvous task: UNCHANGED
current workflow count: 3
stable dispatchers: 2
non-dispatchers: 1
automatic-push workflows: 2
PR-only workflows: 1
```

The remaining non-dispatcher is `stegfin-early-adopter-contribution-validator-source.yml`, whose source lane is separately owner-bound. It must be reconciled with that canonical owner before removal or recorded as an explicit standalone exception.

## Site cost dependency — reconciled current state

GitHub billing evidence supplied during the Actions cost session identified `StegVerse-Labs/Site` as the largest observed Actions repository cost center. Canonical Site authority remains `StegVerse-Labs/Site/docs/ACTIONS_COST_CONTAINMENT_MIRROR_HANDOFF.md` / Site #268.

The earlier statement that the VA Claims Guide workflow was only a pending candidate is superseded. Site's canonical handoff records the VA Claims Guide cost repair as RELEASED (Site #428); Healer must not recreate that lane.

Current nonterminal Site dependencies relevant to Healer are:

1. **Thought Experiments B27** — source/native validation carrier exists, but exact live validation still depends on the sovereign scheduler receipt.
2. **VA governed surfaces deployment observer** — Site PR #473 merged as `b526c69a647b96cf8ee6e9e44aca0facc1d61241` after Handoff `32669715065`, Heartbeat `32669715039`, and Bootstrap `32669715040` PASS. Its six-hour schedule/writeback/artifact mechanics are removed, but the task remains `MERGED_AWAITING_TASK_SPECIFIC_MAIN_OBSERVATION`; see `StegVerse-Labs/Site/docs/VA_GOVERNED_SURFACES_DEPLOYMENT_ACTIONS_FANOUT_MIRROR_HANDOFF.md`.
3. **Executive Rhetoric Ledger sync migration** — Healer #39 / PR #40 installed the fixed local target on the existing sovereign scheduler. Exact head `aca5b7871e2720b0d56757e33fc2a22c10291136` passed Test Readiness `32670203077` / job `97269769966`; merge `ff3d9985b773d91dce0d90351a7a8a04a499c59b`. Source is `COMPLETE_RELEASED`; live execution is `MACHINE_OWNED_PENDING_SCHEDULER_RECEIPT`. Detailed authority: `docs/SITE_ERL_SOVEREIGN_SYNC_MIRROR_HANDOFF.md`.
4. **Site `validate.yml` trigger narrowing** — remains blocked by active Site claim `SITE-STEGFIN-IOS-LOCAL-WALLET-TRANSPORT-388-20260817`, whose current receipt is `SOURCE_AND_SITE_MERGED_CORRECTED_PUBLICATION_PROOF_PENDING` and `release_blocked=true`.

The required scheduler receipt remains:

`StegVerse-Labs/.github/receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`

Live inspection still reports it absent. `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` remains the single canonical scheduler lane; do not create a second scheduler or worker. Until the receipt proves the ERL target COMPLETE/PASS, Site's existing GitHub ERL sync carrier must remain for continuity.

## Upstream runtime dependency — corrected 2026-08-26

Heartbeat activation is terminal under the HB32 protocol anchor and does not block this hygiene lane. The historical iPhone HB30 capsule is already satisfied/superseded and requires **no current user action**.

The single remaining upstream execution dependency for `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` is the separate durable worker/runtime substrate:

```text
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
state: BLOCKED_SOVEREIGN_NODE_REQUIRED_NON_HEARTBEAT
receipt blocker: SOVEREIGN_NODE_DECLARATION_NOT_PRESENT
claim/fence: existing G18/fence18 machine-owned
next boundary: eligible StegVerse-owned/federated sovereign node + canonical native installer/verifier
current iPhone HB30 action: NONE
```

Do not create a second scheduler/runtime lane. Once the existing durable-runtime owner produces real sovereign-node execution evidence, consume it in the existing Healer scheduler lane and then evaluate ERL/B27 retirements.

## Completion gate

This hygiene goal is not complete. Three `.github` workflows remain; the single non-dispatcher is the active StegFin early-adopter validation source lane, Site cost work remains active, the sovereign scheduler has no live receipt, and count >2 cannot be accepted without explicit exception evidence.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
