from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from backtesting.catalog import DatasetId
from backtesting.data import MarketData
from backtesting.policy.base import PositionPlan


class RegisteredStrategy(ABC):
    @property
    @abstractmethod
    def datasets(self) -> tuple[DatasetId, ...]:
        raise NotImplementedError

    @abstractmethod
    def build_signal(self, market: MarketData) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def build_plan(self, market: MarketData) -> PositionPlan:
        raise NotImplementedError

    def build_weights(self, market: MarketData) -> pd.DataFrame:
        return self.build_plan(market).target_weights
