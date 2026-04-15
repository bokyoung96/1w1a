from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from .config import ArasConfig
from .domain import ReportRecord
from .storage import SqliteArasStore


class TelegramBotClient(Protocol):
    def get_updates(self, *, offset: int | None, limit: int) -> list[dict[str, Any]]: ...

    def get_file(self, file_id: str) -> dict[str, str]: ...

    def download_file(self, file_path: str) -> bytes: ...


class TelegramChannelClient(Protocol):
    def get_latest_message_id(self, *, channel: str) -> int | None: ...

    def iter_channel_messages(
        self,
        *,
        channel: str,
        after_message_id: int | None,
        limit: int,
    ) -> list[dict[str, Any]]: ...

    def download_document(self, message: dict[str, Any]) -> bytes: ...


@dataclass(frozen=True)
class FetchBatch:
    downloaded: list[ReportRecord] = field(default_factory=list)
    skipped_duplicates: list[dict[str, Any]] = field(default_factory=list)
    ignored_updates: list[int] = field(default_factory=list)
    next_offset: int | None = None


class TelegramFetcher:
    def __init__(self, *, client: TelegramBotClient | TelegramChannelClient, store: SqliteArasStore, config: ArasConfig) -> None:
        self.client = client
        self.store = store
        self.config = config

    def poll_once(self, *, channel: str) -> FetchBatch:
        if self._supports_telethon_channel_crawl():
            return self._poll_channel_once(channel=channel)
        return self._poll_bot_updates_once(channel=channel)

    def _poll_bot_updates_once(self, *, channel: str) -> FetchBatch:
        offset = self.store.get_next_update_offset()
        updates = self.client.get_updates(offset=offset, limit=self.config.polling_limit)
        downloaded: list[ReportRecord] = []
        skipped_duplicates: list[dict[str, Any]] = []
        ignored_updates: list[int] = []
        safe_next_offset = offset

        for update in sorted(updates, key=lambda item: item["update_id"]):
            parsed = self._extract_pdf_message(update, expected_channel=channel)
            if parsed is None:
                ignored_updates.append(update["update_id"])
                safe_next_offset = update["update_id"] + 1
                continue

            file_unique_id = parsed["document"]["file_unique_id"]
            if self.store.has_seen_file(file_unique_id):
                skipped_duplicates.append(update)
                safe_next_offset = update["update_id"] + 1
                continue

            file_id = parsed["document"]["file_id"]
            file_info = self.client.get_file(file_id)
            file_bytes = self.client.download_file(file_info["file_path"])
            pdf_path = self._write_pdf(
                update_id=update["update_id"],
                file_unique_id=file_unique_id,
                file_name=parsed["document"].get("file_name"),
                payload=file_bytes,
            )
            report = ReportRecord(
                id=None,
                source="telegram",
                channel=channel,
                message_id=parsed["message_id"],
                published_at=self._format_timestamp(parsed.get("date")),
                title=parsed.get("caption") or Path(parsed["document"].get("file_name", "report.pdf")).stem,
                pdf_path=pdf_path,
                content="",
                metadata={
                    "file_unique_id": file_unique_id,
                    "telegram_file_id": file_id,
                    "telegram_file_path": file_info["file_path"],
                    "telegram_update_id": update["update_id"],
                },
            )
            inserted = self.store.record_download(report)
            if inserted:
                downloaded.append(report)
            else:
                skipped_duplicates.append(update)
            safe_next_offset = update["update_id"] + 1

        if safe_next_offset is not None:
            self.store.set_next_update_offset(safe_next_offset)

        return FetchBatch(
            downloaded=downloaded,
            skipped_duplicates=skipped_duplicates,
            ignored_updates=ignored_updates,
            next_offset=safe_next_offset,
        )

    def _poll_channel_once(self, *, channel: str) -> FetchBatch:
        last_seen_message_id = self.store.get_last_seen_message_id(channel)
        if last_seen_message_id is None:
            latest_message_id = self.client.get_latest_message_id(channel=channel)
            if latest_message_id is not None:
                self.store.set_last_seen_message_id(channel, latest_message_id)
            return FetchBatch(next_offset=latest_message_id)

        messages = self.client.iter_channel_messages(
            channel=channel,
            after_message_id=last_seen_message_id,
            limit=self.config.polling_limit,
        )
        downloaded: list[ReportRecord] = []
        skipped_duplicates: list[dict[str, Any]] = []
        ignored_updates: list[int] = []
        safe_last_seen_message_id = last_seen_message_id

        try:
            for message in sorted(messages, key=lambda item: item["message_id"]):
                parsed = self._extract_pdf_message(message, expected_channel=channel)
                message_id = int(message["message_id"])
                if parsed is None:
                    ignored_updates.append(message_id)
                    safe_last_seen_message_id = message_id
                    continue

                file_unique_id = parsed["document"]["file_unique_id"]
                if self.store.has_seen_file(file_unique_id):
                    skipped_duplicates.append(message)
                    safe_last_seen_message_id = message_id
                    continue

                file_bytes = self.client.download_document(parsed)
                pdf_path = self._write_pdf(
                    update_id=message_id,
                    file_unique_id=file_unique_id,
                    file_name=parsed["document"].get("file_name"),
                    payload=file_bytes,
                )
                report = ReportRecord(
                    id=None,
                    source="telegram",
                    channel=channel,
                    message_id=message_id,
                    published_at=self._format_timestamp(parsed.get("date")),
                    title=parsed.get("caption") or Path(parsed["document"].get("file_name", "report.pdf")).stem,
                    pdf_path=pdf_path,
                    content="",
                    metadata={
                        "file_unique_id": file_unique_id,
                        "telegram_file_id": parsed["document"]["file_id"],
                        "telegram_message_id": message_id,
                    },
                )
                inserted = self.store.record_download(report)
                if inserted:
                    downloaded.append(report)
                else:
                    skipped_duplicates.append(message)
                safe_last_seen_message_id = message_id
        except Exception:
            if safe_last_seen_message_id != last_seen_message_id:
                self.store.set_last_seen_message_id(channel, safe_last_seen_message_id)
            raise

        if safe_last_seen_message_id is not None:
            self.store.set_last_seen_message_id(channel, safe_last_seen_message_id)

        return FetchBatch(
            downloaded=downloaded,
            skipped_duplicates=skipped_duplicates,
            ignored_updates=ignored_updates,
            next_offset=safe_last_seen_message_id,
        )

    @staticmethod
    def _extract_pdf_message(update: dict[str, Any], *, expected_channel: str) -> dict[str, Any] | None:
        payload = update.get("channel_post") or update.get("message") or update
        if not payload:
            return None
        chat = payload.get("chat") or {}
        if chat.get("title") != expected_channel:
            return None
        document = payload.get("document")
        if not document:
            return None
        file_name = str(document.get("file_name", ""))
        mime_type = str(document.get("mime_type", ""))
        if mime_type != "application/pdf" and not file_name.lower().endswith(".pdf"):
            return None
        return payload

    def _write_pdf(self, *, update_id: int, file_unique_id: str, file_name: str | None, payload: bytes) -> Path:
        safe_name = (file_name or "report.pdf").replace("/", "-")
        target = self.config.paths.raw_dir / f"{update_id}-{file_unique_id}-{safe_name}"
        target.write_bytes(payload)
        return target

    @staticmethod
    def _format_timestamp(timestamp: int | None) -> str | None:
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")

    def _supports_telethon_channel_crawl(self) -> bool:
        return all(
            hasattr(self.client, attribute)
            for attribute in ("get_latest_message_id", "iter_channel_messages", "download_document")
        )
