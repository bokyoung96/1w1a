from pathlib import Path
import warnings

import pandas as pd

from backtesting.data import MarketData
from backtesting.strategies import build_strategy, list_strategies


def test_registry_lists_default_strategies() -> None:
    assert {"momentum", "op_fwd_yield"}.issubset(list_strategies())


def test_momentum_strategy_builds_weights() -> None:
    strategy = build_strategy("momentum", top_n=1, lookback=1)
    close = pd.DataFrame(
        {
            "A": [10.0, 11.0, 12.0],
            "B": [10.0, 10.0, 9.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    market = MarketData(frames={"close": close}, universe=None, benchmark=None)

    weights = strategy.build_weights(market)

    assert weights.loc["2024-01-04", "A"] == 1.0
    assert weights.loc["2024-01-04", "B"] == 0.0


def test_op_fwd_yield_strategy_builds_weights() -> None:
    strategy = build_strategy("op_fwd_yield", top_n=1)
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    market = MarketData(
        frames={
            "op_fwd": pd.DataFrame({"A": [20.0, 20.0], "B": [5.0, 5.0]}, index=index),
            "market_cap": pd.DataFrame({"A": [10.0, 10.0], "B": [10.0, 10.0]}, index=index),
        },
        universe=None,
        benchmark=None,
    )

    weights = strategy.build_weights(market)

    assert weights.loc["2024-01-03", "A"] == 1.0
    assert weights.loc["2024-01-03", "B"] == 0.0


def test_momentum_strategy_avoids_future_warning_on_pct_change() -> None:
    strategy = build_strategy("momentum", top_n=1, lookback=1)
    close = pd.DataFrame(
        {
            "A": [10.0, 11.0, 12.0],
            "B": [10.0, 10.0, 9.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    market = MarketData(frames={"close": close}, universe=None, benchmark=None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        strategy.build_signal(market)

    assert not any(item.category is FutureWarning for item in caught)


def test_registered_strategy_avoids_future_warning_when_masking_universe() -> None:
    strategy = build_strategy("momentum", top_n=1, lookback=1)
    close = pd.DataFrame(
        {
            "A": [10.0, 11.0, 12.0],
            "B": [10.0, 10.0, 9.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    universe = pd.DataFrame(
        {
            "A": [True, True, True],
            "B": [True, None, True],
        },
        index=close.index,
    )
    market = MarketData(frames={"close": close}, universe=universe, benchmark=None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        strategy.build_weights(market)

    assert not any(item.category is FutureWarning for item in caught)
