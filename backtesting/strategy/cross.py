from dataclasses import dataclass

import pandas as pd

from .base import BaseStrategy


@dataclass(slots=True)
class RankLongOnly(BaseStrategy):
    top_n: int

    def target_weights(self, signal: pd.Series) -> pd.Series:
        winners = signal.sort_values(ascending=False).head(self.top_n)
        return pd.Series(1.0 / len(winners), index=winners.index)


@dataclass(slots=True)
class RankLongShort(BaseStrategy):
    top_n: int
    bottom_n: int

    def target_weights(self, signal: pd.Series) -> pd.Series:
        long_leg = signal.sort_values(ascending=False).head(self.top_n)
        short_leg = signal.sort_values(ascending=True).head(self.bottom_n)
        weights = pd.Series(0.0, index=signal.index)
        weights.loc[long_leg.index] = 1.0 / self.top_n
        weights.loc[short_leg.index] = -1.0 / self.bottom_n
        return weights
