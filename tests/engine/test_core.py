import pandas as pd
import pytest

from backtesting.engine.core import BacktestEngine
from backtesting.execution.costs import CostModel


def test_engine_tracks_equity_from_weights() -> None:
    close = pd.DataFrame(
        {
            "A": [100.0, 110.0],
            "B": [100.0, 90.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    weights = pd.DataFrame(
        {
            "A": [0.5, 0.5],
            "B": [0.5, 0.5],
        },
        index=close.index,
    )

    engine = BacktestEngine(cost=CostModel())
    result = engine.run(close=close, weights=weights, capital=1000.0, fill_mode="close")

    assert result.equity.iloc[0] == 1000.0
    assert round(result.equity.iloc[-1], 2) == 1000.0


def test_engine_requires_open_for_next_open_mode() -> None:
    close = pd.DataFrame(
        {"A": [100.0, 101.0]},
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    weights = pd.DataFrame(
        {"A": [1.0, 1.0]},
        index=close.index,
    )

    engine = BacktestEngine(cost=CostModel())

    with pytest.raises(ValueError, match="open prices required for next_open"):
        engine.run(close=close, weights=weights, capital=1000.0, fill_mode="next_open")


def test_engine_close_mode_works_without_open() -> None:
    close = pd.DataFrame(
        {"A": [100.0, 110.0]},
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    weights = pd.DataFrame(
        {"A": [1.0, 1.0]},
        index=close.index,
    )

    engine = BacktestEngine(cost=CostModel())
    result = engine.run(close=close, weights=weights, capital=1000.0, fill_mode="close")

    assert result.equity.tolist() == [1000.0, 1100.0]


def test_engine_uses_next_open_fill_prices() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    close = pd.DataFrame({"A": [100.0, 110.0, 120.0]}, index=index)
    open_ = pd.DataFrame({"A": [95.0, 100.0, 115.0]}, index=index)
    weights = pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=index)

    engine = BacktestEngine(cost=CostModel())
    result = engine.run(
        close=close,
        open=open_,
        weights=weights,
        capital=1000.0,
        fill_mode="next_open",
    )

    assert result.equity.tolist() == [1000.0, 1100.0, 1200.0]
    assert result.qty.loc["2024-01-02", "A"] == 0.0
    assert result.qty.loc["2024-01-03", "A"] == 10.0


def test_engine_respects_tradable_mask() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    close = pd.DataFrame({"A": [100.0, 110.0, 120.0]}, index=index)
    weights = pd.DataFrame({"A": [1.0, 0.0, 0.0]}, index=index)
    tradable = pd.DataFrame({"A": [True, False, True]}, index=index)

    engine = BacktestEngine(cost=CostModel())
    result = engine.run(
        close=close,
        weights=weights,
        tradable=tradable,
        capital=100.0,
        fill_mode="close",
    )

    assert result.qty.loc["2024-01-03", "A"] == 1.0
    assert result.qty.loc["2024-01-04", "A"] == 0.0
    assert result.equity.iloc[-1] == 120.0


def test_engine_rounds_target_quantity_when_fractional_disabled() -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    close = pd.DataFrame({"A": [42.0, 42.0]}, index=index)
    weights = pd.DataFrame({"A": [1.0, 1.0]}, index=index)

    engine = BacktestEngine(cost=CostModel())
    result = engine.run(
        close=close,
        weights=weights,
        capital=100.0,
        fill_mode="close",
        allow_fractional=False,
        show_progress=True,
    )

    assert result.qty.loc["2024-01-02", "A"] == 2.0
