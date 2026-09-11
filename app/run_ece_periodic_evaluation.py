#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

from app.ece_periodic_evaluation import execute_periodic_ece


def main() -> int:
    raw_roots = os.getenv("STEGVERSE_REPO_ROOTS_JSON", "").strip()
    raw_runtime = os.getenv("STEGVERSE_HEARTBEAT_ROOT", "").strip()
    if not raw_roots or not raw_runtime:
        print(json.dumps({"state":"BLOCKED","outcome":"ECE_RUNTIME_BINDING_MISSING","authority_effect":"NONE"}, sort_keys=True))
        return 3
    parsed = json.loads(raw_roots)
    if not isinstance(parsed, dict):
        raise SystemExit("STEGVERSE_REPO_ROOTS_JSON must be an object")
    roots = {str(repo): Path(str(path)).expanduser().resolve() for repo, path in parsed.items()}
    result = execute_periodic_ece(roots, Path(raw_runtime))
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("state") == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
