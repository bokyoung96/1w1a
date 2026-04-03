import pandas as pd


class BaseStrategy:
    def target_weights(self, signal: pd.Series) -> pd.Series:
        raise NotImplementedError
