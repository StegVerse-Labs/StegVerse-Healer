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


def main() -> int:
    token = os.environ.get("HEALER_GH_TOKEN", "").strip()
    if not token:
        print("Missing HEALER_GH_TOKEN env var.", file=sys.stderr)
        return 2

    scope = (os.environ.get("RUN_SCOPE") or "all").strip().lower()
    config_path = os.environ.get("TARGETS_FILE", "data/orchestrator_targets.json")
    config = load_config(config_path)
    default_ref = str(config.get("default_ref", "main"))

    def matches(target: dict[str, Any]) -> bool:
        if not target.get("enabled", True):
            return False
        if scope == "all":
            return True
        short_name = str(target.get("repo", "")).split("/")[-1].lower()
        aliases = {str(value).lower() for value in target.get("aliases", [])}
        return scope == short_name or scope in aliases

    selected = [target for target in config["targets"] if matches(target)]
    if not selected:
        print(f"No enabled targets match scope '{scope}'.")
        return 0

    print(f"Dispatching {len(selected)} target(s) with scope='{scope}'")
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
        except Exception as exc:  # report all target failures in one run
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
