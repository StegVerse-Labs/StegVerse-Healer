# Healer GitHub Failure Mailbox

This directory implements a StegVerse-Healer-owned failure incident engine derived from the deterministic replay/ledger pattern used by `StegVerse-Labs/ara-admissibility-interop` deployment mailbox monitoring, but with different semantics.

## Purpose

The ARA deployment monitor answers: "is this governed deployment notification a new verification candidate, a duplicate, or a conflicting replay?"

This Healer engine answers: "which underlying failure incident does this GitHub notification observe, how often has it recurred, what repositories/workflows are affected, what lifecycle state is the incident in, and what evidence is eligible for cleanup after durable resolution?"

An email is an observation, not an incident.

```text
GitHub failure notification
        |
        v
normalize observation
        |
        v
deterministic failure signature
        |
        +--> existing incident -> append observation / update frequency
        |
        +--> new incident -> allocate inventory number
        |
        v
classify failure family + propagation hints
        |
        v
OPEN -> TRIAGED -> REPAIRING -> RETESTING -> RESOLVED
                       |
                       +--> UNABLE_TO_REPAIR -> SANDBOX_REQUIRED
                       |
                       +--> UNRESOLVED
```

## Non-authority boundary

- GitHub/email observations do not grant repository, runtime, release, deployment, credential, wallet, or repair authority.
- The engine never treats a failed workflow as proof of a runtime failure without corroborating evidence.
- `UNABLE_TO_REPAIR` / `IMPOSSIBLE_TO_REPAIR` maps to `SANDBOX_REQUIRED`; it must not generate endless retries of the same repair path.
- Resolved notification cleanup is emitted as an archive plan only. A mailbox adapter with explicit authority must perform the actual archive action.
- Credential authority remains TV/TVC. No GitHub token or NON-TV/TVC secret/token is required by this engine.
- Heartbeat progression is unrelated to notification arrival, failure state, or incident lifecycle.

## Deterministic identity

The engine derives a failure signature from normalized fields:

```text
repository
workflow
job/check
branch-or-pr
failure_class
failure_fingerprint
```

Commit SHA and message identity remain observation evidence but are intentionally not always part of the incident identity so repeated occurrences of the same defect across commits can accumulate into one history.

Each incident receives a stable inventory ID of the form `GF-000001` in creation order. The ledger preserves the identity-to-ID mapping.

## Primary outputs

`incident_engine.py` maintains a JSON ledger containing:

- incident inventory number;
- first/last seen timestamps;
- repository/workflow/job;
- normalized failure class and fingerprint;
- occurrence count and unique message count;
- commit/branch/PR history;
- lifecycle state;
- repair and sandbox references;
- neighboring repository observations and temporal correlation candidates;
- resolution evidence;
- notification IDs eligible for archive after resolution.

The summary emitted on each run includes failure-family frequency, repository frequency, repeated incidents, unresolved incidents, sandbox-required incidents, and archive candidates.

## Transport contract

Mailbox transport is intentionally separate. A TV/TVC-authorized adapter should convert a GitHub notification into the normalized JSON observation accepted by `incident_engine.py` and should consume the engine's archive plan only after `RESOLVED` is durably evidenced.

The existing sovereign Healer scheduler remains the only ordinary scheduler owner. Do not add an hourly GitHub Actions workflow for this engine.
