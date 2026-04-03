from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .analytics import (
    DrawdownStats,
    ExposureSnapshot,
    PerformanceMetrics,
    RollingMetrics,
    SectorSnapshot,
    annualized_sharpe,
)
from .benchmarks import BenchmarkRepository, SectorRepository
from .models import BenchmarkConfig, SavedRun


@dataclass(frozen=True, slots=True)
class PerformanceSnapshot:
    run_id: str
    display_name: str
    metrics: PerformanceMetrics
    rolling: RollingMetrics
    drawdowns: DrawdownStats
    exposure: ExposureSnapshot
    sectors: SectorSnapshot
    strategy_equity: pd.Series
    strategy_returns: pd.Series
    benchmark_returns: pd.Series
    benchmark_equity: pd.Series


class PerformanceSnapshotFactory:
    def __init__(self, benchmark_repo: BenchmarkRepository, sector_repo: SectorRepository) -> None:
        self.benchmark_repo = benchmark_repo
        self.sector_repo = sector_repo

    def build(self, run: SavedRun, benchmark: BenchmarkConfig) -> PerformanceSnapshot:
        strategy_returns = run.returns.astype(float).sort_index()
        strategy_equity = run.equity.astype(float).sort_index()
        benchmark_series = self.benchmark_repo.load_series(
            benchmark,
            start=str(strategy_returns.index.min().date()),
            end=str(strategy_returns.index.max().date()),
        )
        benchmark_returns = benchmark_series.returns.reindex(strategy_returns.index).fillna(0.0).astype(float)
        benchmark_equity = self._equity_from_returns(benchmark_returns, starting_value=float(strategy_equity.iloc[0]))

        rolling = self._build_rolling_metrics(strategy_returns, benchmark_returns)
        drawdowns = self._build_drawdowns(strategy_equity)
        exposure = self._build_exposure(run)
        sectors = self._build_sectors(run.weights)
        metrics = self._build_metrics(run, strategy_returns, strategy_equity, benchmark_returns, drawdowns.underwater)

        return PerformanceSnapshot(
            run_id=run.run_id,
            display_name=str(run.config.get("name") or run.run_id),
            metrics=metrics,
            rolling=rolling,
            drawdowns=drawdowns,
            exposure=exposure,
            sectors=sectors,
            strategy_equity=strategy_equity,
            strategy_returns=strategy_returns,
            benchmark_returns=benchmark_returns,
            benchmark_equity=benchmark_equity,
        )

    def _build_metrics(
        self,
        run: SavedRun,
        strategy_returns: pd.Series,
        strategy_equity: pd.Series,
        benchmark_returns: pd.Series,
        underwater: pd.Series,
    ) -> PerformanceMetrics:
        active_returns = strategy_returns.sub(benchmark_returns, fill_value=0.0)
        benchmark_variance = float(benchmark_returns.var(ddof=0))
        covariance = float(strategy_returns.cov(benchmark_returns, ddof=0))
        beta = 0.0 if abs(benchmark_variance) < 1e-12 else covariance / benchmark_variance
        alpha = float((strategy_returns.mean() - beta * benchmark_returns.mean()) * 252.0)
        annual_volatility = float(strategy_returns.std(ddof=0) * (252.0**0.5)) if len(strategy_returns) > 1 else 0.0
        downside = strategy_returns.loc[strategy_returns.lt(0.0)]
        downside_volatility = float(downside.std(ddof=0) * (252.0**0.5)) if len(downside) > 0 else 0.0
        tracking_error = float(active_returns.std(ddof=0) * (252.0**0.5)) if len(active_returns) > 1 else 0.0
        information_ratio = 0.0 if abs(tracking_error) < 1e-12 else float(active_returns.mean() * 252.0 / tracking_error)
        cumulative_return = float(strategy_equity.iloc[-1] / strategy_equity.iloc[0] - 1.0)
        cagr = self._cagr(strategy_equity)
        max_drawdown = float(underwater.min()) if not underwater.empty else 0.0
        sortino = 0.0 if abs(downside_volatility) < 1e-12 else float(strategy_returns.mean() * 252.0 / downside_volatility)
        calmar = 0.0 if max_drawdown >= 0.0 else float(cagr / abs(max_drawdown))

        return PerformanceMetrics(
            cumulative_return=cumulative_return,
            cagr=cagr,
            annual_volatility=annual_volatility,
            sharpe=annualized_sharpe(strategy_returns),
            sortino=sortino,
            calmar=calmar,
            max_drawdown=max_drawdown,
            final_equity=float(strategy_equity.iloc[-1]),
            avg_turnover=float(run.turnover.fillna(0.0).mean()),
            alpha=alpha,
            beta=float(beta),
            tracking_error=tracking_error,
            information_ratio=information_ratio,
        )

    def _build_rolling_metrics(self, strategy_returns: pd.Series, benchmark_returns: pd.Series) -> RollingMetrics:
        window = max(3, min(20, len(strategy_returns)))
        rolling_sharpe = strategy_returns.rolling(window=window, min_periods=2).apply(
            lambda values: annualized_sharpe(pd.Series(values)),
            raw=False,
        )
        benchmark_variance = benchmark_returns.rolling(window=window, min_periods=2).var(ddof=0)
        rolling_beta = strategy_returns.rolling(window=window, min_periods=2).cov(benchmark_returns, ddof=0).div(
            benchmark_variance
        )
        rolling_beta = rolling_beta.replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
        return RollingMetrics(
            series={
                "rolling_sharpe": rolling_sharpe.rename("rolling_sharpe"),
                "rolling_beta": rolling_beta.rename("rolling_beta"),
            }
        )

    def _build_drawdowns(self, equity: pd.Series) -> DrawdownStats:
        peak = equity.cummax()
        underwater = equity.div(peak).sub(1.0).rename("underwater")
        records: list[dict[str, object]] = []
        in_drawdown = False
        start = trough = None
        trough_value = 0.0

        for date, value in underwater.items():
            value = float(value)
            if value < 0.0 and not in_drawdown:
                start = trough = date
                trough_value = value
                in_drawdown = True
            elif value < 0.0 and in_drawdown and value <= trough_value:
                trough = date
                trough_value = value
            elif value >= 0.0 and in_drawdown:
                records.append(
                    {
                        "start": start,
                        "trough": trough,
                        "end": date,
                        "drawdown": trough_value,
                    }
                )
                in_drawdown = False

        if in_drawdown:
            records.append(
                {
                    "start": start,
                    "trough": trough,
                    "end": equity.index[-1],
                    "drawdown": trough_value,
                }
            )

        episodes = pd.DataFrame.from_records(records, columns=["start", "trough", "end", "drawdown"])
        return DrawdownStats(underwater=underwater, episodes=episodes)

    def _build_exposure(self, run: SavedRun) -> ExposureSnapshot:
        holdings_count = run.weights.fillna(0.0).ne(0.0).sum(axis=1).rename("holdings_count")
        latest_holdings = run.latest_weights.copy() if run.latest_weights is not None else pd.DataFrame()
        return ExposureSnapshot(holdings_count=holdings_count.astype(float), latest_holdings=latest_holdings)

    def _build_sectors(self, weights: pd.DataFrame) -> SectorSnapshot:
        latest_weighted = self.sector_repo.latest_sector_weights(weights)
        latest_weighted = latest_weighted.loc[latest_weighted.ne(0.0)]
        latest_date = weights.index.max()
        latest_weight_row = weights.loc[:latest_date].iloc[-1].astype(float)
        latest_sector_row = self.sector_repo.sector.loc[:latest_date].iloc[-1]

        counts = (
            pd.DataFrame(
                {
                    "sector": latest_sector_row.reindex(latest_weight_row.index),
                    "weight": latest_weight_row,
                }
            )
            .loc[lambda frame: frame["weight"].ne(0.0)]
            .dropna(subset=["sector"])
            .groupby("sector", sort=False)
            .size()
            .astype(float)
            .rename("count")
        )
        concentration = latest_weighted.abs().sort_values(ascending=False).rename("concentration")
        return SectorSnapshot(latest_weighted=latest_weighted, latest_count=counts, concentration=concentration)

    @staticmethod
    def _equity_from_returns(returns: pd.Series, starting_value: float) -> pd.Series:
        return (1.0 + returns.fillna(0.0)).cumprod().mul(starting_value).rename("benchmark_equity")

    @staticmethod
    def _cagr(equity: pd.Series, periods: int = 252) -> float:
        if len(equity) < 2:
            return 0.0

        starting = float(equity.iloc[0])
        ending = float(equity.iloc[-1])
        if starting <= 0.0 or ending <= 0.0:
            return 0.0

        years = len(equity) / float(periods)
        if years <= 0.0:
            return 0.0
        return float((ending / starting) ** (1.0 / years) - 1.0)
