from pathlib import Path

import pandas as pd

from backtesting.reporting.reader import RunReader


def test_run_reader_loads_saved_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "sample-run"
    series_dir = run_dir / "series"
    positions_dir = run_dir / "positions"
    run_dir.mkdir()
    series_dir.mkdir()
    positions_dir.mkdir()

    (run_dir / "config.json").write_text(
        '{"strategy":"momentum","start":"2024-01-01","end":"2024-01-31"}',
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        '{"cagr":0.1,"mdd":-0.2,"sharpe":1.2,"final_equity":110.0,"avg_turnover":0.05}',
        encoding="utf-8",
    )
    pd.Series([100.0, 110.0], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), name="equity").to_csv(
        series_dir / "equity.csv",
        index_label="date",
    )
    pd.Series([0.0, 0.1], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), name="returns").to_csv(
        series_dir / "returns.csv",
        index_label="date",
    )
    pd.Series([0.0, 0.05], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), name="turnover").to_csv(
        series_dir / "turnover.csv",
        index_label="date",
    )
    pd.DataFrame({"A": [1.0]}, index=pd.to_datetime(["2024-01-03"])).to_parquet(positions_dir / "weights.parquet")
    pd.DataFrame({"A": [10.0]}, index=pd.to_datetime(["2024-01-03"])).to_parquet(positions_dir / "qty.parquet")

    run = RunReader().read(run_dir)

    assert run.run_id == "sample-run"
    assert run.summary["final_equity"] == 110.0
    assert list(run.equity.index) == list(pd.to_datetime(["2024-01-02", "2024-01-03"]))
