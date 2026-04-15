from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .agents import AnalystCoordinator
from .config import ArasConfig
from .domain import PipelineExecution, PipelineRunSummary, ReportRecord
from .fetcher import TelegramFetcher
from .parser import DocumentParser
from .router import TaskRouter
from .signal import SignalEngine
from .storage import SqliteArasStore
from .wiki import WikiBuilder


@dataclass(frozen=True)
class ArasPipeline:
    client: Any
    store: SqliteArasStore
    config: ArasConfig

    def run_once(self, *, channel: str) -> PipelineExecution:
        fetcher = TelegramFetcher(client=self.client, store=self.store, config=self.config)
        parser = DocumentParser()
        router = TaskRouter()
        coordinator = AnalystCoordinator()
        wiki = WikiBuilder(base_dir=self.config.paths.base_dir)
        signals = SignalEngine(base_dir=self.config.paths.base_dir)

        batch = fetcher.poll_once(channel=channel)
        insights = []
        for report in batch.downloaded:
            stored_report = self._hydrate_report(report)
            parsed = parser.parse(stored_report)
            routes = router.route(parsed)
            insights.extend(
                coordinator.build_insights(parsed, routes, source_document_id=stored_report.id or 0)
            )

        wiki_pages: list[Path] = []
        signal_files: list[Path] = []
        if insights:
            wiki_result = wiki.materialize(insights)
            signal_result = signals.generate(insights)
            wiki_pages = wiki_result.page_paths
            signal_files = signal_result.snapshot_paths

        return PipelineExecution(
            summary=PipelineRunSummary(
                downloaded=len(batch.downloaded),
                duplicates=len(batch.skipped_duplicates),
                ignored=len(batch.ignored_updates),
                next_offset=batch.next_offset,
            ),
            wiki_pages=wiki_pages,
            signal_files=signal_files,
        )

    def _hydrate_report(self, report: ReportRecord) -> ReportRecord:
        file_unique_id = str(report.metadata["file_unique_id"])
        for stored in self.store.list_reports():
            if str(stored.metadata.get("file_unique_id")) == file_unique_id:
                return stored
        return report
