from dataclasses import dataclass

import pandas as pd


class RebalanceSchedule:
    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        raise NotImplementedError


@dataclass(slots=True)
class WeeklySchedule(RebalanceSchedule):
    weekday: int = 4

    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        return pd.Series(index.weekday == self.weekday, index=index)


@dataclass(slots=True)
class DailySchedule(RebalanceSchedule):
    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        return pd.Series(True, index=index)


@dataclass(slots=True)
class MonthlySchedule(RebalanceSchedule):
    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        month_periods = pd.Series(index.to_period("M"), index=index)
        month_change = month_periods.ne(month_periods.shift(-1))
        return month_change.fillna(True)


@dataclass(slots=True)
class CustomSchedule(RebalanceSchedule):
    dates: pd.DatetimeIndex

    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        return pd.Series(index.isin(self.dates), index=index)
