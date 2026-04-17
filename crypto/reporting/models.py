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
class ExecutionStageReport:
    stage: str
    fraction: float
    target_weight: float


@dataclass(frozen=True, slots=True)
class SelectedStrategyReportEntry:
    candidate_id: str
    strategy_name: str
    family: str
    instrument_symbol: str
    primary_cadence: str
    feature_cadences: tuple[str, ...]
    total_score: float
    max_pairwise_correlation: float
    target_weight: float
    execution_stages: tuple[ExecutionStageReport, ...]


@dataclass(frozen=True, slots=True)
class FamilyAllocationReportEntry:
    family: str
    weight: float
    strategy_count: int


@dataclass(frozen=True, slots=True)
class InstrumentAllocationReportEntry:
    instrument_symbol: str
    net_target_weight: float
    gross_target_weight: float
    contributor_count: int


@dataclass(frozen=True, slots=True)
class FactoryResearchOverview:
    candidate_pool_size: int
    trigger_reason: str
    selected_basket: tuple[SelectedStrategyReportEntry, ...]
    family_allocations: tuple[FamilyAllocationReportEntry, ...]
    instrument_allocations: tuple[InstrumentAllocationReportEntry, ...]


@dataclass(frozen=True, slots=True)
class PaperPerformanceReport:
    metadata: ReportMetadata
    summary: PerformanceSummary
    graphs: tuple[GraphSeries, ...]
    thresholds: PromotionThresholds
    registered_strategies: tuple[StrategyCatalogEntry, ...]
    factory_overview: FactoryResearchOverview | None = None
