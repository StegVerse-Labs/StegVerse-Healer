# StegVerse-Healer Mirror Handoff

## Current goal
Continue building until task handoff and task completion can be handled by ecosystem management without manual intervention.

## Active source of truth
StegVerse-Healer is the central reusable healing repo for YAML and workflow consistency across StegVerse repos.

## Current state
- `actions/yaml-corrector/action.yml` normalizes YAML line endings, tabs, final newlines, creates `data/summary/chainlog.jsonl`, and emits healer reports.
- `.github/workflows/supercheck_core.yml` is reusable through `workflow_call`.
- Caller repositories can invoke SuperCheck Core and receive either a direct commit, PR creation when `HEALER_PAT` exists, or a pushed repair branch when no PAT is available.
- `registry/managed_repos.yml` now records `StegVerse-Labs/TV` as the first connected managed repo.
- `docs/HEALER_ACTIVATION_PLAN.md` defines the activation target and done condition.

## Connected repositories
- `StegVerse-Labs/TV` via `github/workflows/tv_self_heal.yml`.

Note: displayed `github/...` paths omit the leading dot. Actual paths begin with `.github/...`.

## Next activation tasks
1. Validate TV Self-Heal after the latest central workflow changes.
2. Add stronger manifest-specific checks once a tool-safe implementation path is available.
3. Add repo-specific policy packs for TV, Site, Publisher, and future core repos.
4. Add `HEALER_PAT` to target repos when PR creation is desired.
5. Add self-validation for StegVerse-Healer so the healer can manage its own drift.
6. Extend `registry/managed_repos.yml` as additional repos are connected.

## Handoff standard
Each StegVerse repo should maintain a repo-specific `*_MIRROR_HANDOFF.md` file that records current goal, current source of truth, active workflows, and next activation tasks.

## Done condition
The repo is ready for activation when target repos can call the reusable healer and receive non-failing repair branches or PRs without manual reconstruction.
