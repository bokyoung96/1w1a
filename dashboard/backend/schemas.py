from __future__ import annotations

from pydantic import BaseModel, ConfigDict


def _to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class DashboardBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)


class RunSummaryModel(DashboardBaseModel):
    final_equity: float
    avg_turnover: float


class RunOptionModel(DashboardBaseModel):
    run_id: str
    label: str
    strategy: str
    start: str | None = None
    end: str | None = None
    summary: RunSummaryModel


class BenchmarkModel(DashboardBaseModel):
    code: str
    name: str


class LaunchStrategyBenchmarkModel(DashboardBaseModel):
    strategy: str
    label: str
    benchmark: BenchmarkModel


class LaunchBenchmarkContextModel(DashboardBaseModel):
    kind: str
    shared: BenchmarkModel | None = None
    strategies: list[LaunchStrategyBenchmarkModel]


class DashboardLaunchModel(DashboardBaseModel):
    configured_start_date: str | None = None
    configured_end_date: str | None = None
    capital: float | None = None
    schedule: str | None = None
    fill_mode: str | None = None
    fee: float | None = None
    sell_tax: float | None = None
    slippage: float | None = None
    benchmark: LaunchBenchmarkContextModel | None = None
    as_of_date: str | None = None


class ValuePointModel(DashboardBaseModel):
    date: str
    value: float


class NamedSeriesModel(DashboardBaseModel):
    run_id: str
    label: str
    points: list[ValuePointModel]


class RollingSeriesModel(NamedSeriesModel):
    benchmark: BenchmarkModel
    window: int


class CategorySeriesModel(DashboardBaseModel):
    name: str
    points: list[ValuePointModel]


class HoldingModel(DashboardBaseModel):
    symbol: str
    target_weight: float
    abs_weight: float


class HoldingPerformanceModel(HoldingModel):
    return_since_latest_rebalance: float


class CategoryPointModel(DashboardBaseModel):
    name: str
    value: float


class HeatmapCellModel(DashboardBaseModel):
    year: int
    month: int
    value: float


class DistributionBinModel(DashboardBaseModel):
    start: float
    end: float
    count: int
    frequency: float


class DrawdownEpisodeModel(DashboardBaseModel):
    peak: str
    start: str
    trough: str
    end: str
    drawdown: float
    duration_days: int
    time_to_trough_days: int
    recovery_days: int | None = None
    recovered: bool


class ResearchFocusModel(DashboardBaseModel):
    kind: str
    label: str
    value: str | None = None


class DashboardMetricModel(DashboardBaseModel):
    label: str
    cumulative_return: float
    cagr: float
    annual_volatility: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown: float
    final_equity: float
    avg_turnover: float
    alpha: float
    beta: float
    tracking_error: float
    information_ratio: float


class DashboardContextModel(DashboardBaseModel):
    label: str
    strategy: str
    benchmark: BenchmarkModel
    start_date: str
    end_date: str
    as_of_date: str


class DashboardPerformanceModel(DashboardBaseModel):
    series: list[NamedSeriesModel]
    benchmark: list[ValuePointModel] | None = None
    benchmarks: list[NamedSeriesModel]
    drawdowns: list[NamedSeriesModel]


class DashboardRollingModel(DashboardBaseModel):
    rolling_sharpe: list[NamedSeriesModel]
    rolling_beta: list[NamedSeriesModel]
    rolling_correlation: list[RollingSeriesModel]


class DashboardExposureModel(DashboardBaseModel):
    holdings_count: list[NamedSeriesModel]
    latest_holdings: dict[str, list[HoldingModel]]
    latest_holdings_winners: dict[str, list[HoldingPerformanceModel]]
    latest_holdings_losers: dict[str, list[HoldingPerformanceModel]]
    sector_weights: dict[str, list[CategoryPointModel]]


class DashboardResearchModel(DashboardBaseModel):
    focus: ResearchFocusModel
    sector_contribution_method: str
    monthly_heatmap: dict[str, list[HeatmapCellModel]]
    return_distribution: dict[str, list[DistributionBinModel]]
    monthly_return_distribution: dict[str, list[DistributionBinModel]]
    yearly_excess_returns: dict[str, list[ValuePointModel]]
    sector_contribution_series: dict[str, list[CategorySeriesModel]]
    sector_weight_series: dict[str, list[CategorySeriesModel]]
    drawdown_episodes: dict[str, list[DrawdownEpisodeModel]]


class CryptoFactoryExecutionStageModel(DashboardBaseModel):
    stage: str
    fraction: float
    target_weight: float


class CryptoFactorySelectedStrategyModel(DashboardBaseModel):
    candidate_id: str
    strategy_name: str
    family: str
    primary_cadence: str
    feature_cadences: list[str]
    total_score: float
    max_pairwise_correlation: float
    target_weight: float
    documentation_path: str
    rationale_excerpt: str
    execution_stages: list[CryptoFactoryExecutionStageModel]


class CryptoFactoryFamilyAllocationModel(DashboardBaseModel):
    family: str
    weight: float
    strategy_count: int


class CryptoFactoryInstrumentAllocationModel(DashboardBaseModel):
    instrument_symbol: str
    net_target_weight: float
    gross_target_weight: float
    contributor_count: int


class CryptoFactoryRegistryEntryModel(DashboardBaseModel):
    name: str
    family: str
    primary_cadence: str
    feature_cadences: list[str]
    candidate_count: int
    selected: bool
    top_score: float
    documentation_path: str
    rationale_excerpt: str


class CryptoFactorySummaryModel(DashboardBaseModel):
    candidate_pool_size: int
    selected_basket_size: int
    registered_strategy_count: int
    family_cap: int
    trigger_reason: str


class CryptoFactoryPerformanceSummaryModel(DashboardBaseModel):
    total_return: float
    max_drawdown: float
    paper_sharpe: float
    paper_days: int
    realized_fees: float
    net_funding: float


class CryptoFactoryPerformanceModel(DashboardBaseModel):
    equity_curve: list[ValuePointModel]
    drawdown_curve: list[ValuePointModel]
    gross_exposure_curve: list[ValuePointModel]
    net_exposure_curve: list[ValuePointModel]


class CryptoFactoryPayloadModel(DashboardBaseModel):
    summary: CryptoFactorySummaryModel
    performance_summary: CryptoFactoryPerformanceSummaryModel
    performance: CryptoFactoryPerformanceModel
    selected_basket: list[CryptoFactorySelectedStrategyModel]
    family_allocations: list[CryptoFactoryFamilyAllocationModel]
    instrument_allocations: list[CryptoFactoryInstrumentAllocationModel]
    registry: list[CryptoFactoryRegistryEntryModel]


class DashboardPayloadModel(DashboardBaseModel):
    mode: str
    selected_run_ids: list[str]
    available_runs: list[RunOptionModel]
    launch: DashboardLaunchModel
    metrics: dict[str, DashboardMetricModel]
    context: dict[str, DashboardContextModel]
    performance: DashboardPerformanceModel
    rolling: DashboardRollingModel
    exposure: DashboardExposureModel
    research: DashboardResearchModel
    crypto_factory: CryptoFactoryPayloadModel | None = None


class SessionBootstrapModel(DashboardBaseModel):
    default_selected_run_ids: list[str]
