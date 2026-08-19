#!/usr/bin/env python3
"""Parse GitHub Actions failure-notification mail into Healer observations.

This module is transport-neutral: it accepts already-read message metadata/body,
contains no mailbox credentials, and performs no mailbox mutation. The parser is
intended for historical backfill and live adapters that are separately admitted.
"""

from __future__ import annotations

import re
from typing import Any

SUBJECT_RE = re.compile(
    r"^\[(?P<repository>[^\]]+)\]\s+"
    r"(?P<kind>PR run failed|Run failed):\s+"
    r"(?P<workflow>.+?)\s+-\s+"
    r"(?P<context>.+?)\s+\((?P<commit>[0-9a-fA-F]{7,40})\)$"
)
RUN_URL_RE = re.compile(r"github\.com/[^/\s]+/[^/\s]+/actions/runs/(?P<run_id>\d+)")
ANNOTATION_JOB_RE = re.compile(r"annotations for\s+(.+?)(?:\n|\r|\d|\])", re.IGNORECASE)


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def classify_mail_result(body: str, snippet: str = "") -> tuple[str, str]:
    text = f"{body}\n{snippet}".lower()
    if "no jobs were run" in text:
        return "NO_JOBS_RUN", "No jobs were run"
    if "some jobs were not successful" in text:
        return "WORKFLOW_JOB_FAILURE", "Some jobs were not successful"
    if "all jobs have failed" in text:
        return "WORKFLOW_JOB_FAILURE", "All jobs have failed"
    return "GITHUB_ACTIONS_FAILURE_NOTIFICATION", _clean(snippet)[:500]


def parse_github_failure_message(message: dict[str, Any]) -> dict[str, Any]:
    subject = _clean(message.get("subject"))
    match = SUBJECT_RE.match(subject)
    if not match:
        raise ValueError("unsupported GitHub failure notification subject")

    body = str(message.get("body") or "")
    snippet = _clean(message.get("snippet"))
    failure_class, failure_message = classify_mail_result(body, snippet)
    run_match = RUN_URL_RE.search(body)
    run_id = run_match.group("run_id") if run_match else ""
    job = ""
    job_match = ANNOTATION_JOB_RE.search(body)
    if job_match:
        job = _clean(job_match.group(1))

    kind = match.group("kind")
    context = _clean(match.group("context"))
    branch = context if kind == "Run failed" else ""
    pr = context if kind == "PR run failed" else ""

    received_at = _clean(message.get("email_ts") or message.get("received_at"))
    message_id = _clean(message.get("id") or message.get("message_id"))
    if not message_id or not received_at:
        raise ValueError("message id and received timestamp are required")

    return {
        "message_id": message_id,
        "thread_id": _clean(message.get("thread_id")),
        "internet_message_id": _clean(message.get("internet_message_id")),
        "repository": _clean(match.group("repository")),
        "workflow": _clean(match.group("workflow")),
        "job": job,
        "branch": branch,
        "pr": pr,
        "commit_sha": match.group("commit").lower(),
        "run_id": run_id,
        "received_at": received_at,
        "subject": subject,
        "failure_message": failure_message,
        "failure_class": failure_class,
        "source": "github-email",
        "source_semantics": "observation_only",
        "authority_effect": False,
        "heartbeat_effect": False,
    }
