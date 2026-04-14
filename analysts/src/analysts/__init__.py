"""ARAS analysts package."""

from .config import ArasConfig, ArasPaths, build_config
from .domain import (
    InsightRecord,
    ParseQuality,
    ParsedDocument,
    PipelineRunSummary,
    ReportRecord,
    RouteDecision,
    SignalSnapshot,
)
from .fetcher import FetchBatch, TelegramFetcher
from .pipeline import ArasPipeline
from .signal import SignalEngine, SignalGenerationResult
from .storage import SqliteArasStore
from .wiki import WikiBuilder, WikiMaterializationResult

__all__ = [
    "ArasConfig",
    "ArasPaths",
    "ArasPipeline",
    "FetchBatch",
    "InsightRecord",
    "ParseQuality",
    "ParsedDocument",
    "PipelineRunSummary",
    "ReportRecord",
    "RouteDecision",
    "SignalEngine",
    "SignalGenerationResult",
    "SignalSnapshot",
    "SqliteArasStore",
    "TelegramFetcher",
    "WikiBuilder",
    "WikiMaterializationResult",
    "build_config",
]
