from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class ParseQuality(StrEnum):
    HIGH = "high"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class ReportRecord:
    id: int | None
    source: str
    channel: str
    message_id: int
    published_at: str | None
    title: str
    pdf_path: Path
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParsedDocument:
    title: str
    content: str
    sections: list[str]
    entities: list[str]
    tickers: list[str]
    routes: list[str]
    parse_quality: ParseQuality
    degraded_reason: str | None = None


@dataclass(frozen=True)
class RouteDecision:
    topic: str
    lane: str
    rationale: str


@dataclass(frozen=True)
class InsightRecord:
    topic: str
    lane: str
    summary: str
    bull_case: str
    bear_case: str
    confidence: str
    key_drivers: list[str]
    risk_factors: list[str]
    source_document_id: int


@dataclass(frozen=True)
class SignalSnapshot:
    topic: str
    repeated_keywords: list[str]
    sentiment_delta: str
    conflict_flags: list[str]


@dataclass(frozen=True)
class PipelineRunSummary:
    downloaded: int
    duplicates: int
    ignored: int
    next_offset: int | None


@dataclass(frozen=True)
class PipelineExecution:
    summary: PipelineRunSummary
    wiki_pages: list[Path]
    signal_files: list[Path]
