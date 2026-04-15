from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Awaitable, Callable, Protocol

from .domain import ReportRecord

_ACCEPTED_AT_KEY = "_accepted_at"


@dataclass(frozen=True)
class WatchMessageResult:
    status: str
    report: ReportRecord | None = None


@dataclass(frozen=True)
class AsyncWatchResult:
    seen: int = 0
    downloaded: int = 0
    duplicates: int = 0
    ignored: int = 0
    summarized: int = 0
    summarize_failures: int = 0
    summarize_retries: int = 0


class AsyncWatchClient(Protocol):
    async def watch_channel(
        self,
        *,
        channel: str,
        until: datetime,
        on_message: Callable[[dict[str, Any]], Awaitable[None] | None],
    ) -> None: ...


class MessageIngestor(Protocol):
    def ingest_message(self, *, channel: str, message: dict[str, Any]) -> WatchMessageResult: ...


class ReportPipeline(Protocol):
    def summarize_report(self, report: ReportRecord): ...


class WatchUntilRunner:
    def __init__(
        self,
        *,
        client: AsyncWatchClient,
        message_ingestor: MessageIngestor,
        pipeline: ReportPipeline,
        now_fn: Callable[[], datetime] = datetime.now,
        summarize_retry_limit: int = 1,
        heartbeat_interval_seconds: float = 15.0,
        logger: logging.Logger | None = None,
    ) -> None:
        self.client = client
        self.message_ingestor = message_ingestor
        self.pipeline = pipeline
        self.now_fn = now_fn
        self.summarize_retry_limit = summarize_retry_limit
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self.logger = logger or logging.getLogger("analysts.watch")

    async def watch_until(self, *, channel: str, until: datetime) -> AsyncWatchResult:
        if until.tzinfo is None:
            raise ValueError("watch-until requires a timezone-aware deadline")
        if self._normalize_now(until=until) >= until:
            return AsyncWatchResult()

        counts = self._new_counts()
        self.logger.info("watch_started channel=%s until=%s", channel, until.isoformat())
        stop_heartbeat = asyncio.Event()

        async def on_message(message: dict[str, Any]) -> None:
            await self._handle_message(channel=channel, message=message, until=until, counts=counts)

        heartbeat_task = asyncio.create_task(self._heartbeat(channel=channel, until=until, counts=counts, stop=stop_heartbeat))
        try:
            await self._await_watch(channel=channel, until=until, on_message=on_message)
        finally:
            stop_heartbeat.set()
            await heartbeat_task
        self.logger.info(
            "watch_finished channel=%s seen=%s downloaded=%s duplicates=%s ignored=%s summarized=%s retries=%s failures=%s",
            channel,
            counts["seen"],
            counts["downloaded"],
            counts["duplicates"],
            counts["ignored"],
            counts["summarized"],
            counts["summarize_retries"],
            counts["summarize_failures"],
        )
        return AsyncWatchResult(**counts)

    async def _await_watch(
        self,
        *,
        channel: str,
        until: datetime,
        on_message: Callable[[dict[str, Any]], Awaitable[None] | None],
    ) -> None:
        maybe_awaitable = self.client.watch_channel(channel=channel, until=until, on_message=on_message)
        if inspect.isawaitable(maybe_awaitable):
            await maybe_awaitable

    def _normalize_now(self, *, until: datetime) -> datetime:
        current = self.now_fn()
        if current.tzinfo is None:
            return current.replace(tzinfo=until.tzinfo)
        return current.astimezone(until.tzinfo)

    @staticmethod
    def _new_counts() -> dict[str, int]:
        return {
            "seen": 0,
            "downloaded": 0,
            "duplicates": 0,
            "ignored": 0,
            "summarized": 0,
            "summarize_failures": 0,
            "summarize_retries": 0,
        }

    async def _handle_message(
        self,
        *,
        channel: str,
        message: dict[str, Any],
        until: datetime,
        counts: dict[str, int],
    ) -> None:
        if not self._was_accepted_before_deadline(message=message, until=until):
            self.logger.info("watch_message status=ignored_after_deadline channel=%s message_id=%s", channel, message.get("message_id"))
            return
        counts["seen"] += 1
        result = self.message_ingestor.ingest_message(channel=channel, message=message)
        if result.status == "duplicate":
            counts["duplicates"] += 1
            self.logger.info("watch_message status=duplicate channel=%s message_id=%s", channel, message.get("message_id"))
            return
        if result.status == "existing_unsummarized" and result.report is not None:
            counts["duplicates"] += 1
            self.logger.info("watch_message status=existing_unsummarized channel=%s message_id=%s", channel, result.report.message_id)
            self._summarize_report(report=result.report, counts=counts)
            return
        if result.status == "ignored" or result.report is None:
            counts["ignored"] += 1
            self.logger.info("watch_message status=ignored channel=%s message_id=%s", channel, message.get("message_id"))
            return

        counts["downloaded"] += 1
        self.logger.info("watch_message status=downloaded channel=%s message_id=%s", channel, result.report.message_id)
        self._summarize_report(report=result.report, counts=counts)

    def _summarize_report(self, *, report: ReportRecord, counts: dict[str, int]) -> None:
        for attempt in range(self.summarize_retry_limit + 1):
            try:
                self.pipeline.summarize_report(report)
                counts["summarized"] += 1
                self.logger.info("watch_summary_ok message_id=%s", report.message_id)
                return
            except Exception:
                if attempt < self.summarize_retry_limit:
                    counts["summarize_retries"] += 1
                    self.logger.warning("watch_retry message_id=%s attempt=%s", report.message_id, attempt + 1)
                    continue
                counts["summarize_failures"] += 1
                self.logger.exception("watch_summary_failed message_id=%s", report.message_id)

    def _was_accepted_before_deadline(self, *, message: dict[str, Any], until: datetime) -> bool:
        accepted_at = self._accepted_at(message=message, until=until)
        if accepted_at is None:
            return self._normalize_now(until=until) < until
        return accepted_at < until

    @staticmethod
    def _accepted_at(*, message: dict[str, Any], until: datetime) -> datetime | None:
        value = message.get(_ACCEPTED_AT_KEY)
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=until.tzinfo)
        return value.astimezone(until.tzinfo)

    async def _heartbeat(
        self,
        *,
        channel: str,
        until: datetime,
        counts: dict[str, int],
        stop: asyncio.Event,
    ) -> None:
        if self.heartbeat_interval_seconds <= 0:
            return
        while True:
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.heartbeat_interval_seconds)
                return
            except asyncio.TimeoutError:
                self.logger.info(
                    "watch_heartbeat channel=%s until=%s seen=%s downloaded=%s duplicates=%s ignored=%s summarized=%s retries=%s failures=%s",
                    channel,
                    until.isoformat(),
                    counts["seen"],
                    counts["downloaded"],
                    counts["duplicates"],
                    counts["ignored"],
                    counts["summarized"],
                    counts["summarize_retries"],
                    counts["summarize_failures"],
                )
