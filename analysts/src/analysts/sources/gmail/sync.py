from __future__ import annotations

from base64 import urlsafe_b64decode
from dataclasses import dataclass
from typing import Any

from .models import GmailMessageRecord
from .storage import GmailStore


@dataclass(frozen=True)
class GmailSyncResult:
    fetched: int
    skipped_existing: int
    last_history_id: str | None


class GmailPollingSync:
    def __init__(self, *, api: Any, store: GmailStore, account_name: str, query: str) -> None:
        self.api = api
        self.store = store
        self.account_name = account_name
        self.query = query

    def sync_once(self, *, limit: int) -> GmailSyncResult:
        listed = self.api.list_message_ids(query=self.query, limit=limit)
        fetched = 0
        skipped_existing = 0
        last_history_id: str | None = None

        for item in listed.get("messages", []):
            message_id = item["id"]
            if self.store.get_message(message_id) is not None:
                skipped_existing += 1
                continue
            payload = self.api.get_message(message_id=message_id)
            record = build_message_record(account_name=self.account_name, query=self.query, payload=payload)
            self.store.record_message(record)
            fetched += 1
            last_history_id = payload.get("historyId") or last_history_id

        if fetched or last_history_id is not None:
            self.store.set_sync_state(
                account_name=self.account_name,
                last_history_id=last_history_id,
                full_sync_required=False,
            )
        return GmailSyncResult(
            fetched=fetched,
            skipped_existing=skipped_existing,
            last_history_id=last_history_id,
        )


def build_message_record(*, account_name: str, query: str, payload: dict[str, Any]) -> GmailMessageRecord:
    headers = {
        header.get("name", "").lower(): header.get("value")
        for header in (payload.get("payload", {}).get("headers") or [])
    }
    body_plain = _extract_body_text(payload.get("payload", {}))
    return GmailMessageRecord(
        gmail_message_id=str(payload["id"]),
        gmail_thread_id=str(payload["threadId"]),
        history_id=str(payload.get("historyId") or ""),
        account_name=account_name,
        subject=str(headers.get("subject") or ""),
        sender=headers.get("from"),
        internal_date=str(payload.get("internalDate")) if payload.get("internalDate") is not None else None,
        label_ids=tuple(str(item) for item in payload.get("labelIds", [])),
        snippet=str(payload.get("snippet") or ""),
        body_plain=body_plain,
        body_html=None,
        raw_payload_json=payload,
        sync_status="synced",
        query_fingerprint=query,
    )


def _extract_body_text(message_part: dict[str, Any]) -> str | None:
    body = message_part.get("body") or {}
    data = body.get("data")
    if data:
        padded = data + "=" * (-len(data) % 4)
        return urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
    for child in message_part.get("parts", []) or []:
        child_text = _extract_body_text(child)
        if child_text:
            return child_text
    return None
