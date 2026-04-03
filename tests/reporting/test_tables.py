from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from backtesting.reporting.models import SavedRun
from backtesting.reporting.tables import (
    build_appendix_table,
    build_latest_qty_table,
    build_latest_weights_table,
    build_summary_table,
)


def test_build_summary_table_compares_runs() -> None:
    index = pd.to_datetime(["2024-01-02"])
    run_a = SavedRun(
        run_id="a",
        path=Path("a"),
        config={"strategy": "momentum"},
        summary={"cagr": 0.2, "mdd": -0.1, "sharpe": 1.1, "final_equity": 120.0, "avg_turnover": 0.05},
        equity=pd.Series([120.0], index=index),
        returns=pd.Series([0.0], index=index),
        turnover=pd.Series([0.05], index=index),
        weights=pd.DataFrame({"A": [1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0]}, index=index),
    )
    run_b = SavedRun(
        run_id="b",
        path=Path("b"),
        config={"strategy": "op_fwd_yield"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 0.9, "final_equity": 110.0, "avg_turnover": 0.02},
        equity=pd.Series([110.0], index=index),
        returns=pd.Series([0.0], index=index),
        turnover=pd.Series([0.02], index=index),
        weights=pd.DataFrame({"A": [1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0]}, index=index),
    )

    table = build_summary_table([run_a, run_b])

    assert list(table["run_id"]) == ["a", "b"]
    assert "cagr" in table.columns
    assert table.loc[1, "strategy"] == "op_fwd_yield"


def test_build_latest_weights_table_uses_latest_non_zero_row() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="a",
        path=Path("a"),
        config={"strategy": "momentum"},
        summary={},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [0.0, -0.25], "B": [0.5, 0.75]}, index=index),
        qty=pd.DataFrame({"A": [0.0, 2.0], "B": [0.0, -5.0]}, index=index),
    )

    table = build_latest_weights_table(run)

    expected = pd.DataFrame(
        {
            "symbol": ["B", "A"],
            "target_weight": [0.75, -0.25],
            "abs_weight": [0.75, 0.25],
        }
    )
    assert_frame_equal(table, expected)


def test_build_latest_qty_table_uses_latest_non_zero_row() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="a",
        path=Path("a"),
        config={"strategy": "momentum"},
        summary={},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [0.0, -0.25], "B": [0.5, 0.75]}, index=index),
        qty=pd.DataFrame({"A": [0.0, 2.0], "B": [0.0, -5.0]}, index=index),
    )

    table = build_latest_qty_table(run)

    expected = pd.DataFrame(
        {
            "symbol": ["B", "A"],
            "qty": [-5.0, 2.0],
            "abs_qty": [5.0, 2.0],
        }
    )
    assert_frame_equal(table, expected)


def test_build_appendix_table_lists_run_metadata() -> None:
    index = pd.to_datetime(["2024-01-02"])
    run = SavedRun(
        run_id="a",
        path=Path("runs/a"),
        config={"strategy": "momentum", "start": "2024-01-01", "end": "2024-01-31"},
        summary={},
        equity=pd.Series([100.0], index=index),
        returns=pd.Series([0.0], index=index),
        turnover=pd.Series([0.0], index=index),
        weights=pd.DataFrame({"A": [1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0]}, index=index),
    )

    table = build_appendix_table([run])

    expected = pd.DataFrame(
        [
            {
                "run_id": "a",
                "path": str(Path("runs/a")),
                "strategy": "momentum",
                "start": "2024-01-01",
                "end": "2024-01-31",
            }
        ]
    )
    assert_frame_equal(table, expected)
