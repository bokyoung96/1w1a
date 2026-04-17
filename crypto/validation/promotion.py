from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import pandas as pd


@dataclass(frozen=True, slots=True)
class PromotionThresholds:
    oos_sharpe: float
    paper_sharpe: float
    max_drawdown: float
    minimum_paper_days: int
    max_pairwise_correlation: float


@dataclass(frozen=True, slots=True)
class PromotionMetrics:
    oos_sharpe: float
    paper_sharpe: float
    max_drawdown: float
    paper_days: int
    pairwise_correlation: float


@dataclass(frozen=True, slots=True)
class ValidationReport:
    ready: bool
    metrics: PromotionMetrics
    thresholds: PromotionThresholds
    failed_checks: dict[str, str]


@dataclass(frozen=True, slots=True)
class OverlapDiagnostics:
    correlation_matrix: pd.DataFrame
    violating_pairs: list[tuple[str, str, float]]
    max_pairwise_correlation: float


DEFAULT_PROMOTION_THRESHOLDS = PromotionThresholds(
    oos_sharpe=0.75,
    paper_sharpe=0.5,
    max_drawdown=0.15,
    minimum_paper_days=30,
    max_pairwise_correlation=0.70,
)



def evaluate_promotion_readiness(
    metrics: PromotionMetrics,
    thresholds: PromotionThresholds,
) -> ValidationReport:
    failed_checks: dict[str, str] = {}
    if metrics.oos_sharpe <= thresholds.oos_sharpe:
        failed_checks["oos_sharpe"] = f"must be > {thresholds.oos_sharpe:.2f}"
    if metrics.paper_sharpe <= thresholds.paper_sharpe:
        failed_checks["paper_sharpe"] = f"must be > {thresholds.paper_sharpe:.1f}"
    if metrics.max_drawdown >= thresholds.max_drawdown:
        failed_checks["max_drawdown"] = f"must be < {thresholds.max_drawdown:.2f}"
    if metrics.paper_days < thresholds.minimum_paper_days:
        failed_checks["paper_days"] = f"must be >= {thresholds.minimum_paper_days}"
    if metrics.pairwise_correlation >= thresholds.max_pairwise_correlation:
        failed_checks["pairwise_correlation"] = (
            f"must be < {thresholds.max_pairwise_correlation:.2f}"
        )

    return ValidationReport(
        ready=not failed_checks,
        metrics=metrics,
        thresholds=thresholds,
        failed_checks=failed_checks,
    )



def pairwise_correlation_diagnostics(
    returns: pd.DataFrame,
    threshold: float,
) -> OverlapDiagnostics:
    correlation_matrix = returns.corr().sort_index(axis=0).sort_index(axis=1)

    violating_pairs: list[tuple[str, str, float]] = []
    max_pairwise_correlation = 0.0
    for left, right in combinations(correlation_matrix.columns, 2):
        value = float(correlation_matrix.loc[left, right])
        max_pairwise_correlation = max(max_pairwise_correlation, abs(value))
        if value >= threshold:
            pair = tuple(sorted((left, right)))
            violating_pairs.append((pair[0], pair[1], value))

    violating_pairs.sort(key=lambda item: (item[0], item[1]))
    return OverlapDiagnostics(
        correlation_matrix=correlation_matrix,
        violating_pairs=violating_pairs,
        max_pairwise_correlation=max_pairwise_correlation,
    )
