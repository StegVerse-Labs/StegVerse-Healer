# Healer Self-Validation Next Steps

## Purpose
This note preserves the next build target for StegVerse-Healer: the healer must validate itself before it becomes the ecosystem-level healing authority.

## Current blocker
A direct self-test workflow was not committed in the current pass. The next implementation should add a workflow that checks the healer repo using the same standards it applies to managed repos.

## Required behavior
- Run manually.
- Run on pushes to workflow, action, registry, and docs handoff paths.
- Produce `data/summary/heal_report.json`.
- Avoid failing when no pull-request token is available.
- Push a repair branch or open a PR depending on available credentials.

## Intended workflow path
Actual path: `.github/workflows/healer_self_test.yml`
Displayed path without leading dot: `github/workflows/healer_self_test.yml`

## Done condition
StegVerse-Healer is self-validation ready when the self-test workflow can run without requiring the user to reconstruct broken YAML or workflow dependencies.
