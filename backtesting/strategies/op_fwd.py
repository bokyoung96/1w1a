from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from backtesting.catalog import DatasetId
from backtesting.data import MarketData
from backtesting.strategy.cross import RankLongOnly

from .base import RegisteredStrategy


@dataclass(slots=True)
class OpFwdYieldTopN(RegisteredStrategy):
    top_n: int = 20
    ranker: RankLongOnly = field(init=False)

    def __post_init__(self) -> None:
        self.ranker = RankLongOnly(top_n=self.top_n)

    @property
    def datasets(self) -> tuple[DatasetId, ...]:
        return (DatasetId.QW_OP_NFY1, DatasetId.QW_MKTCAP)

    def build_signal(self, market: MarketData) -> pd.DataFrame:
        op_fwd = market.frames["op_fwd"]
        market_cap = market.frames["market_cap"].where(market.frames["market_cap"].ne(0.0))
        return op_fwd.div(market_cap)

    def target_weights(self, signal: pd.Series) -> pd.Series:
        return self.ranker.target_weights(signal)
