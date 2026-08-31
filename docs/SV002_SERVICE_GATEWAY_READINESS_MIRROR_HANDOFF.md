# SV002 Service Gateway Readiness Mirror Handoff

Updated: 2026-08-29
Repository: StegVerse-Labs/StegVerse-Healer
Issue: #49
Branch: fix/sv002-gateway-readiness-49

## Source of truth

This file is the current handoff and task source of truth for the bounded StegVerse-002 observation readiness verification inside the existing sovereign Service Gateway activation target.

## Scope

When `STEGVERSE_SV002_OBSERVE_ENABLED=true`, Healer must not report the shared Gateway target COMPLETE merely because the Coinbase readiness surface is healthy. It must additionally observe the deployed Gateway's own:

```text
GET /intr/sv002-observe/readiness
```

and require the exact authority-neutral projection:

```text
schema: stegverse.service-gateway.sv002-observation-readiness/v1
enabled: true
loopback_upstream_configured: true
state: READY
transport: InTr
credential_authority: TV/TVC
gateway_receipt_authority: false
gateway_experiment_authority: false
authority_effect: NONE
```

This verifies Gateway configuration/readiness only. It does not establish the resident SV002 receiver process, public Internet route, valid external observer round trip, principal experiment execution, or Master Records custody.

## Existing owners retained

- shared Service Gateway implementation: StegVerse-org/LLM-adapter
- SV002 receiver/runtime task: StegVerse-Labs/.github#462 / SHWP-SV002-PUBLIC-OBSERVATION-RUNTIME-001
- credential/TLS authority: TV/TVC
- resident scheduler: SHWP-HEALER-SOVEREIGN-SCHEDULER-001
- custody/reconstruction: master-records/orchestration

No second Gateway, scheduler, heartbeat, TLS authority, or credential surface may be created.

## Files

- `app/coinbase_stegdeploy_gateway.py`
- `tests/test_coinbase_stegdeploy_gateway.py`
- `docs/SV002_SERVICE_GATEWAY_READINESS_MIRROR_HANDOFF.md`

## Remaining installation / integration destinations

- resident Healer scheduler execution -> StegVerse-Labs/.github sovereign runtime
- persistent SV002 receiver -> StegVerse-Labs/.github
- public Gateway route/TLS -> StegVerse-org/LLM-adapter + StegVerse-Labs/TVC
- Site browser observation -> StegVerse-Labs/Site
- experiment artifacts -> StegVerse-002/micro-node-runtime
- custody/reconstruction -> master-records/orchestration

## Completion

Source completion requires deterministic tests, repository validation, merge to main, and issue reconciliation. Runtime activation remains separately evidence-gated.


## Universal InTr public-profile runtime binding — 2026-08-31

Public observation from `StegVerse-Labs/Site#860` established that `https://stegverse.org/intr/profile` returned HTTP 404 on eight independent attempts. LLM-adapter source already contains the route through PR #244 / merge `49676d20cff32ee346f22cfd79726b0127d80b33`, so the observed failure is runtime publication/binding drift rather than missing Gateway router source.

The fixed sovereign Gateway handler now consumes the existing resident Universal InTr route projection:

```text
STEGVERSE_HIL_INTR_ENABLED=true
STEGVERSE_HIL_INTR_UPSTREAM=http://127.0.0.1:8765/intr/materialization
```

When enabled it requires:
- the exact canonical same-host upstream;
- local LLM-adapter HEAD to contain merge `49676d20cff32ee346f22cfd79726b0127d80b33` as an ancestor;
- `/intr/materialization/readiness` to report READY, event-triggered, G18-independent, TV/TVC-bound, no GitHub authority, and no receipt/execution/custody authority.

The binding is configuration/transport only. Local readiness remains distinct from public HTTPS observation. A source merge or local READY result does not establish `https://stegverse.org/intr/profile`; that route must be re-observed independently after authentic resident publication.
