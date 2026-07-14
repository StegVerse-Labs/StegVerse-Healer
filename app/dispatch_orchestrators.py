import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

API = "https://api.github.com"


def post(url: str, token: str, payload: dict[str, Any]) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "StegVerse-Healer",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status not in (200, 201, 202, 204):
                raise RuntimeError(f"Unexpected status: {resp.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub dispatch failed ({exc.code}): {detail}") from exc


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config.get("targets"), list):
        raise ValueError("targets must be a list")
    return config


def due_now(target: dict[str, Any], now: dt.datetime, mode: str) -> bool:
    """Manual dispatch bypasses cadence; scheduled dispatch honors UTC hours/days."""
    if mode != "schedule":
        return True

    hours = target.get("run_hours_utc")
    if hours is not None:
        if not isinstance(hours, list) or not all(isinstance(value, int) and 0 <= value <= 23 for value in hours):
            raise ValueError(f"{target.get('repo')}: run_hours_utc must be a list of integers from 0 to 23")
        if now.hour not in hours:
            return False

    weekdays = target.get("run_weekdays_utc")
    if weekdays is not None:
        if not isinstance(weekdays, list) or not all(isinstance(value, int) and 0 <= value <= 6 for value in weekdays):
            raise ValueError(f"{target.get('repo')}: run_weekdays_utc must be a list of integers from 0 to 6")
        if now.weekday() not in weekdays:
            return False

    return True


def main() -> int:
    token = os.environ.get("HEALER_GH_TOKEN", "").strip()
    if not token:
        print("Missing HEALER_GH_TOKEN env var.", file=sys.stderr)
        return 2

    scope = (os.environ.get("RUN_SCOPE") or "all").strip().lower()
    mode = (os.environ.get("DISPATCH_MODE") or "manual").strip().lower()
    config_path = os.environ.get("TARGETS_FILE", "data/orchestrator_targets.json")
    config = load_config(config_path)
    default_ref = str(config.get("default_ref", "main"))
    now = dt.datetime.now(dt.timezone.utc)

    def matches(target: dict[str, Any]) -> bool:
        if not target.get("enabled", True):
            return False
        short_name = str(target.get("repo", "")).split("/")[-1].lower()
        aliases = {str(value).lower() for value in target.get("aliases", [])}
        scope_match = scope == "all" or scope == short_name or scope in aliases
        return scope_match and due_now(target, now, mode)

    selected = [target for target in config["targets"] if matches(target)]
    if not selected:
        print(f"No enabled targets are due for scope='{scope}', mode='{mode}', utc={now.isoformat()}.")
        return 0

    print(f"Dispatching {len(selected)} target(s) with scope='{scope}', mode='{mode}', utc={now.isoformat()}")
    failures: list[str] = []

    for target in selected:
        repo = str(target["repo"])
        workflow = str(target["workflow"])
        ref = str(target.get("ref") or default_ref)
        inputs = target.get("inputs", {})
        if not isinstance(inputs, dict):
            failures.append(f"{repo}: inputs must be an object")
            continue

        url = f"{API}/repos/{repo}/actions/workflows/{workflow}/dispatches"
        payload: dict[str, Any] = {"ref": ref}
        if inputs:
            payload["inputs"] = {str(key): str(value) for key, value in inputs.items()}

        print(f"- Trigger: {repo} :: {workflow} (ref={ref}, inputs={payload.get('inputs', {})})")
        try:
            post(url, token, payload)
        except Exception as exc:
            failures.append(f"{repo}: {exc}")
            print(f"  FAILED: {exc}", file=sys.stderr)
        else:
            print("  OK")

    if failures:
        print("Dispatch failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
