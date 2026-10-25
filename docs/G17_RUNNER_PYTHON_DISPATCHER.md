# G17 stable dispatcher: runner-python variant

Repository: StegVerse-Labs/StegVerse-Healer. Goal: G17-WORKFLOW-SURFACE-MINIMIZATION
(StegVerse-Labs/.github#167/#168; StegVerse-org/.github#166).

## Why a variant

The StegDB#60 template (`StegVerse-Labs/StegDB .github/workflows/validation-dispatcher.yml`
@ eab2e773) uses `actions/checkout@11bd7190` and an optional
`actions/setup-python@a26af69b` step. This repository's contract
`tests/test_dependency_surface.py` forbids both:

- `test_workflows_install_nothing_and_do_not_set_up_python` rejects any workflow line
  that names `actions/setup-python` or installs a package;
- `test_workflows_use_only_allowed_actions` allows only the five SHA-pinned actions in
  `ALLOWED_ACTIONS` (checkout@11d5960a, cache/restore, cache/save, download-artifact,
  upload-artifact@ea165f8d).

## What the variant is

It is the dispatcher StegVerse-org/LLM-adapter uses under LLMA-368
(no token-backed setup action), with this repository's name and credential list:

1. `permissions: {}` at workflow level; triggers `pull_request` and `push` to `main` only
   (no dispatch, schedule or polling).
2. Every job (`plan` and each `check` matrix cell) first refuses a credential-bearing
   environment (the same variable list `test-readiness.yml` refused), then fetches the
   exact source anonymously: `git init .`, `git -c http.extraheader= fetch --depth 1
   https://github.com/StegVerse-Labs/StegVerse-Healer.git <sha>`, `git checkout --detach
   FETCH_HEAD`. No named remote is added, so a folded job's own anonymous fetch step
   (which adds `origin`) still runs byte for byte.
3. `tools/tasks/run_catalog.py` (StegDB @ eab2e773, copied unmodified) runs on the
   runner image's `python3` (`command -v python3 || command -v python`). There is no
   setup-python step and no `python_version` in any catalog group.
4. The only action is `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02`
   (in `ALLOWED_ACTIONS`), used only when a folded job uploaded an artifact.

Everything else is the StegDB#60 pattern unchanged: `tools/tasks/task_catalog.json` holds
the groups, each step body is pinned by sha256 and refused on drift by
`run_catalog.py verify`, the originals are verbatim records under `tools/tasks/folded/`
with their sha256 in `control/workflow-surface-registry.json`, and
`tests/test_workflow_surface_registry.py` fails closed on an unregistered workflow.

## When to use it

Use this variant in any repository whose contract forbids `actions/setup-python` or
`actions/checkout@11bd7190`, or whose folded jobs ran on the runner's Python. Adjust only
the repository URL and the refused-credential list; keep `permissions: {}`.

The SKAP Vault inside KV is the only PII and credential store for every user, the
ecosystem's own included. No secret, token, credential, dependency, cron, dispatch or
polling is added or changed.
