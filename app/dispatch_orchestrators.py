import json
import os
import sys
import urllib.request

API = "https://api.github.com"

def post(url: str, token: str, payload: dict) -> None:
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
        },
    )
    with urllib.request.urlopen(req) as resp:
        # GitHub dispatch returns 204 No Content if successful
        if resp.status not in (200, 201, 202, 204):
            raise RuntimeError(f"Unexpected status: {resp.status}")

def main() -> int:
    token = os.environ.get("HEALER_GH_TOKEN", "").strip()
    if not token:
        print("Missing HEALER_GH_TOKEN env var.")
        return 2

    scope = (os.environ.get("RUN_SCOPE") or "all").strip().lower()
    config_path = os.environ.get("TARGETS_FILE", "data/orchestrator_targets.json")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    targets = cfg.get("targets", [])
    default_ref = cfg.get("default_ref", "main")

    # scope filtering: "all" or exact repo shortname (e.g. "site", "tv")
    def matches(t: dict) -> bool:
        if scope == "all":
            return True
        repo = t.get("repo", "")
        short = repo.split("/")[-1].lower()
        return scope == short

    selected = [t for t in targets if matches(t)]

    if not selected:
        print(f"No targets match scope '{scope}'.")
        return 0

    print(f"Dispatching {len(selected)} target(s) with scope='{scope}'")

    for t in selected:
        repo = t["repo"]
        workflow = t["workflow"]
        ref = t.get("ref") or default_ref

        url = f"{API}/repos/{repo}/actions/workflows/{workflow}/dispatches"
        payload = {"ref": ref, "inputs": {"master_override": "false"}}

        print(f"- Trigger: {repo} :: {workflow} (ref={ref})")
        post(url, token, payload)
        print("  OK")

    return 0

if __name__ == "__main__":
    sys.exit(main())
