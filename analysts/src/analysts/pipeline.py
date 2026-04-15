from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import ArasConfig
from .domain import AnalystSummary, PipelineExecution, PipelineRunSummary, ReportRecord
from .extraction import SummaryReadyExtractor
from .fetcher import TelegramFetcher
from .parser import DocumentParser
from .router import TaskRouter
from .storage import SqliteArasStore
from .summarizer import CodexAnalystSummarizer


@dataclass(frozen=True)
class ArasPipeline:
    client: Any
    store: SqliteArasStore
    config: ArasConfig
    summarizer: CodexAnalystSummarizer | None = None
    extractor: SummaryReadyExtractor | None = None

    def run_once(self, *, channel: str) -> PipelineExecution:
        fetcher = TelegramFetcher(client=self.client, store=self.store, config=self.config)
        batch = fetcher.poll_once(channel=channel)
        processed_files: list[Path] = []
        summaries: list[AnalystSummary] = []

        for report in batch.downloaded:
            stored_report = self._hydrate_report(report)
            result = self.summarize_report(stored_report)
            processed_files.extend(result.processed_files)
            summaries.extend(result.summaries)

        return PipelineExecution(
            summary=PipelineRunSummary(
                downloaded=len(batch.downloaded),
                duplicates=len(batch.skipped_duplicates),
                ignored=len(batch.ignored_updates),
                next_offset=batch.next_offset,
            ),
            processed_files=processed_files,
            summaries=summaries,
        )

    def summarize_latest(self, *, channel: str) -> PipelineExecution:
        report = self.store.get_latest_report(channel)
        if report is None:
            raise RuntimeError(f"No stored report found for channel {channel}")
        return self.summarize_report(report)

    def summarize_report(self, report: ReportRecord) -> PipelineExecution:
        parser = DocumentParser()
        router = TaskRouter()
        extractor = self.extractor or SummaryReadyExtractor(self.config)
        summarizer = self.summarizer or CodexAnalystSummarizer(config=self.config, base_dir=self.config.paths.base_dir)

        parsed = parser.parse(report)
        routes = router.route(parsed)
        packet = extractor.build_packet(report=report, parsed=parsed, routes=routes)
        artifacts = extractor.write_artifacts(packet)
        summaries = [
            summarizer.summarize(packet=packet, lane=lane, topic=topic)
            for lane, topic in summarizer.lane_plan(packet)
        ]
        summary_json_path, summary_md_path = self._write_summary_outputs(packet=packet, summaries=summaries)

        return PipelineExecution(
            summary=PipelineRunSummary(downloaded=0, duplicates=0, ignored=0, next_offset=report.message_id),
            processed_files=[artifacts.raw_text_path, artifacts.summary_input_path, summary_json_path, summary_md_path],
            summaries=summaries,
        )

    def _hydrate_report(self, report: ReportRecord) -> ReportRecord:
        file_unique_id = str(report.metadata["file_unique_id"])
        for stored in self.store.list_reports():
            if str(stored.metadata.get("file_unique_id")) == file_unique_id:
                return stored
        return report

    def _write_summary_outputs(self, *, packet, summaries: list[AnalystSummary]) -> tuple[Path, Path]:
        slug = f"report-{packet.source_document_id or packet.message_id}"
        json_path = self.config.paths.processed_dir / f"{slug}-summary.json"
        md_path = self.config.paths.processed_dir / f"{slug}-summary.md"
        payload = {
            "report_title": packet.report_title,
            "message_id": packet.message_id,
            "published_at": packet.published_at,
            "raw_pdf_path": str(packet.raw_pdf_path),
            "extraction_quality": packet.extraction_quality,
            "extraction_reason": packet.extraction_reason,
            "route_hints": packet.route_hints,
            "summaries": [
                {
                    "lane": summary.lane,
                    "topic": summary.topic,
                    "headline": summary.headline,
                    "executive_summary": summary.executive_summary,
                    "key_points": summary.key_points,
                    "risks": summary.risks,
                    "confidence": summary.confidence,
                    "follow_up_questions": summary.follow_up_questions,
                }
                for summary in summaries
            ],
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        lines = [
            f"# {packet.report_title}",
            "",
            f"- Message ID: {packet.message_id}",
            f"- Published at: {packet.published_at}",
            f"- Raw PDF: `{packet.raw_pdf_path}`",
            f"- Extraction quality: {packet.extraction_quality}",
            f"- Extraction reason: {packet.extraction_reason}",
            "",
        ]
        for summary in summaries:
            lines.extend(
                [
                    f"## {summary.lane.title()} analyst",
                    f"- Topic: {summary.topic}",
                    f"- Confidence: {summary.confidence}",
                    f"- Headline: {summary.headline}",
                    "",
                    summary.executive_summary,
                    "",
                    "### Key points",
                    *[f"- {item}" for item in summary.key_points],
                    "",
                    "### Risks",
                    *[f"- {item}" for item in summary.risks],
                    "",
                    "### Follow-up questions",
                    *[f"- {item}" for item in summary.follow_up_questions],
                    "",
                ]
            )
        md_path.write_text("\n".join(lines).rstrip() + "\n")
        return json_path, md_path
