# StegVerse-Healer Mirror Handoff

## Canonical state

```text
repository: StegVerse-Labs/StegVerse-Healer
branch: main
primary_goal: HEALER-TV-TVC-NO-GITHUB-TOKEN-DISPATCH-001
credential_authority: TV/TVC
non_tv_tvc_secret_or_token_allowed: false
github_token_production_authority: NONE
github_actions_production_role: NONE
heartbeat_owner: StegVerse-Labs/.github G18
ordinary_scheduler_owner: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
wallet_signing_and_broadcast: USER_ONLY
state: SOURCE_CONTROL_RELEASED_LIVE_SCHEDULER_ACTIVATION_MACHINE_OWNED
```

Canonical organization/runtime continuations are `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md`, `StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json`, and `StegVerse-Labs/.github/handoffs/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`.

## Released source integrations

- `HEALER-G18-PRE-CARRIER-ASSIST-001`: PR #5 merge `571b6a86737173a89235110294025f9808695531`.
- `HEALER-SITE-MARKETPLACE-COINBASE-LOCAL-OBSERVER-001`: PR #7 merge `ecf96188348c097dfdea3ce55c47db9dff6e84ef`.
- `HEALER-SITE-MARKETPLACE-PROJECTION-LOCAL-IMPORT-001`: COMPLETE_RELEASED for source/integration.

Projection-import evidence:

```text
Healer issue: #8
Healer PR #9 merge: b280025ed0007d10fdbb377cdf77cfd74443565c
Healer Test Readiness: 32045128811 SUCCESS
fixed target: marketplace-coinbase-local-projection-import
Site PR #352 head: 1706f22da79fd8e8c90cbad4d9ff5f088410142d
Site PR #352 merge: 218fee91a7d2214fec328f74247e079292c45ce0
Site Bootstrap: 32050796944 SUCCESS
Site Handoff: 32050796941 SUCCESS
Ecosystem Heartbeat: 32050797014 SUCCESS
StegFin projection: 32050785197 SUCCESS
```

The fixed target uses already-materialized Site and `GCAT-BCAT-Engine/Publisher` roots through `STEGVERSE_REPO_ROOTS_JSON`. Site now consumes Publisher evidence locally, has no `raw.githubusercontent.com` acquisition path, refuses GitHub/project credential environments, and fails closed when local evidence is absent. No second scheduler/heartbeat or GitHub/PAT/provider/wallet credential path is introduced.

## Activation boundary

Source/CI integration is complete, but ordinary live Healer execution remains `MACHINE_OWNED`. Activation requires `receipts/healer-sovereign-scheduler/SHWP-HEALER-SOVEREIGN-SCHEDULER-001.json`. No source merge, CI run, chat session, GitHub Action, or Render path substitutes for that receipt.

The Marketplace projection-import integration is archive-safe as a chat-owned implementation task. Broader Site #268 cleanup and machine-owned runtime activation continue through their canonical owners.
