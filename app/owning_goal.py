"""Derive a Healer target's owning goal from the canonical task registry, without guessing.

Order: a target's declared ``canonical_owner`` wins; otherwise exactly one
canonical task record whose ``targets.repositories`` (or ``repository``) names
the target repository AND whose ``targets.components`` names the target's
workflow (with or without ``.yml``), one of its aliases, or its
``canonical_path``; otherwise no owner is inferred and a six-field refusal is
returned. Repository overlap alone is never a mapping, since one repository is
named by many unrelated tasks.

The registry is read only from the locally materialized
``StegVerse-Labs/.github`` root listed in STEGVERSE_REPO_ROOTS_JSON
(``data/canonical-task-registry.json`` tasks plus
``data/canonical-task-records/*.json``). Nothing is fetched over the network.

Standard library only; importable as ``app.owning_goal`` or ``owning_goal``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from app.disposition import DEFAULT_OWNING_EXISTING_GOAL, non_allow
except ImportError:  # executed from app/ as a top-level module
    from disposition import DEFAULT_OWNING_EXISTING_GOAL, non_allow

LABS_REPOSITORY = "StegVerse-Labs/.github"
REGISTRY_PATH = "data/canonical-task-registry.json"
RECORDS_DIR = "data/canonical-task-records"
REGISTRY_SOURCE = "CANONICAL_TASK_REGISTRY"
FAILED_PREDICATE = "TARGET_OWNING_GOAL_DECLARED_OR_REGISTERED"
NOT_IN_REGISTRY = "TARGET_OWNING_GOAL_NOT_IN_REGISTRY"
AMBIGUOUS_IN_REGISTRY = "TARGET_OWNING_GOAL_AMBIGUOUS_IN_REGISTRY"
REGISTRY_NOT_MATERIALIZED = "CANONICAL_TASK_REGISTRY_NOT_MATERIALIZED"
DEFAULT_RETRY_ENTRYPOINT = "python -m app.sovereign_scheduler"


def load_registry_records(labs_root: Path | None) -> list[dict[str, Any]] | None:
    """Task records from a local Labs root; ``None`` when the registry is not materialized there."""
    if labs_root is None:
        return None
    root = Path(labs_root)
    registry_file = root / REGISTRY_PATH
    records_dir = root / RECORDS_DIR
    if not registry_file.is_file() and not records_dir.is_dir():
        return None
    candidates: list[Any] = []
    try:
        registry = json.loads(registry_file.read_text(encoding="utf-8")) if registry_file.is_file() else {}
        if isinstance(registry, dict) and isinstance(registry.get("tasks"), list):
            candidates.extend(registry["tasks"])
    except (OSError, ValueError):
        pass  # an unreadable index only narrows what can be mapped; it never yields a guess
    if records_dir.is_dir():
        for path in sorted(records_dir.glob("*.json")):
            try:
                candidates.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
    records: dict[str, dict[str, Any]] = {}
    for record in candidates:
        if isinstance(record, dict) and isinstance(record.get("task_id"), str) and record["task_id"].strip():
            # The per-record file is the authoritative copy when both exist.
            records[record["task_id"]] = record
    return list(records.values())


def registry_records_from_roots(roots: Mapping[str, Path]) -> list[dict[str, Any]] | None:
    """Registry records from the Labs root in an existing roots map, never raising."""
    try:
        return load_registry_records(roots.get(LABS_REPOSITORY))
    except Exception:  # metadata derivation must never change target execution
        return None


def _target_keys(target: Mapping[str, Any]) -> set[str]:
    keys: set[str] = set()
    workflow = str(target.get("workflow") or "").strip()
    if workflow:
        keys.add(workflow)
        for suffix in (".yml", ".yaml"):
            if workflow.endswith(suffix):
                keys.add(workflow[: -len(suffix)])
    aliases = target.get("aliases") if isinstance(target.get("aliases"), list) else []
    keys.update(str(alias).strip() for alias in aliases if str(alias).strip())
    canonical_path = str(target.get("canonical_path") or "").strip()
    if canonical_path:
        keys.add(canonical_path)
    return keys


def _strings(value: Any) -> set[str]:
    return {item for item in value if isinstance(item, str)} if isinstance(value, list) else set()


def registry_matches(target: Mapping[str, Any], registry_records: Iterable[Mapping[str, Any]]) -> list[str]:
    """Sorted task_ids whose structured targets name this target's repository and workflow/alias/path."""
    repo = str(target.get("repo") or "").strip()
    keys = _target_keys(target)
    if not repo or not keys:
        return []
    matches = set()
    for record in registry_records:
        targets = record.get("targets") if isinstance(record.get("targets"), dict) else {}
        repositories = _strings(targets.get("repositories"))
        if isinstance(record.get("repository"), str):
            repositories.add(record["repository"])
        if repo in repositories and _strings(targets.get("components")) & keys:
            matches.add(str(record["task_id"]))
    return sorted(matches)


def _refusal(code: str, repair: str, retry_entrypoint: str) -> dict[str, str]:
    return non_allow(code, FAILED_PREDICATE, repair, retry_entrypoint=retry_entrypoint,
                     owning_existing_goal=DEFAULT_OWNING_EXISTING_GOAL,
                     next_attempt="rerun the Healer target after its canonical_owner is declared or its owning task is registered")


def owning_goal_for_target(
    target: Mapping[str, Any],
    registry_records: Iterable[Mapping[str, Any]] | None,
    *,
    retry_entrypoint: str = DEFAULT_RETRY_ENTRYPOINT,
) -> tuple[str | None, dict[str, str] | None]:
    """``(goal, None)`` when declared or exactly registered, else ``(None, six-field refusal)``."""
    owner = str(target.get("canonical_owner") or "").strip()
    if owner:
        return owner, None
    repo = str(target.get("repo") or "")
    workflow = str(target.get("workflow") or target.get("canonical_path") or "")
    named = f"{repo} {workflow}".strip()
    declare = (f"declare canonical_owner for target {named} in data/orchestrator_targets.json, or register "
               f"it in the canonical task registry (a {LABS_REPOSITORY} {RECORDS_DIR} record whose "
               f"targets.repositories names {repo} and whose targets.components names the workflow or an alias)")
    if registry_records is None:
        return None, _refusal(
            REGISTRY_NOT_MATERIALIZED,
            f"materialize {LABS_REPOSITORY} and list its root in STEGVERSE_REPO_ROOTS_JSON so the owning goal "
            f"of {named} can be read from {RECORDS_DIR}; or {declare}", retry_entrypoint)
    matches = registry_matches(target, list(registry_records))
    if len(matches) == 1:
        return matches[0], None
    if matches:
        return None, _refusal(
            AMBIGUOUS_IN_REGISTRY,
            f"canonical task records {', '.join(matches)} all name {named}; declare which one owns it as "
            f"canonical_owner in data/orchestrator_targets.json, or narrow the registry records to one", retry_entrypoint)
    return None, _refusal(NOT_IN_REGISTRY, declare, retry_entrypoint)
