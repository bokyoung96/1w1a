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


class ValuePointModel(DashboardBaseModel):
    date: str
    value: float


class NamedSeriesModel(DashboardBaseModel):
    run_id: str
    label: str
    points: list[ValuePointModel]


class HoldingModel(DashboardBaseModel):
    symbol: str
    target_weight: float
    abs_weight: float


class CategoryPointModel(DashboardBaseModel):
    name: str
    value: float


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
    benchmark: list[ValuePointModel] | None
    drawdowns: list[NamedSeriesModel]


class DashboardRollingModel(DashboardBaseModel):
    rolling_sharpe: list[NamedSeriesModel]
    rolling_beta: list[NamedSeriesModel]


class DashboardExposureModel(DashboardBaseModel):
    holdings_count: list[NamedSeriesModel]
    latest_holdings: dict[str, list[HoldingModel]]
    sector_weights: dict[str, list[CategoryPointModel]]


class DashboardPayloadModel(DashboardBaseModel):
    mode: str
    selected_run_ids: list[str]
    available_runs: list[RunOptionModel]
    metrics: dict[str, DashboardMetricModel]
    context: dict[str, DashboardContextModel]
    performance: DashboardPerformanceModel
    rolling: DashboardRollingModel
    exposure: DashboardExposureModel
