#!/usr/bin/env python3
"""Parse GitHub operational-failure mail into Healer observations.

The parser accepts ordinary repository workflow-failure notifications plus
organization/account-level GitHub Actions capacity and budget alerts. Transport
credential and sender verification remain outside this credential-neutral module.
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
INCLUDED_MINUTES_RE = re.compile(
    r"^\[GitHub\]\s+You have used\s+(?P<percent>\d+)%\s+of the Actions minutes included for the\s+(?P<account>.+?)\s+account$",
    re.IGNORECASE,
)
BUDGET_RE = re.compile(
    r"^\[GitHub\]\s+You've hit\s+(?P<percent>\d+)%\s+of your budget for the\s+(?P<account>.+?)\s+account$",
    re.IGNORECASE,
)
RUN_URL_RE = re.compile(r"github\.com/[^/\s]+/[^/\s]+/actions/runs/(?P<run_id>\d+)")
ANNOTATION_JOB_RE = re.compile(r"annotations for\s+(.+?)(?:\n|\r|\d|\])", re.IGNORECASE)
CAPACITY_FAILURE_CLASSES = {
    "ACTIONS_INCLUDED_MINUTES_WARNING",
    "ACTIONS_INCLUDED_MINUTES_EXHAUSTED",
    "ACTIONS_BUDGET_APPROACHING",
    "ACTIONS_BUDGET_HIGH",
    "ACTIONS_BUDGET_EXHAUSTED",
}


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def classify_actions_capacity_subject(subject: str) -> dict[str, Any] | None:
    subject = _clean(subject)
    match = INCLUDED_MINUTES_RE.match(subject)
    if match:
        percent = int(match.group("percent"))
        if percent >= 100:
            failure_class, result = "ACTIONS_INCLUDED_MINUTES_EXHAUSTED", "OPERATIONAL_CAPACITY_EXHAUSTED"
        elif percent >= 90:
            failure_class, result = "ACTIONS_INCLUDED_MINUTES_WARNING", "OPERATIONAL_CAPACITY_HIGH"
        else:
            return None
        return {
            "account": _clean(match.group("account")),
            "threshold_percent": percent,
            "failure_class": failure_class,
            "notification_result_class": result,
            "workflow": "GitHub Actions included minutes",
        }

    match = BUDGET_RE.match(subject)
    if match:
        percent = int(match.group("percent"))
        if percent >= 100:
            failure_class, result = "ACTIONS_BUDGET_EXHAUSTED", "OPERATIONAL_CAPACITY_EXHAUSTED"
        elif percent >= 90:
            failure_class, result = "ACTIONS_BUDGET_HIGH", "OPERATIONAL_CAPACITY_HIGH"
        elif percent >= 75:
            failure_class, result = "ACTIONS_BUDGET_APPROACHING", "OPERATIONAL_CAPACITY_WARNING"
        else:
            return None
        return {
            "account": _clean(match.group("account")),
            "threshold_percent": percent,
            "failure_class": failure_class,
            "notification_result_class": result,
            "workflow": "GitHub Actions budget",
        }
    return None


def classify_notification_result(body: str, snippet: str = "") -> tuple[str, str]:
    text = f"{body}\n{snippet}".lower()
    if "no jobs were run" in text:
        return "NO_JOBS_RUN", "No jobs were run"
    if "some jobs were not successful" in text:
        return "WORKFLOW_JOB_FAILURE", "Some jobs were not successful"
    if "all jobs have failed" in text:
        return "WORKFLOW_JOB_FAILURE", "All jobs have failed"
    return "GITHUB_ACTIONS_FAILURE_NOTIFICATION", _clean(snippet)[:500]


def semantic_failure_class(workflow: str, subject: str, body: str, snippet: str, notification_result: str) -> str:
    if notification_result == "NO_JOBS_RUN":
        return "NO_JOBS_RUN"
    text = " ".join((workflow, subject, body, snippet)).lower()
    if "chain continuation" in text or "continuation" in workflow.lower():
        return "CONTINUITY_FAILURE"
    if "route_unreachable" in text or "route unreachable" in text:
        return "ROUTE_UNREACHABLE"
    if "module not found" in text or "modulenotfounderror" in text:
        return "MODULE_NOT_FOUND"
    if "cannot import name" in text or "importerror" in text:
        return "IMPORT_ERROR"
    if "schema" in workflow.lower() or "schema validation" in text:
        return "SCHEMA_VALIDATION"
    if "fail_closed" in text or "fail-closed" in text:
        return "FAIL_CLOSED"
    if "forbidden credential" in text or "credential authority" in text or "permission" in text:
        return "AUTHORITY_BOUNDARY"
    if "timed out" in text or "timeout" in text:
        return "TIMEOUT"
    return ""


def _required_identity(message: dict[str, Any]) -> tuple[str, str]:
    received_at = _clean(message.get("email_ts") or message.get("received_at"))
    message_id = _clean(message.get("id") or message.get("message_id"))
    if not message_id or not received_at:
        raise ValueError("message id and received timestamp are required")
    return message_id, received_at


def parse_github_failure_message(message: dict[str, Any]) -> dict[str, Any]:
    subject = _clean(message.get("subject"))
    message_id, received_at = _required_identity(message)
    snippet = _clean(message.get("snippet"))
    body = str(message.get("body") or "")

    capacity = classify_actions_capacity_subject(subject)
    if capacity:
        supplied_class = _clean(message.get("signal_class")).upper()
        if supplied_class and supplied_class != capacity["failure_class"]:
            raise ValueError("GitHub capacity signal classification mismatch")
        account = capacity["account"]
        return {
            "message_id": message_id,
            "thread_id": _clean(message.get("thread_id")),
            "internet_message_id": _clean(message.get("internet_message_id")),
            "repository": f"github-account:{account}",
            "workflow": capacity["workflow"],
            "job": "",
            "branch": "",
            "pr": "",
            "commit_sha": "",
            "run_id": "",
            "received_at": received_at,
            "subject": subject,
            "failure_message": snippet[:500] or subject,
            "notification_result_class": capacity["notification_result_class"],
            "failure_class": capacity["failure_class"],
            "account": account,
            "threshold_percent": capacity["threshold_percent"],
            "source": "github-email",
            "source_semantics": "observation_only",
            "authority_effect": False,
            "heartbeat_effect": False,
        }

    match = SUBJECT_RE.match(subject)
    if not match:
        raise ValueError("unsupported GitHub operational failure notification subject")

    notification_result, failure_message = classify_notification_result(body, snippet)
    workflow = _clean(match.group("workflow"))
    failure_class = semantic_failure_class(workflow, subject, body, snippet, notification_result)
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

    observation = {
        "message_id": message_id,
        "thread_id": _clean(message.get("thread_id")),
        "internet_message_id": _clean(message.get("internet_message_id")),
        "repository": _clean(match.group("repository")),
        "workflow": workflow,
        "job": job,
        "branch": branch,
        "pr": pr,
        "commit_sha": match.group("commit").lower(),
        "run_id": run_id,
        "received_at": received_at,
        "subject": subject,
        "failure_message": failure_message,
        "notification_result_class": notification_result,
        "source": "github-email",
        "source_semantics": "observation_only",
        "authority_effect": False,
        "heartbeat_effect": False,
    }
    if failure_class:
        observation["failure_class"] = failure_class
    return observation
