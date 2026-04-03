from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import pandas as pd


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
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


@dataclass(frozen=True, slots=True)
class RollingMetrics:
    series: dict[str, pd.Series]


@dataclass(frozen=True, slots=True)
class DrawdownStats:
    underwater: pd.Series
    episodes: pd.DataFrame


@dataclass(frozen=True, slots=True)
class ExposureSnapshot:
    holdings_count: pd.Series
    latest_holdings: pd.DataFrame


@dataclass(frozen=True, slots=True)
class SectorSnapshot:
    latest_weighted: pd.Series
    latest_count: pd.Series
    concentration: pd.Series


def annualized_sharpe(returns: pd.Series, periods: int = 252) -> float:
    clean = returns.dropna().astype(float)
    if len(clean) < 2:
        return 0.0

    volatility = float(clean.std(ddof=0))
    if abs(volatility) < 1e-12:
        return 0.0
    return float(clean.mean() / volatility * sqrt(periods))
