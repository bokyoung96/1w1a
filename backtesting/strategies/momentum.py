from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from backtesting.catalog import DatasetId
from backtesting.data import MarketData
from backtesting.strategy.cross import RankLongOnly

from .base import RegisteredStrategy


@dataclass(slots=True)
class MomentumTopN(RegisteredStrategy):
    top_n: int = 20
    lookback: int = 20
    ranker: RankLongOnly = field(init=False)

    def __post_init__(self) -> None:
        self.ranker = RankLongOnly(top_n=self.top_n)

    @property
    def datasets(self) -> tuple[DatasetId, ...]:
        return (DatasetId.QW_ADJ_C,)

    def build_signal(self, market: MarketData) -> pd.DataFrame:
        close = market.frames["close"]
        return close.pct_change(self.lookback, fill_method=None)

    def target_weights(self, signal: pd.Series) -> pd.Series:
        return self.ranker.target_weights(signal)
