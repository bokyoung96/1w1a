import pandas as pd

from backtesting.strategy.cross import RankLongOnly, RankLongShort


def test_rank_long_only_selects_top_names() -> None:
    factor = pd.Series({"A": 1.0, "B": 3.0, "C": 2.0})
    strategy = RankLongOnly(top_n=2)

    weights = strategy.target_weights(factor)

    assert weights["B"] == 0.5
    assert weights["C"] == 0.5
    assert weights.get("A", 0.0) == 0.0


def test_rank_long_short_balances_long_and_short_legs() -> None:
    factor = pd.Series({"A": 1.0, "B": 4.0, "C": 2.0, "D": 0.5})
    strategy = RankLongShort(top_n=2, bottom_n=1)

    weights = strategy.target_weights(factor)

    assert weights["B"] == 0.5
    assert weights["C"] == 0.5
    assert weights["D"] == -1.0
    assert weights["A"] == 0.0
