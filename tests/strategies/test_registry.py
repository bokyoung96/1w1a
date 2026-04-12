from pathlib import Path
import warnings

import pandas as pd
from pandas.testing import assert_frame_equal

from backtesting.data import MarketData
from backtesting.strategies import RegisteredStrategy, build_strategy, list_strategies


def test_registry_lists_default_strategies() -> None:
    assert {
        "momentum",
        "op_fwd_yield",
        "momentum_long_short",
        "momentum_sector_neutral",
        "momentum_sector_neutral_staged",
    }.issubset(list_strategies())


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

    plan = strategy.build_plan(market)
    weights = strategy.build_weights(market)

    assert plan.bucket_ledger["bucket_id"].eq("base").all()
    assert plan.target_weights.loc["2024-01-04", "A"] == 1.0
    assert plan.target_weights.loc["2024-01-04", "B"] == 0.0
    assert weights.equals(plan.target_weights)
    assert weights.loc["2024-01-04", "A"] == 1.0
    assert weights.loc["2024-01-04", "B"] == 0.0


def test_momentum_long_short_builds_market_neutral_weights() -> None:
    strategy = build_strategy("momentum_long_short", top_n=1, lookback=1)
    close = pd.DataFrame(
        {
            "A": [10.0, 11.0, 12.0],
            "B": [10.0, 10.0, 10.0],
            "C": [10.0, 9.0, 8.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
    )
    market = MarketData(frames={"close": close}, universe=None, benchmark=None)

    plan = strategy.build_plan(market)

    assert plan.target_weights.loc["2024-01-04", "A"] == 1.0
    assert plan.target_weights.loc["2024-01-04", "B"] == 0.0
    assert plan.target_weights.loc["2024-01-04", "C"] == -1.0
    assert round(float(plan.target_weights.loc["2024-01-04"].sum()), 8) == 0.0
    assert plan.bucket_ledger["bucket_id"].eq("base").all()


def test_momentum_sector_neutral_staged_enters_symbols_on_first_nonzero_base_weight_date() -> None:
    strategy = build_strategy("momentum_sector_neutral_staged", top_n=1, lookback=1)
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    close = pd.DataFrame(
        {
            "A": [100.0, 101.0, 106.05],
            "B": [100.0, 102.0, 103.02],
            "C": [100.0, 100.0, 99.0],
            "D": [100.0, 103.0, 105.06],
            "E": [100.0, 101.0, 101.0],
            "F": [100.0, 99.0, 97.02],
        },
        index=index,
    )
    sector = pd.DataFrame(
        {
            "A": ["Tech"],
            "B": ["Tech"],
            "C": ["Tech"],
            "D": ["Energy"],
            "E": ["Energy"],
            "F": ["Energy"],
        },
        index=pd.to_datetime(["2024-01-31"]),
    )
    market = MarketData(
        frames={"close": close, "sector_big": sector.reindex(index, method="bfill")},
        universe=None,
        benchmark=None,
    )

    plan = strategy.build_plan(market)

    assert plan.target_weights.loc["2024-01-03", "A"] == 0.0
    assert plan.target_weights.loc["2024-01-04", "A"] == 0.25
    assert plan.target_weights.loc["2024-01-04", "C"] == -0.5
    late_entry = plan.bucket_ledger[
        (plan.bucket_ledger["date"] == pd.Timestamp("2024-01-04"))
        & (plan.bucket_ledger["symbol"] == "A")
    ]
    assert late_entry["bucket_id"].tolist() == ["entry"]
    assert late_entry["target_weight"].tolist() == [0.25]


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


def test_op_fwd_yield_strategy_builds_plan() -> None:
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

    plan = strategy.build_plan(market)

    assert_frame_equal(plan.target_weights, strategy.build_weights(market))
    assert plan.bucket_ledger["bucket_id"].eq("base").all()


def test_registered_strategy_preserves_legacy_extension_path() -> None:
    class LegacyStrategy(RegisteredStrategy):
        @property
        def datasets(self) -> tuple:
            return ()

        def build_signal(self, market: MarketData) -> pd.DataFrame:
            return market.frames["close"].pct_change(fill_method=None)

        def target_weights(self, signal: pd.Series) -> pd.Series:
            weights = pd.Series(0.0, index=signal.index, dtype=float)
            winner = signal.dropna().sort_values(ascending=False).head(1)
            if not winner.empty:
                weights.loc[winner.index] = 1.0
            return weights

    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    close = pd.DataFrame({"A": [10.0, 11.0, 12.0], "B": [10.0, 10.0, 9.0]}, index=index)
    market = MarketData(frames={"close": close}, universe=None, benchmark=None)

    strategy = LegacyStrategy()

    plan = strategy.build_plan(market)

    assert plan.target_weights.loc["2024-01-04", "A"] == 1.0
    assert plan.bucket_ledger["bucket_id"].eq("base").all()


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
