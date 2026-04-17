from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from crypto.validation import PromotionThresholds


@dataclass(frozen=True, slots=True)
class GraphPoint:
    at: datetime
    value: float


@dataclass(frozen=True, slots=True)
class GraphSeries:
    slug: str
    label: str
    points: tuple[GraphPoint, ...]


@dataclass(frozen=True, slots=True)
class StrategyCatalogEntry:
    name: str
    family: str
    primary_cadence: str
    feature_cadences: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReportMetadata:
    session_id: str
    strategy_id: str
    exchange_id: str
    primary_cadence: str
    feature_cadences: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PerformanceSummary:
    total_return: float
    max_drawdown: float
    paper_sharpe: float
    paper_days: int
    realized_fees: float
    net_funding: float
    max_peer_correlation: float | None


@dataclass(frozen=True, slots=True)
class PaperPerformanceReport:
    metadata: ReportMetadata
    summary: PerformanceSummary
    graphs: tuple[GraphSeries, ...]
    thresholds: PromotionThresholds
    registered_strategies: tuple[StrategyCatalogEntry, ...]
