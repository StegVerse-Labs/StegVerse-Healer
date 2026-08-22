# Healer .github Workflow Hygiene Mirror Handoff

Updated: 2026-08-22
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
18 workflow files
12 automatic-push
6 PR/manual-only
```

Current target-repository evidence:

```text
11 workflow files
8 automatic-push
3 PR/manual-only
7 standalone workflows removed with parity proof
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

The nine non-dispatcher workflows now remaining are predominantly owner-sensitive and must not be deleted for denominator pressure alone:

```text
activate-ecosystem-chat-sovereign-inference-worker.yml — active owner #60
activate-sovereign-runtime-worker.yml — active durable-runtime owner #59
a ll-org-heartbeat-federation.yml — owner #81
mcp-activation-binding-test.yml — active MCP ownership
sovereign-ephemeral-console.yml — durable-runtime/G18 ownership
sovereign-runtime-self-bootstrap.yml — #59/#65 ownership
stegfin-early-adopter-contribution-validator-source.yml — active StegFin ownership
steggate-heartbeat-integration.yml — active rendezvous handoff remains HANDOFF_READY
test-lanes-autolaunch-validation.yml — active machine-owned test-lane task
```

(Note: `a ll-org-heartbeat-federation.yml` above denotes the actual `all-org-heartbeat-federation.yml`; spacing is prose-only and carries no path authority.)

Next Healer action is owner reconciliation for one bounded surface, followed by consolidation/transfer/elimination only if validation parity and runtime non-interference are proven. Otherwise record `KEEP_STANDALONE_EXCEPTION` with technical necessity.

## Site cost dependency

GitHub billing evidence supplied 2026-08-22 identified `StegVerse-Labs/Site` as the largest observed Actions repository cost center. Site B27 already owns retirement of the hourly Thought Experiments workflow but remains waiting for the sovereign Healer scheduler receipt; `SHWP-HEALER-SOVEREIGN-SCHEDULER-001` is still `HANDOFF_READY`. GitHub CI cannot substitute.

A separate Site VA-guide workflow is a proven cost candidate but requires a distinct Site pre-work claim before mutation.

## Completion gate

This hygiene goal is not complete. Eleven workflows remain, nine are not yet terminally classified, Site cost work remains active, and count >2 cannot be accepted without explicit exception evidence.

Current status: `DO NOT ARCHIVE THIS SESSION — UNIQUE ACTIVE WORK REMAINS.`
