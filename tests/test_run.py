from pathlib import Path

import pandas as pd

import run as root_run
from backtesting.catalog import DataCatalog
from backtesting.data import ParquetStore
from backtesting.run import BacktestRunner, RunConfig, main as backtesting_main


def test_runner_executes_momentum_strategy(tmp_path: Path) -> None:
    parquet_dir = tmp_path / "parquet"
    raw_dir = tmp_path / "raw"
    result_dir = tmp_path / "results"
    parquet_dir.mkdir()
    raw_dir.mkdir()
    store = ParquetStore(parquet_dir)
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    store.write("qw_adj_c", pd.DataFrame({"A": [10.0, 11.0, 12.0], "B": [10.0, 10.0, 9.0]}, index=index))
    store.write("qw_adj_o", pd.DataFrame({"A": [10.0, 11.0, 12.0], "B": [10.0, 10.0, 9.0]}, index=index))
    store.write("qw_k200_yn", pd.DataFrame({"A": [1, 1, 1], "B": [1, 1, 1]}, index=index))

    runner = BacktestRunner(
        catalog=DataCatalog.default(),
        raw_dir=raw_dir,
        parquet_dir=parquet_dir,
        result_dir=result_dir,
    )
    report = runner.run(
        RunConfig(
            strategy="momentum",
            start="2024-01-02",
            end="2024-01-04",
            top_n=1,
            lookback=1,
            schedule="daily",
            fill_mode="close",
        )
    )

    assert report.summary["final_equity"] > 0.0
    assert report.result.weights.loc["2024-01-04", "A"] == 1.0
    assert report.output_dir is not None
    assert (report.output_dir / "config.json").exists()
    assert (report.output_dir / "summary.json").exists()
    assert (report.output_dir / "series" / "equity.csv").exists()
    assert (report.output_dir / "series" / "monthly_returns.csv").exists()
    assert (report.output_dir / "positions" / "latest_qty.csv").exists()
    assert (report.output_dir / "plots" / "equity.png").exists()
    assert (report.output_dir / "plots" / "drawdown.png").exists()


def test_runner_executes_op_fwd_strategy(tmp_path: Path) -> None:
    parquet_dir = tmp_path / "parquet"
    raw_dir = tmp_path / "raw"
    result_dir = tmp_path / "results"
    parquet_dir.mkdir()
    raw_dir.mkdir()
    store = ParquetStore(parquet_dir)
    daily = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    monthly = pd.to_datetime(["2024-01-31"])
    store.write("qw_adj_c", pd.DataFrame({"A": [10.0, 10.5, 11.0], "B": [10.0, 9.8, 9.7]}, index=daily))
    store.write("qw_adj_o", pd.DataFrame({"A": [10.0, 10.5, 11.0], "B": [10.0, 9.8, 9.7]}, index=daily))
    store.write("qw_k200_yn", pd.DataFrame({"A": [1, 1, 1], "B": [1, 1, 1]}, index=daily))
    store.write("qw_mktcap", pd.DataFrame({"A": [10.0, 10.0, 10.0], "B": [10.0, 10.0, 10.0]}, index=daily))
    store.write("qw_op_nfy1", pd.DataFrame({"A": [20.0], "B": [5.0]}, index=monthly))

    runner = BacktestRunner(
        catalog=DataCatalog.default(),
        raw_dir=raw_dir,
        parquet_dir=parquet_dir,
        result_dir=result_dir,
    )
    report = runner.run(
        RunConfig(
            strategy="op_fwd_yield",
            start="2024-01-02",
            end="2024-01-04",
            top_n=1,
            schedule="daily",
            fill_mode="close",
        )
    )

    assert report.summary["final_equity"] > 0.0
    assert report.result.weights.iloc[-1]["A"] == 1.0
    assert report.output_dir is not None
    assert (report.output_dir / "positions" / "qty.parquet").exists()


def test_root_run_delegates_to_backtesting_main() -> None:
    assert root_run.main is backtesting_main
