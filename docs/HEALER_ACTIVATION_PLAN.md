# StegVerse-Healer Activation Plan

## Goal
Operate StegVerse-Healer as the sole scheduler and reusable repair authority for managed repositories, without requiring the user to identify or silence obsolete workflows manually.

## Activation target
A repository is fully Healer-managed when it can:
1. Preserve an accurate repo-local `*_MIRROR_HANDOFF.md`.
2. Call `StegVerse-Labs/StegVerse-Healer/.github/workflows/supercheck_core.yml@main` for repair.
3. Accept Healer dispatch through `.github/workflows/ingestion-orchestrator.yml`.
4. Keep all non-Healer workflows free of `on.schedule`.
5. Gate downstream work with `MASTER_INGESTION_ENABLED`.
6. Execute real repository adapters rather than placeholder steps.
7. Produce a successful execution receipt or an intentional no-op receipt.
8. Avoid failing when GitHub blocks PR creation by falling back to a repair branch.

## Central scheduling contract
Only `StegVerse-Labs/StegVerse-Healer` may host approved schedules for repositories listed in `registry/managed_repos.yml`.

The central path is:
1. `.github/workflows/healer_scheduler.yml`
2. `data/orchestrator_targets.json`
3. `app/dispatch_orchestrators.py`
4. target `.github/workflows/ingestion-orchestrator.yml`
5. target repository adapter

The audit path is `.github/workflows/quiet_enforcer.yml`.

## Universal downstream contract
Install `templates/universal_ingestion_orchestrator.yml` as `.github/workflows/ingestion-orchestrator.yml` in a target repository, then provide one executable adapter:
- `scripts/ingestion/run.sh`
- `scripts/ingestion/run.py`
- `scripts/orchestrate.sh`
- `scripts/orchestrate.py`

A target with no adapter is scaffolding and is not activation-complete.

## Legacy workflow contract
Use `templates/disabled_legacy_workflow.yml` only after:
1. reading the target handoff;
2. reconstructing the old workflow's purpose and dependencies;
3. mapping retained logic to the universal adapter;
4. recording the migration in the target handoff.

The stub has only `workflow_dispatch`, empty permissions, and a one-minute timeout.

## Current managed migration set
- `StegVerse-Labs/Site` — audit pending; first priority because of repeated CFP and sports ingestion failures.
- `StegVerse-Labs/SCW` — audit pending.
- `StegVerse-Labs/TV` — connected to reusable repair; scheduler migration pending.
- `StegVerse-Labs/CosDen` — audit pending.
- `StegVerse-Labs/Continuity` — audit pending.

## Authentication
`HEALER_GH_TOKEN` must be configured as a StegVerse-Healer repository secret with:
- Actions: read and write for target repositories;
- Contents: read for audit and discovery;
- access to every configured private target, when applicable.

No token value belongs in committed files.

## Validation sequence
1. Validate `data/orchestrator_targets.json` and compile `app/dispatch_orchestrators.py`.
2. Manually run `Healer Scheduler (Single Clock)` with one target scope.
3. Confirm the downstream orchestrator accepted the dispatch.
4. Confirm enabled targets executed their real adapter.
5. Confirm disabled targets emitted an intentional no-op.
6. Remove or stub superseded schedules.
7. Run `Quiet Enforcer` and obtain zero unauthorized schedules.
8. Update the target handoff and registry status with commit and run evidence.

## Remaining build tasks
1. Scan target repos in the registry order defined by the handoff.
2. Add machine-readable workflow inventories and migration maps.
3. Add stable audit receipt schema for downstream StegCore ingestion.
4. Add Healer self-validation.
5. Add controlled auto-fix PR generation only after audit-only behavior is proven.
6. Add failure backoff and notification deduplication to prevent Healer itself becoming noisy.

## Handoff condition
The migration can be continued without this conversation when the Healer handoff, activation plan, registry, target handoffs, adapter mappings, and validation receipts contain all ownership and continuation information.

## Done condition
Activation is complete when every registered target is dispatchable through Healer, has no unauthorized schedules, uses a real adapter, preserves a current handoff, and leaves durable success or intentional-no-op evidence without manual reconstruction.
