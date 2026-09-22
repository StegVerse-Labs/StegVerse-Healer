from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

import reusable_task_scheduler as subject  # noqa: E402


def materialize_component(base: Path, component_id: str, marker: Path) -> Path:
    root = base / component_id.replace(".", "-")
    target = root / marker
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# fixture\n", encoding="utf-8")
    return root


def valid_receipt(base: Path) -> tuple[Path, dict]:
    roots = {}
    identities = {}
    for index, (component_id, (_repo, marker)) in enumerate(subject.SOURCE_PREP_COMPONENTS.items(), start=1):
        root = materialize_component(base, component_id, marker)
        roots[component_id] = str(root)
        identities[component_id] = "sha256:" + format(index, "064x")
    value = {
        "schema": subject.SOURCE_PREP_SCHEMA,
        "state": "COMPLETE",
        "transition_id": "SV_DN1_PRODUCTION_SOURCE_PREPARATION_COMPLETE",
        "source_roots": roots,
        "source_identities": identities,
        "migration_anchors_verified": True,
        "network_source_fetch_performed": False,
        "github_platform_required": False,
        "credential_used": False,
        "github_token_used": False,
        "repository_writeback_performed": False,
    }
    path = base / "latest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path, value


def test_complete_verified_source_prep_receipt_augments_all_four_governance_roots():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        receipt, value = valid_receipt(base)
        with mock.patch.dict("os.environ", {subject.SOURCE_PREP_RECEIPT_ENV: str(receipt)}, clear=False):
            roots, state = subject._verified_governance_component_roots()
        assert state == "SV_DN1_SOURCE_PREP_RECEIPT_VERIFIED"
        assert set(roots) == {repository for repository, _marker in subject.SOURCE_PREP_COMPONENTS.values()}
        for component_id, (repository, _marker) in subject.SOURCE_PREP_COMPONENTS.items():
            assert roots[repository] == Path(value["source_roots"][component_id]).resolve()


def test_source_prep_receipt_with_network_fetch_or_missing_complete_state_is_rejected():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        receipt, value = valid_receipt(base)
        value["network_source_fetch_performed"] = True
        receipt.write_text(json.dumps(value), encoding="utf-8")
        with mock.patch.dict("os.environ", {subject.SOURCE_PREP_RECEIPT_ENV: str(receipt)}, clear=False):
            roots, state = subject._verified_governance_component_roots()
        assert roots == {}
        assert state == "SV_DN1_SOURCE_PREP_RECEIPT_NOT_ADMISSIBLE"


def test_source_prep_receipt_rejects_missing_component_marker_even_with_sha_identity():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        receipt, value = valid_receipt(base)
        sdk_root = Path(value["source_roots"]["stegverse.sdk"])
        (sdk_root / subject.SOURCE_PREP_COMPONENTS["stegverse.sdk"][1]).unlink()
        with mock.patch.dict("os.environ", {subject.SOURCE_PREP_RECEIPT_ENV: str(receipt)}, clear=False):
            roots, state = subject._verified_governance_component_roots()
        assert roots == {}
        assert state == "SV_DN1_SOURCE_PREP_ROOT_NOT_MATERIALIZED:stegverse.sdk"


def test_absent_source_prep_receipt_does_not_fabricate_roots():
    with tempfile.TemporaryDirectory() as td:
        missing = Path(td) / "missing.json"
        with mock.patch.dict("os.environ", {subject.SOURCE_PREP_RECEIPT_ENV: str(missing)}, clear=False):
            roots, state = subject._verified_governance_component_roots()
        assert roots == {}
        assert state == "SV_DN1_SOURCE_PREP_RECEIPT_NOT_PRESENT"


def test_existing_source_prep_bridge_uses_canonical_targeted_resident_path_only():
    with tempfile.TemporaryDirectory() as td:
        base_dir = Path(td)
        github_root = base_dir / ".github"
        bridge = github_root / subject.SOURCE_PREP_BRIDGE_REL
        bridge.parent.mkdir(parents=True, exist_ok=True)
        bridge.write_text("# bridge fixture\n", encoding="utf-8")
        runtime_root = base_dir / "runtime"
        runtime_root.mkdir()

        roots = {"StegVerse-Labs/.github": github_root}
        for component_id, (repository, marker) in subject.SOURCE_PREP_COMPONENTS.items():
            roots[repository] = materialize_component(base_dir, component_id, marker)

        observed = {}

        def fake_run(command, cwd, env, timeout):
            observed["command"] = command
            observed["cwd"] = cwd
            observed["env"] = env
            observed["timeout"] = timeout
            return {"returncode": 0, "stdout": "{}", "stderr": ""}

        verified = {repository: roots[repository] for repository, _marker in subject.SOURCE_PREP_COMPONENTS.values()}
        with mock.patch.object(subject.base, "_run", side_effect=fake_run), mock.patch.object(
            subject, "_verified_governance_component_roots", return_value=(verified, "SV_DN1_SOURCE_PREP_RECEIPT_VERIFIED")
        ):
            result = subject._invoke_existing_source_prep_bridge(
                roots=roots,
                runtime_root=runtime_root,
                runtime_root_source="TEST_RUNTIME",
            )

        assert result["state"] == "SOURCE_PREP_RECEIPT_VERIFIED"
        assert observed["command"] == [
            sys.executable,
            str(bridge),
            "--source-root", str(github_root),
            "--runtime-root", str(runtime_root),
            "--task-id", subject.SOURCE_PREP_TASK_ID,
            "--cosv-task-vector", subject.SOURCE_PREP_COSV,
        ]
        assert observed["cwd"] == github_root
        assert observed["env"]["STEGVERSE_SDK_SOURCE_ROOT"] == str(roots["StegVerse-org/StegVerse-SDK"])
        assert observed["env"]["STEGVERSE_STEGCORE_SOURCE_ROOT"] == str(roots["StegVerse-Labs/StegCore"])
        assert observed["env"]["STEGVERSE_CORE_LITE_SOURCE_ROOT"] == str(roots["Data-Continuation/core-lite"])
        assert observed["env"]["STEGVERSE_MASTER_RECORDS_SOURCE_ROOT"] == str(roots["master-records/orchestration"])
        assert observed["env"][subject.RUNTIME_ROOT_ENV] == str(runtime_root)
        assert result["new_scheduler_created"] is False
        assert result["new_dispatcher_created"] is False
        assert result["new_workercoordinator_created"] is False


def test_existing_source_prep_bridge_fails_closed_when_runtime_root_is_unavailable():
    result = subject._invoke_existing_source_prep_bridge(
        roots={"StegVerse-Labs/.github": ROOT},
        runtime_root=None,
        runtime_root_source="NOT_OBSERVED",
    )
    assert result["state"] == "BOUNDARY_RECORDED"
    assert result["boundary"] == "RESIDENT_RUNTIME_ROOT_NOT_MATERIALIZED"
