"""Task Registry disposition invariant for every non-ALLOW record Healer produces.

ECOSYSTEM_STATE_TRANSITION_DISPOSITION_INVARIANT: no bare BLOCKED. Any record
whose state/disposition is not an ALLOW (BLOCKED, FAILED, FAIL_CLOSED, DENY, ...)
carries the six fields below. An effect that was not observed is recorded as
consequence_observation NOT_AUTHENTICALLY_OBSERVED plus a
reconciliation_entrypoint; no external machine is awaited or polled, and
destination liveness is never a transition predicate.

Standard library only; importable both as ``app.disposition`` and, when a
module runs as ``python app/<module>.py``, as ``disposition``.
"""
from __future__ import annotations

DEFAULT_OWNING_EXISTING_GOAL = "LLMA-DECLARED-PATH-CONFORMANCE-368"
DEFAULT_NEXT_ATTEMPT = "rerun the Healer target once the named repair is in place"
NOT_AUTHENTICALLY_OBSERVED = "NOT_AUTHENTICALLY_OBSERVED"
DISPOSITION_FIELDS = (
    "failure_code",
    "failed_predicate",
    "required_evidence_or_repair",
    "retry_entrypoint",
    "owning_existing_goal",
    "next_attempt",
)


def non_allow(
    failure_code: str,
    failed_predicate: str,
    repair: str,
    *,
    retry_entrypoint: str,
    owning_existing_goal: str = DEFAULT_OWNING_EXISTING_GOAL,
    next_attempt: str = DEFAULT_NEXT_ATTEMPT,
) -> dict[str, str]:
    """The six fields every non-ALLOW carries; spread with ``**non_allow(...)``."""
    return {
        "failure_code": str(failure_code),
        "failed_predicate": failed_predicate,
        "required_evidence_or_repair": repair,
        "retry_entrypoint": retry_entrypoint,
        "owning_existing_goal": owning_existing_goal,
        "next_attempt": next_attempt,
    }


def exception_failure_code(exc: BaseException, fallback: str) -> str:
    """A code for a caught exception: its UPPER_SNAKE prefix when it carries one, else ``fallback``."""
    prefix = str(exc).split(":", 1)[0].strip()
    if prefix and prefix.replace("_", "").isalnum() and prefix.upper() == prefix and "_" in prefix:
        return prefix
    return fallback


def unobserved_consequence(reconciliation_entrypoint: str) -> dict[str, str]:
    """Record an effect that was not observed without awaiting any machine."""
    return {
        "consequence_observation": NOT_AUTHENTICALLY_OBSERVED,
        "reconciliation_entrypoint": reconciliation_entrypoint,
    }


def missing_disposition_fields(record: dict) -> list[str]:
    """Names of the six fields that are absent or empty on ``record``."""
    return [name for name in DISPOSITION_FIELDS if not str(record.get(name) or "").strip()]
