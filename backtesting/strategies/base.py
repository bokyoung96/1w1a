from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from backtesting.catalog import DatasetId
from backtesting.data import MarketData


class RegisteredStrategy(ABC):
    @property
    @abstractmethod
    def datasets(self) -> tuple[DatasetId, ...]:
        raise NotImplementedError

    @abstractmethod
    def build_signal(self, market: MarketData) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def target_weights(self, signal: pd.Series) -> pd.Series:
        raise NotImplementedError

    def build_weights(self, market: MarketData) -> pd.DataFrame:
        signal = self.build_signal(market)
        if market.universe is not None:
            universe = market.universe.reindex(index=signal.index, columns=signal.columns)
            universe = universe.astype("boolean").fillna(False).astype(bool)
            signal = signal.where(universe)

        rows = {}
        for ts in signal.index:
            rows[ts] = self.target_weights(signal.loc[ts])

        return (
            pd.DataFrame.from_dict(rows, orient="index")
            .reindex(index=signal.index, columns=signal.columns)
            .fillna(0.0)
            .astype(float)
        )
