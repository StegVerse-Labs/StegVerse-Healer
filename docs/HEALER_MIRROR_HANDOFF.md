# StegVerse-Healer Mirror Handoff

## Current goal
Continue building until task handoff and task completion can be handled by ecosystem management without manual intervention.

## Active source of truth
StegVerse-Healer is the central reusable healing repo for YAML/workflow consistency across StegVerse repos.

## Current state
- `actions/yaml-corrector/action.yml` normalizes YAML line endings, tabs, final newlines, creates `data/summary/chainlog.jsonl`, and emits healer reports.
- `.github/workflows/supercheck_core.yml` is reusable through `workflow_call`.
- Caller repositories can invoke SuperCheck Core and receive either a direct commit, PR creation when `HEALER_PAT` exists, or a pushed repair branch when no PAT is available.

## Next activation tasks
1. Add stronger manifest-specific checks once tool-safe code path is available.
2. Add repo-specific policy packs for TV, Site, Publisher, and future core repos.
3. Add HEALER_PAT to target repos when PR creation is desired.
4. Add machine-readable handoff index once multiple repos are connected.

## Handoff standard
Each StegVerse repo should maintain a repo-specific `*_MIRROR_HANDOFF.md` file that records current goal, current source of truth, active workflows, and next activation tasks.

## Done condition
The repo is ready for activation when target repos can call the reusable healer and receive non-failing repair branches or PRs without manual reconstruction.
