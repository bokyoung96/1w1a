from pathlib import Path

import pandas as pd

from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository
from backtesting.reporting.models import BenchmarkConfig, SavedRun
from backtesting.reporting.snapshots import PerformanceSnapshotFactory


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
    assert snapshot.exposure.holdings_count.iloc[-1] == 2
    assert len(snapshot.exposure.latest_holdings) == 2
    assert snapshot.sectors.latest_weighted.to_dict() == {"Tech": 0.6, "Utilities": 0.4}
    assert snapshot.drawdowns.episodes["drawdown"].lt(0.0).any()


def _toy_run() -> SavedRun:
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
