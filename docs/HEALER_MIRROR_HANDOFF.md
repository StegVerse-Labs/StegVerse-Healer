# StegVerse-Healer Mirror Handoff

## Current goal
Make `StegVerse-Labs/StegVerse-Healer` the sole scheduling authority for managed StegVerse repositories, while downstream repositories expose quiet, manual/event-driven orchestrators and retain durable repair continuity.

## Active source of truth
This file, `docs/HEALER_ACTIVATION_PLAN.md`, and `registry/managed_repos.yml` jointly define current ownership, scope, blockers, and continuation requirements.

## Decisions now durable
1. `StegVerse-Healer` is the only managed repository permitted to contain approved `on.schedule` triggers.
2. Downstream managed repositories must use `.github/workflows/ingestion-orchestrator.yml` with `workflow_dispatch` and no schedule.
3. Downstream execution is gated by the repository variable `MASTER_INGESTION_ENABLED`.
4. Obsolete workflows are replaced in place by `templates/disabled_legacy_workflow.yml` or deleted after their logic is migrated and history is preserved in Git.
5. The scheduler reads `data/orchestrator_targets.json`; target duplication inside workflow YAML is prohibited.
6. `quiet_enforcer.yml` audits configured target repositories for unauthorized schedules.

## Current implemented files
- `.github/workflows/healer_scheduler.yml` — sole hourly clock; validates configuration and invokes the dispatcher.
- `.github/workflows/quiet_enforcer.yml` — daily unauthorized-schedule audit.
- `app/dispatch_orchestrators.py` — config-driven cross-repository workflow dispatcher.
- `data/orchestrator_targets.json` — active dispatch target list.
- `templates/universal_ingestion_orchestrator.yml` — downstream event-driven orchestrator contract with adapter discovery.
- `templates/disabled_legacy_workflow.yml` — manual-only, one-minute legacy workflow tombstone.
- `actions/yaml-corrector/action.yml` — YAML normalization and healer reporting.
- `.github/workflows/supercheck_core.yml` — reusable repair workflow.

## Managed migration scope
The initial single-scheduler migration covers:
- `StegVerse-Labs/Site`
- `StegVerse-Labs/SCW`
- `StegVerse-Labs/TV`
- `StegVerse-Labs/CosDen`
- `StegVerse-Labs/Continuity`

`registry/managed_repos.yml` is the authoritative expansion point for additional repositories.

## Discovered tasks and blockers
### Required downstream work
1. Read each target repository's `*_MIRROR_HANDOFF.md` before mutation; create it first when absent.
2. Inventory every `.github/workflows/*.yml` and `.yaml` file, including schedules, cross-repo dispatches, reusable calls, and required scripts.
3. Classify each automatic workflow as retained logic, migrated logic, disabled legacy logic, or prohibited duplicate schedule.
4. Install `.github/workflows/ingestion-orchestrator.yml` from the universal template and adapt repository scripts to one supported entrypoint:
   - `scripts/ingestion/run.sh`
   - `scripts/ingestion/run.py`
   - `scripts/orchestrate.sh`
   - `scripts/orchestrate.py`
5. Replace obsolete workflow contents with the disabled stub only after recording the original path and migration mapping in the repo handoff.
6. Remove unauthorized schedules after confirming Healer dispatch coverage.

### Authentication blocker
Cross-repository dispatch and private-repository auditing require `HEALER_GH_TOKEN` with repository access and Actions read/write plus Contents read. The token value is never stored in this repository; it must exist as a repository secret.

### Validation requirements
- `healer_scheduler.yml` validates JSON and Python syntax before dispatch.
- Each configured target must accept `workflow_dispatch` for `ingestion-orchestrator.yml` on its configured ref.
- `quiet_enforcer.yml` must report zero unauthorized schedules after migration.
- Downstream repositories must produce an intentional no-op when their master switch is disabled.
- Existing business logic must be mapped to a real adapter; placeholder-only success is not activation.

## Ownership
- Central scheduler, templates, registry, and audit policy: `StegVerse-Labs/StegVerse-Healer`.
- Repository-specific logic and handoff accuracy: each target repository, coordinated through Healer.
- Pending secret installation: repository/organization administrator.

## Permitted continuation scope
A continuation session may:
- inspect registered target repositories;
- update or create their mirror handoffs;
- install the universal orchestrator;
- migrate retained workflow logic into adapters;
- disable obsolete automatic triggers;
- update the registry with verified status and evidence;
- validate dispatch and quiet-enforcer results.

It must not blindly disable workflows whose purpose, dependencies, and replacement path have not been reconstructed.

## Next activation tasks
1. Scan `Site`, then `SCW`, `TV`, `CosDen`, and `Continuity` in that order because Site generated the largest observed failure volume.
2. Record concrete workflow inventories and script entrypoints in each repo handoff.
3. Install or adapt the universal orchestrator in each target.
4. Migrate and then quiet obsolete scheduled workflows.
5. Verify `HEALER_GH_TOKEN` availability through a controlled manual scheduler run.
6. Run the quiet enforcer and record a zero-violation receipt.
7. Add StegVerse-Healer self-validation and stable machine-readable audit receipts.

## Release and ecosystem propagation
When the single-scheduler migration reaches release readiness, tag StegVerse-Healer and create verification tasks for relevant policy or integration updates in:
- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `StegVerse-Labs/stegguardian-wiki`

## Done condition
Activation is complete when all registered targets are dispatchable through Healer, contain no unauthorized schedules, use real repository adapters rather than scaffolding, preserve repo-local handoffs, and produce non-failing execution or intentional no-op receipts without manual reconstruction.
