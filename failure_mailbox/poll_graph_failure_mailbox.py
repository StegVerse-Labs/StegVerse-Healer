#!/usr/bin/env python3
"""Poll Microsoft Graph for bounded GitHub Actions failure notifications.

This transport intentionally reuses the proven ARA Microsoft Graph application
credential mechanism. It differs semantically from ARA: Healer observes messages
but does not mark them read, archive them, or otherwise mutate the mailbox.

The output is a sanitized JSONL batch plus a non-secret manifest suitable for
failure_mailbox.shadow. Mailbox credentials never enter either output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ENV_NAMES = (
    "STEGVERSE_MAIL_TENANT_ID",
    "STEGVERSE_MAIL_CLIENT_ID",
    "STEGVERSE_MAIL_CLIENT_SECRET",
    "STEGVERSE_MONITOR_MAILBOX",
)
SENDER = "notifications@github.com"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def configuration() -> tuple[dict[str, str], str]:
    values = {name: os.getenv(name, "").strip() for name in ENV_NAMES}
    present = [name for name, value in values.items() if value]
    if not present:
        return values, "not_configured"
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError("partial mailbox configuration; missing: " + ", ".join(missing))
    return values, "configured"


def request_json(url: str, *, token: str) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Graph HTTP {exc.code}: {raw[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Graph network error: {exc.reason}") from exc


def get_access_token(config: dict[str, str]) -> str:
    tenant = urllib.parse.quote(config["STEGVERSE_MAIL_TENANT_ID"], safe="")
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    form = urllib.parse.urlencode({
        "client_id": config["STEGVERSE_MAIL_CLIENT_ID"],
        "client_secret": config["STEGVERSE_MAIL_CLIENT_SECRET"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Microsoft identity HTTP {exc.code}: {raw[:1000]}") from exc
    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Microsoft identity response did not contain an access token")
    return token


def first_page_url(mailbox: str, page_size: int) -> str:
    mailbox_part = urllib.parse.quote(mailbox, safe="@._+-")
    params = urllib.parse.urlencode({
        "$select": "id,conversationId,subject,receivedDateTime,internetMessageId,bodyPreview,from",
        "$orderby": "receivedDateTime desc",
        "$top": str(page_size),
    })
    return f"https://graph.microsoft.com/v1.0/users/{mailbox_part}/mailFolders/inbox/messages?{params}"


def parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_failure_message(message: dict[str, Any], start: datetime, end: datetime) -> bool:
    received = message.get("receivedDateTime")
    subject = str(message.get("subject") or "")
    sender = (((message.get("from") or {}).get("emailAddress") or {}).get("address") or "").lower()
    if not isinstance(received, str):
        return False
    timestamp = parse_dt(received)
    return (
        start <= timestamp < end
        and sender == SENDER
        and ("Run failed:" in subject or "PR run failed:" in subject)
    )


def stable_id(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def sanitize(message: dict[str, Any]) -> dict[str, Any]:
    raw_id = str(message.get("id") or "")
    raw_thread = str(message.get("conversationId") or "")
    internet_id = str(message.get("internetMessageId") or "")
    return {
        "id": stable_id(raw_id),
        "thread_id": stable_id(raw_thread) if raw_thread else "",
        "internet_message_id": stable_id(internet_id) if internet_id else "",
        "email_ts": str(message.get("receivedDateTime") or ""),
        "subject": str(message.get("subject") or ""),
        "snippet": str(message.get("bodyPreview") or ""),
        "body": "",
        "transport": "ara-microsoft-graph-legacy-authorized-for-healer",
        "mailbox_mutated": False,
    }


def collect_messages(*, token: str, mailbox: str, start: datetime, end: datetime, page_size: int, max_pages: int) -> list[dict[str, Any]]:
    url = first_page_url(mailbox, page_size)
    matched: list[dict[str, Any]] = []
    pages = 0
    while url and pages < max_pages:
        status, payload = request_json(url, token=token)
        if status != 200:
            raise RuntimeError(f"unexpected mailbox list status: {status}")
        pages += 1
        values = payload.get("value", [])
        if not isinstance(values, list):
            raise RuntimeError("Graph mailbox response value is not a list")
        oldest: datetime | None = None
        for item in values:
            if not isinstance(item, dict):
                continue
            received = item.get("receivedDateTime")
            if isinstance(received, str):
                timestamp = parse_dt(received)
                oldest = timestamp if oldest is None or timestamp < oldest else oldest
            if is_failure_message(item, start, end):
                matched.append(item)
        if oldest is not None and oldest < start:
            break
        next_link = payload.get("@odata.nextLink")
        url = str(next_link) if isinstance(next_link, str) and next_link else ""
    if url and pages >= max_pages:
        raise RuntimeError("mailbox pagination exceeded max_pages before bounded window was exhausted")
    return matched


def write_outputs(batch_path: Path, manifest_path: Path, rows: list[dict[str, Any]], *, start: datetime, end: datetime) -> dict[str, Any]:
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    sanitized = [sanitize(row) for row in sorted(rows, key=lambda x: str(x.get("receivedDateTime") or ""))]
    with batch_path.open("w", encoding="utf-8") as handle:
        for row in sanitized:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    batch_sha = hashlib.sha256(batch_path.read_bytes()).hexdigest()
    batch_id = f"graph-{start.strftime('%Y%m%dT%H%M%SZ')}-{end.strftime('%Y%m%dT%H%M%SZ')}"
    manifest = {
        "schema": "stegverse.healer.ara-graph-failure-intake/v0.1",
        "batch_id": batch_id,
        "window_start": iso_z(start),
        "window_end": iso_z(end),
        "source_count": len(rows),
        "materialized_count": len(sanitized),
        "source_ref": "microsoft-graph://inbox/github-actions-failure-notifications",
        "batch_sha256": batch_sha,
        "credential_transport": "ARA_GITHUB_ACTIONS_SECRETS_SCOPED_EXCEPTION",
        "credential_value_exported": False,
        "mailbox_mutated": False,
        "mark_read": False,
        "archive": False,
        "delete": False,
        "label_mutation": False,
        "authority_effect": False,
        "heartbeat_effect": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--window-minutes", type=int, default=20)
    parser.add_argument("--lag-minutes", type=int, default=2)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--require-config", action="store_true")
    args = parser.parse_args()
    if args.window_minutes < 1 or args.window_minutes > 120:
        raise ValueError("window-minutes must be between 1 and 120")
    if args.lag_minutes < 0 or args.lag_minutes > 30:
        raise ValueError("lag-minutes must be between 0 and 30")

    config, state = configuration()
    if state == "not_configured":
        print("HEALER_FAILURE_MAILBOX_POLL=NOT_CONFIGURED")
        return 1 if args.require_config else 0

    token = get_access_token(config)
    end = utc_now() - timedelta(minutes=args.lag_minutes)
    start = end - timedelta(minutes=args.window_minutes)
    messages = collect_messages(
        token=token,
        mailbox=config["STEGVERSE_MONITOR_MAILBOX"],
        start=start,
        end=end,
        page_size=max(1, min(args.page_size, 100)),
        max_pages=max(1, args.max_pages),
    )
    manifest = write_outputs(args.batch, args.manifest, messages, start=start, end=end)
    print(json.dumps({"result": "PASS", **manifest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
