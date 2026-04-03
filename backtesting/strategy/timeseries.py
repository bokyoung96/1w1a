from dataclasses import dataclass

import pandas as pd

from .base import BaseStrategy


@dataclass(slots=True)
class ThresholdTrend(BaseStrategy):
    threshold: float = 0.0

    def target_weights(self, signal: pd.Series) -> pd.Series:
        return signal.gt(self.threshold).astype(float)
