from __future__ import annotations

from math import sqrt
from statistics import mean
from typing import Iterable, Mapping, Sequence

from crypto.domain import timeframe_to_timedelta
from crypto.paper import PaperSession
from crypto.reporting.models import (
    GraphPoint,
    GraphSeries,
    PaperPerformanceReport,
    PerformanceSummary,
    ReportMetadata,
    StrategyCatalogEntry,
)
from crypto.strategies import DEFAULT_STRATEGIES, StrategyDefinition
from crypto.validation import DEFAULT_PROMOTION_THRESHOLDS, PromotionThresholds


def build_strategy_catalog(
    strategy_definitions: Iterable[StrategyDefinition],
) -> tuple[StrategyCatalogEntry, ...]:
    return tuple(
        StrategyCatalogEntry(
            name=strategy.name,
            family=strategy.family,
            primary_cadence=strategy.primary_cadence,
            feature_cadences=strategy.feature_cadences,
        )
        for strategy in strategy_definitions
    )


def build_paper_performance_report(
    session: PaperSession,
    *,
    strategy_definitions: Iterable[StrategyDefinition] = DEFAULT_STRATEGIES,
    thresholds: PromotionThresholds = DEFAULT_PROMOTION_THRESHOLDS,
    peer_returns: Mapping[str, Sequence[float]] | None = None,
) -> PaperPerformanceReport:
    if not session.equity_entries:
        raise ValueError("paper reporting requires at least one equity observation")

    equity_points = tuple(
        GraphPoint(at=entry.timestamp, value=float(entry.equity or 0.0))
        for entry in session.equity_entries
    )
    drawdown_points = _drawdown_points(equity_points)
    gross_points = tuple(
        GraphPoint(at=entry.timestamp, value=float(entry.gross_exposure or 0.0))
        for entry in session.equity_entries
    )
    net_points = tuple(
        GraphPoint(at=entry.timestamp, value=float(entry.net_exposure or 0.0))
        for entry in session.equity_entries
    )
    returns = _period_returns([point.value for point in equity_points])

    summary = PerformanceSummary(
        total_return=_total_return(equity_points),
        max_drawdown=max((point.value for point in drawdown_points), default=0.0),
        paper_sharpe=_annualized_sharpe(returns, timeframe=session.primary_cadence),
        paper_days=session.paper_days,
        realized_fees=session.realized_fees,
        net_funding=session.net_funding,
        max_peer_correlation=_max_peer_correlation(returns, peer_returns or {}),
    )
    metadata = ReportMetadata(
        session_id=session.session_id,
        strategy_id=session.strategy_id,
        exchange_id=session.exchange_id,
        primary_cadence=session.primary_cadence,
        feature_cadences=session.feature_cadences,
    )

    return PaperPerformanceReport(
        metadata=metadata,
        summary=summary,
        graphs=(
            GraphSeries(slug="equity_curve", label="Equity Curve", points=equity_points),
            GraphSeries(slug="drawdown_curve", label="Drawdown Curve", points=drawdown_points),
            GraphSeries(
                slug="gross_exposure_curve",
                label="Gross Exposure",
                points=gross_points,
            ),
            GraphSeries(
                slug="net_exposure_curve",
                label="Net Exposure",
                points=net_points,
            ),
        ),
        thresholds=thresholds,
        registered_strategies=build_strategy_catalog(strategy_definitions),
    )


def _drawdown_points(points: Sequence[GraphPoint]) -> tuple[GraphPoint, ...]:
    running_peak = 0.0
    drawdowns: list[GraphPoint] = []
    for point in points:
        running_peak = max(running_peak, point.value)
        if running_peak <= 0:
            drawdown = 0.0
        else:
            drawdown = 1.0 - (point.value / running_peak)
        drawdowns.append(GraphPoint(at=point.at, value=drawdown))
    return tuple(drawdowns)


def _period_returns(values: Sequence[float]) -> tuple[float, ...]:
    returns: list[float] = []
    for previous, current in zip(values, values[1:]):
        if previous == 0:
            returns.append(0.0)
            continue
        returns.append((current / previous) - 1.0)
    return tuple(returns)


def _total_return(points: Sequence[GraphPoint]) -> float:
    starting_equity = points[0].value
    ending_equity = points[-1].value
    if starting_equity == 0:
        return 0.0
    return (ending_equity / starting_equity) - 1.0


def _annualized_sharpe(returns: Sequence[float], *, timeframe: str) -> float:
    if len(returns) < 2:
        return 0.0
    average = mean(returns)
    variance = sum((value - average) ** 2 for value in returns) / (len(returns) - 1)
    if variance <= 0:
        return 0.0
    period_seconds = timeframe_to_timedelta(timeframe).total_seconds()
    periods_per_year = (365.0 * 24.0 * 60.0 * 60.0) / period_seconds
    return (average / sqrt(variance)) * sqrt(periods_per_year)


def _max_peer_correlation(
    base_returns: Sequence[float],
    peer_returns: Mapping[str, Sequence[float]],
) -> float | None:
    correlations: list[float] = []
    for peer_series in peer_returns.values():
        correlation = _correlation(base_returns, tuple(peer_series))
        if correlation is not None:
            correlations.append(correlation)
    if not correlations:
        return None
    return max(correlations)


def _correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean = mean(left)
    right_mean = mean(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    numerator = sum(a * b for a, b in zip(left_centered, right_centered))
    left_norm = sqrt(sum(value * value for value in left_centered))
    right_norm = sqrt(sum(value * value for value in right_centered))
    denominator = left_norm * right_norm
    if denominator == 0:
        return None
    return numerator / denominator
