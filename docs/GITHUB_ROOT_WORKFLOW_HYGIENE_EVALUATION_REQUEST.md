# StegVerse-Healer Evaluation Request — StegVerse-Labs/.github Workflow Hygiene

Date: 2026-08-22
Target repository: `StegVerse-Labs/.github`
Evaluation owner requested: `StegVerse-Labs/StegVerse-Healer`
Source lane: Actions fanout/cost repair
Decision state: **EVALUATION REQUESTED — NO CONSOLIDATION AUTHORIZED BY THIS DOCUMENT**

## Why this is being transferred to Healer

Repository hygiene and workflow-surface minimization are responsibilities of StegVerse-Healer. The Actions fanout repair lane in `StegVerse-Labs/.github` identified workflow proliferation while narrowing paid CI triggers, but it should not become the permanent hygiene authority or independently delete/consolidate repository workflow surfaces.

This document therefore transfers the **reasoning and evidence for evaluation**, not a completion claim and not deletion authority.

## Governing constraints

- Primary runtime/control plane: StegVerse.
- Third-party execution is fallback-only when required and admitted.
- Credential authority: TV/TVC only.
- No NON-TV/TVC secret/token may be introduced.
- GitHub token production/runtime authority: NONE.
- GitHub Actions may provide credential-clean validation where technically necessary, but never sovereign runtime/control-plane authority.
- Render must not be used.
- Source completeness, workflow success, handoff, assignment, readiness, or machine ownership must not be treated as runtime activation or completion.
- Existing active worker/runtime owners must not be displaced by workflow cleanup.

## Current evidence from StegVerse-Labs/.github

The root repository currently has 18 repository-authored workflow files. Current fanout classification records 12 automatic-push surfaces and 6 PR/manual-only surfaces after the latest containment changes.

A prior fanout-repair audit found that the workflow surface can be divided into two broad stable validation domains:

1. Organization/control-plane validation, currently anchored by `.github/workflows/org-control-plane-validate.yml`.
2. Heartbeat/runtime/worker validation, currently anchored by `.github/workflows/heartbeat-worker-project.yml`.

Those two workflows already provide properties useful for stable dispatcher-style consolidation: credential-clean source acquisition, `permissions: {}`, source/schema/script/test validation, broader pull-request validation, manual dispatch, concurrency containment, and explicit non-authorizing assertions.

## 18 → 2 hypothesis for Healer to evaluate

The working hypothesis is that the root workflow surface may be reducible from 18 files to two stable entry surfaces **without removing underlying validation capability**, if Healer independently confirms parity and owner safety.

Possible stable end state:

- `org-control-plane-validate.yml` — organization/control/config/schema dispatcher/validator.
- `heartbeat-worker-project.yml` — heartbeat/runtime/worker dispatcher/validator.

All other workflow-specific commands would either be invoked behind one of those two stable dispatchers with path-aware gating, remain available through explicit/manual validation commands where intentionally expensive, move recurring or operational behavior to StegVerse-Healer / sovereign workers where GitHub-hosted execution is not technically necessary, or remain standalone only when Healer records an evidence-backed technical exception.

This is a hypothesis, not an authorization to delete sixteen files.

## Candidate consolidation set

The following appear suitable for Healer evaluation as consolidation/transfer candidates because their present role is validation, diagnostics, or source-bound testing rather than sovereign runtime authority:

- `.github/workflows/archive-readiness-validate.yml`
- `.github/workflows/org-handoff-render.yml`
- `.github/workflows/org-heartbeat-watchdog.yml`
- `.github/workflows/activate-host-self-attest-worker.yml`
- `.github/workflows/external-timing-match-validation.yml`
- `.github/workflows/native-process-worker-canary.yml`
- `.github/workflows/org-heartbeat.yml`
- `.github/workflows/steggate-heartbeat-integration.yml`
- `.github/workflows/test-lanes-autolaunch-validation.yml`

The following require explicit active-owner reconciliation before Healer removes or absorbs their standalone workflow surfaces:

- `.github/workflows/activate-ecosystem-chat-sovereign-inference-worker.yml`
- `.github/workflows/activate-sovereign-runtime-worker.yml`
- `.github/workflows/all-org-heartbeat-federation.yml`
- `.github/workflows/mcp-activation-binding-test.yml`
- `.github/workflows/sovereign-runtime-self-bootstrap.yml`
- `.github/workflows/sovereign-ephemeral-console.yml`
- `.github/workflows/stegfin-early-adopter-contribution-validator-source.yml`

The two proposed stable anchors themselves are not deletion candidates in this hypothesis:

- `.github/workflows/org-control-plane-validate.yml`
- `.github/workflows/heartbeat-worker-project.yml`

## Required Healer evaluation

For every current `.github` workflow, Healer should independently classify it as one of:

- `KEEP_STABLE_ENTRY_SURFACE`
- `KEEP_STANDALONE_EXCEPTION`
- `CONSOLIDATE_INTO_ORG_CONTROL_VALIDATOR`
- `CONSOLIDATE_INTO_HEARTBEAT_WORKER_VALIDATOR`
- `TRANSFER_TO_STEGVERSE_HEALER_OR_WORKER`
- `ELIMINATE_AFTER_PARITY_PROOF`
- `BLOCKED_ACTIVE_OWNER`

Any count above two should be retained only with explicit technical necessity and evidence.

## Safety requirements before deletion

A specialized workflow must not be deleted merely because another workflow can run Python or shell commands. Before removal, Healer should prove:

1. source/schema/config/test trigger coverage is preserved or intentionally superseded;
2. pull-request coverage is preserved where it provides meaningful pre-merge protection;
3. intentionally expensive checks remain manually invocable where appropriate;
4. validation commands/tests formerly executed by the workflow still execute through the retained surface or a local Healer/worker path;
5. no active claim, fence, lease, scheduler, wallet, route, provider, deployment, or runtime authority is reassigned by cleanup;
6. no GitHub credential or NON-TV/TVC secret/token is introduced;
7. routine heartbeat carrier state, receipts, observations, projections, events, handoffs, and cost persistence do not regain paid hosted fanout;
8. exact-current-main validation passes after the consolidation tranche;
9. final workflow count and exceptions are recorded in Healer's canonical hygiene evidence.

## Existing policy lineage

`StegVerse-Labs/.github#167` defines the preferred workflow target as 0/1/2 stable workflow entry surfaces where technically sufficient, with counts above two requiring explicit evidence-backed exceptions.

`StegVerse-Labs/.github#168` records workflow-surface minimization as a durable goal and requires preservation of necessary capability, StegVerse-owned recurring execution, TV/TVC credential authority, and durable final-count evidence.

These records provide policy context. This PR asks StegVerse-Healer to evaluate and, if admitted, own the actual cleanup from here.

## Acceptance for this PR

This PR is complete when the reasoning is available inside StegVerse-Healer for canonical evaluation. It does **not** claim that 18 → 2 has been approved, any workflow has been safely removed, validation parity has been demonstrated, Healer's sovereign scheduler is live merely because source exists, or any product/runtime goal is activated.

A subsequent Healer-owned task/issue/PR should carry any accepted implementation and evidence to terminal completion.
