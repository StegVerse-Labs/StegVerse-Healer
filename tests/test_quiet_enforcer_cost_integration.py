import json
from pathlib import Path

from app import audit_schedules


def test_quiet_enforcer_embeds_ranked_actions_cost_analysis(tmp_path, monkeypatch):
    repo_root = tmp_path / "Repo"
    workflow = repo_root / ".github" / "workflows" / "validate.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """name: Validate\non:\n  push: {}\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo pass\n""",
        encoding="utf-8",
    )

    targets = tmp_path / "targets.json"
    targets.write_text(
        json.dumps({
            "targets": [
                {
                    "repo": "StegVerse-Labs/Repo",
                    "workflow": "validate.yml",
                    "enabled": True,
                    "run_hours_utc": [3],
                }
            ]
        }),
        encoding="utf-8",
    )
    receipt = tmp_path / "quiet.json"
    policy = Path(__file__).resolve().parents[1] / "data" / "actions_cost_policy.json"

    monkeypatch.setenv("TARGETS_FILE", str(targets))
    monkeypatch.setenv("QUIET_RECEIPT", str(receipt))
    monkeypatch.setenv("ACTIONS_COST_POLICY", str(policy))
    monkeypatch.setenv("STEGVERSE_REPO_ROOTS_JSON", json.dumps({"StegVerse-Labs/Repo": str(repo_root)}))
    for name in audit_schedules.FORBIDDEN_CREDENTIALS:
        monkeypatch.delenv(name, raising=False)

    assert audit_schedules.main() == 0
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["schema"] == "stegverse.healer.quiet-enforcer-receipt.v3"
    assert payload["state"] == "COMPLETE"
    assert payload["summary"]["violation_count"] == 0
    assert payload["summary"]["cost_review_candidate_count"] >= 1
    assert payload["cost_analysis"]["github_token_required"] is False
    assert payload["cost_analysis"]["network_required"] is False
    assert payload["cost_analysis"]["authority_effect"] == "NONE"
    top = payload["cost_analysis"]["top_remediation_candidates"]
    assert top
    assert top[0]["workflow"].endswith("validate.yml")
    assert "UNFILTERED_PUSH" in top[0]["review_reasons"]


def test_quiet_enforcer_still_fails_repository_local_schedule(tmp_path, monkeypatch):
    repo_root = tmp_path / "Repo"
    workflow = repo_root / ".github" / "workflows" / "hourly.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """name: Hourly\non:\n  schedule:\n    - cron: '0 * * * *'\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo pass\n""",
        encoding="utf-8",
    )
    targets = tmp_path / "targets.json"
    targets.write_text(json.dumps({"targets": [{"repo": "StegVerse-Labs/Repo", "workflow": "hourly.yml", "enabled": True}]}), encoding="utf-8")
    receipt = tmp_path / "quiet.json"
    policy = Path(__file__).resolve().parents[1] / "data" / "actions_cost_policy.json"

    monkeypatch.setenv("TARGETS_FILE", str(targets))
    monkeypatch.setenv("QUIET_RECEIPT", str(receipt))
    monkeypatch.setenv("ACTIONS_COST_POLICY", str(policy))
    monkeypatch.setenv("STEGVERSE_REPO_ROOTS_JSON", json.dumps({"StegVerse-Labs/Repo": str(repo_root)}))
    for name in audit_schedules.FORBIDDEN_CREDENTIALS:
        monkeypatch.delenv(name, raising=False)

    assert audit_schedules.main() == 1
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["state"] == "FAILED"
    assert payload["summary"]["violation_count"] == 1
    assert payload["cost_analysis"]["scheduled_workflow_count"] == 1
    assert payload["cost_analysis"]["estimated_scheduled_job_starts_per_month"] == 744.0
