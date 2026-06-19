# StegVerse-Healer Activation Plan

## Goal
Continue building until repository-level repair can be handled by StegVerse-Healer without manual reconstruction by the user.

## Activation target
A target repository is considered healer-managed when it can:

1. Call `StegVerse-Labs/StegVerse-Healer/.github/workflows/supercheck_core.yml@main`.
2. Normalize YAML files and generate `data/summary/heal_report.json`.
3. Avoid failing when GitHub blocks PR creation.
4. Push a repair branch when no `HEALER_PAT` is present.
5. Open a repair PR when `HEALER_PAT` is present.
6. Preserve a repo-local `*_MIRROR_HANDOFF.md` file.

## Current managed repository
- `StegVerse-Labs/TV`

## Current operating mode
- Default: branch repair mode when `HEALER_PAT` is absent.
- Optional: PR repair mode when `HEALER_PAT` is added.
- Optional: direct commit mode only when `direct_commit: true` is set by a caller repo.

## Required target repo caller
Each managed repo should include a caller workflow equivalent to:

```yaml
name: Repo Self-Heal
on:
  workflow_dispatch: {}
  push:
    branches: ["main"]
    paths:
      - ".github/workflows/**/*.yml"
      - ".github/workflows/**/*.yaml"
      - "tv_manifest.yml"
      - "roles_templates/**"
      - "schema/**"
      - "scripts/**"
permissions:
  contents: write
  pull-requests: write
jobs:
  heal:
    uses: StegVerse-Labs/StegVerse-Healer/.github/workflows/supercheck_core.yml@main
    secrets: inherit
    with:
      direct_commit: false
      paths: ".github/workflows/**/*.yml .github/workflows/**/*.yaml tv_manifest.yml roles_templates/**/*.yml schema/**/*.yml"
```

## Next build tasks
1. Add stronger repo-specific validation packs.
2. Add machine-readable registry of managed repos.
3. Add stale dependency detection for referenced workflow files, scripts, manifests, schemas, and role templates.
4. Add stable report schema for downstream StegCore ingestion.
5. Add test caller inside StegVerse-Healer for self-validation.

## Handoff condition
Task handoff is capable of ecosystem management when StegVerse-Healer can discover target repo drift, produce a repair branch or PR, and leave a report plus handoff record without requiring the user to identify broken YAML manually.
