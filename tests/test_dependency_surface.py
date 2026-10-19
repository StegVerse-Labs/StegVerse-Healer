"""Dependency surface guard: Healer runs on the Python standard library and the runner's own python3.

Every top-level import in every tracked ``.py`` file must be standard library or a
module/package of this repository; no dependency manifest may exist; workflows must
not install packages or a Python toolchain, and may use only the listed GitHub actions.
"""
from __future__ import annotations

import ast
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
MANIFESTS = ("requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "poetry.lock")
INSTALL_STEP = re.compile(r"\b(pip3?\s+install|python3?\s+-m\s+pip\b|apt(-get)?\s+install|curl\s|wget\s|npm\s+(install|ci)\b)")
# The complete set of actions the workflows may use; adding one is a dependency decision.
ALLOWED_ACTIONS = {
    "actions/checkout@v4",
    "actions/cache/restore@v4",
    "actions/cache/save@v4",
    "actions/download-artifact@v4",
    "actions/upload-artifact@v4",
}


def _tracked(pattern: str) -> list[Path]:
    return sorted(p for p in ROOT.rglob(pattern) if not SKIP_PARTS.intersection(p.relative_to(ROOT).parts))


def _local_names() -> set[str]:
    names = {p.stem for p in _tracked("*.py")}
    names.update(p.name for p in ROOT.rglob("*") if p.is_dir() and not SKIP_PARTS.intersection(p.relative_to(ROOT).parts))
    return names


def _workflow_files() -> list[Path]:
    return sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))


class TestDependencySurface(unittest.TestCase):
    def test_every_import_is_stdlib_or_local(self) -> None:
        local = _local_names()
        offenders = []
        for path in _tracked("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                    modules = [node.module]
                else:
                    continue
                for module in modules:
                    top = module.split(".")[0]
                    if top != "__future__" and top not in sys.stdlib_module_names and top not in local:
                        offenders.append(f"{path.relative_to(ROOT)}:{node.lineno} {module}")
        self.assertEqual(offenders, [])

    def test_no_dependency_manifest(self) -> None:
        present = [str(p.relative_to(ROOT)) for name in MANIFESTS for p in _tracked(name)]
        self.assertEqual(present, [])

    def test_workflows_install_nothing_and_do_not_set_up_python(self) -> None:
        offenders = []
        for path in _workflow_files():
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if "actions/setup-python" in line or INSTALL_STEP.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{lineno} {line.strip()}")
        self.assertEqual(offenders, [])

    def test_workflows_use_only_allowed_actions(self) -> None:
        used = set()
        for path in _workflow_files():
            used.update(re.findall(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", path.read_text(encoding="utf-8"), re.M))
        self.assertLessEqual(used, ALLOWED_ACTIONS, sorted(used - ALLOWED_ACTIONS))

    def test_pip_installing_composite_action_is_not_used_by_any_workflow(self) -> None:
        # actions/yaml-corrector installs yamllint; it stays dead unless a workflow adopts it deliberately.
        for path in _workflow_files():
            self.assertNotIn("yaml-corrector", path.read_text(encoding="utf-8"), str(path))


if __name__ == "__main__":
    unittest.main()
