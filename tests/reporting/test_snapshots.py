from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from backtesting.reporting.analytics import annualized_sharpe
from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository
from backtesting.reporting.models import BenchmarkConfig, SavedRun
from backtesting.reporting.snapshots import PerformanceSnapshotFactory


_DEFAULT = object()


def test_performance_snapshot_factory_builds_analytics_snapshot() -> None:
    run = _toy_run()
    factory = PerformanceSnapshotFactory(
        benchmark_repo=BenchmarkRepository.from_frame(_benchmark_prices()),
        sector_repo=SectorRepository.from_frame(_sector_map()),
    )

    snapshot = factory.build(run, BenchmarkConfig.default_kospi200())

    assert snapshot.run_id == "toy-run"
    assert snapshot.display_name == "Toy Strategy"
    assert snapshot.metrics.cagr > 0.0
    assert snapshot.metrics.beta is not None
    assert "rolling_sharpe" in snapshot.rolling.series
    assert "rolling_beta" in snapshot.rolling.series
    assert_series_equal(snapshot.rolling.series["rolling_sharpe"].index.to_series(), run.returns.index.to_series())
    assert_series_equal(snapshot.rolling.series["rolling_beta"].index.to_series(), run.returns.index.to_series())
    assert snapshot.exposure.holdings_count.iloc[-1] == 2
    assert len(snapshot.exposure.latest_holdings) == 2
    assert snapshot.sectors.latest_weighted.to_dict() == {"Tech": 0.6, "Utilities": 0.4}
    assert snapshot.sectors.latest_count.to_dict() == {"Tech": 1.0, "Utilities": 1.0}
    assert snapshot.drawdowns.episodes["drawdown"].lt(0.0).any()
    expected_sortino = _expected_sortino(run.returns)
    assert snapshot.metrics.sortino >= 0.0
    assert snapshot.metrics.sortino == expected_sortino


def test_performance_snapshot_factory_derives_latest_holdings_when_optional_table_missing() -> None:
    run = _toy_run(latest_weights=None)
    factory = PerformanceSnapshotFactory(
        benchmark_repo=BenchmarkRepository.from_frame(_benchmark_prices()),
        sector_repo=SectorRepository.from_frame(_sector_map()),
    )

    snapshot = factory.build(run, BenchmarkConfig.default_kospi200())

    expected = pd.DataFrame(
        {
            "symbol": ["A", "B"],
            "target_weight": [0.6, 0.4],
            "abs_weight": [0.6, 0.4],
        }
    )
    assert_frame_equal(snapshot.exposure.latest_holdings.reset_index(drop=True), expected)


def test_performance_snapshot_factory_uses_fixed_252_day_rolling_window() -> None:
    run = _long_run()
    factory = PerformanceSnapshotFactory(
        benchmark_repo=BenchmarkRepository.from_frame(_long_benchmark_prices(run.equity.index)),
        sector_repo=SectorRepository.from_frame(_long_sector_map(run.equity.index.max())),
    )

    snapshot = factory.build(run, BenchmarkConfig.default_kospi200())

    expected_sharpe = annualized_sharpe(run.returns)
    assert snapshot.rolling.series["rolling_sharpe"].iloc[-1] == expected_sharpe


def _toy_run(latest_weights: pd.DataFrame | None | object = _DEFAULT) -> SavedRun:
    index = pd.date_range("2024-01-02", periods=8, freq="D")
    equity = pd.Series([100.0, 102.0, 101.0, 105.0, 103.0, 106.0, 108.0, 110.0], index=index, name="equity")
    returns = equity.pct_change().fillna(0.0).rename("returns")
    turnover = pd.Series([0.0, 0.1, 0.05, 0.08, 0.03, 0.07, 0.02, 0.01], index=index, name="turnover")
    weights = pd.DataFrame(
        {
            "A": [0.5, 0.5, 0.0, 0.6, 0.6, 0.6, 0.6, 0.6],
            "B": [0.5, 0.4, 0.7, 0.4, 0.4, 0.0, 0.0, 0.4],
            "C": [0.0, 0.1, 0.3, 0.0, 0.0, 0.4, 0.4, 0.0],
        },
        index=index,
    )
    if latest_weights is _DEFAULT:
        latest_weights = pd.DataFrame(
            {
                "symbol": ["A", "B"],
                "target_weight": [0.6, 0.4],
                "abs_weight": [0.6, 0.4],
            }
        )
    qty = pd.DataFrame(
        {
            "A": [5, 5, 0, 6, 6, 6, 6, 6],
            "B": [5, 4, 7, 4, 4, 0, 0, 4],
            "C": [0, 1, 3, 0, 0, 4, 4, 0],
        },
        index=index,
    ).astype(float)

    return SavedRun(
        run_id="toy-run",
        path=Path("/tmp/toy-run"),
        config={"name": "Toy Strategy", "strategy": "momentum"},
        summary={},
        equity=equity,
        returns=returns,
        turnover=turnover,
        weights=weights,
        qty=qty,
        latest_weights=latest_weights,
    )


def _benchmark_prices() -> pd.DataFrame:
    index = pd.date_range("2024-01-02", periods=8, freq="D")
    return pd.DataFrame(
        {
            "IKS200": [200.0, 201.0, 200.5, 202.0, 201.0, 202.5, 203.0, 204.0],
        },
        index=index,
    )


def _sector_map() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "A": ["Tech"],
            "B": ["Utilities"],
            "C": ["Health Care"],
        },
        index=pd.to_datetime(["2024-01-09"]),
    )


def _long_run() -> SavedRun:
    index = pd.date_range("2024-01-02", periods=30, freq="D")
    returns = pd.Series([0.0] + [0.01] * 15 + [-0.02] * 14, index=index, name="returns")
    equity = (1.0 + returns).cumprod().mul(100.0).rename("equity")
    turnover = pd.Series(0.05, index=index, name="turnover")
    weights = pd.DataFrame({"A": 0.6, "B": 0.4, "C": 0.0}, index=index)
    qty = pd.DataFrame({"A": 6.0, "B": 4.0, "C": 0.0}, index=index)

    return SavedRun(
        run_id="long-run",
        path=Path("/tmp/long-run"),
        config={"name": "Long Strategy", "strategy": "momentum"},
        summary={},
        equity=equity,
        returns=returns,
        turnover=turnover,
        weights=weights,
        qty=qty,
        latest_weights=None,
    )


def _long_benchmark_prices(index: pd.DatetimeIndex) -> pd.DataFrame:
    returns = pd.Series([0.0] + [0.004] * (len(index) - 1), index=index)
    prices = (1.0 + returns).cumprod().mul(200.0)
    return pd.DataFrame({"IKS200": prices}, index=index)


def _long_sector_map(latest_date: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {"A": ["Tech"], "B": ["Utilities"], "C": ["Health Care"]},
        index=pd.DatetimeIndex([latest_date]),
    )


def _expected_sortino(returns: pd.Series) -> float:
    downside = returns.clip(upper=0.0)
    downside_deviation = float((downside.pow(2).mean() ** 0.5) * (252.0**0.5))
    if downside_deviation == 0.0:
        return 0.0
    return float(returns.mean() * 252.0 / downside_deviation)
