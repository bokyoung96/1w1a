import pandas as pd
import pytest

from backtesting.execution.fill import fill_prices
from backtesting.execution.schedule import (
    CustomSchedule,
    DailySchedule,
    MonthlySchedule,
    WeeklySchedule,
)


def test_weekly_schedule_marks_rebalance_dates() -> None:
    index = pd.date_range("2024-01-01", periods=10, freq="D")
    schedule = WeeklySchedule()
    flags = schedule.flags(index)

    assert flags.sum() >= 1
    assert flags.index.equals(index)


def test_daily_schedule_marks_every_date() -> None:
    index = pd.date_range("2024-01-01", periods=3, freq="D")

    flags = DailySchedule().flags(index)

    assert flags.index.equals(index)
    assert flags.tolist() == [True, True, True]


def test_monthly_schedule_marks_last_date_in_each_month() -> None:
    index = pd.to_datetime(
        ["2024-01-30", "2024-01-31", "2024-02-01", "2024-02-29", "2024-03-01"]
    )

    flags = MonthlySchedule().flags(index)

    assert flags.index.equals(index)
    assert flags.tolist() == [False, True, False, True, True]


def test_custom_schedule_marks_only_configured_dates() -> None:
    index = pd.date_range("2024-01-01", periods=5, freq="D")
    dates = pd.to_datetime(["2024-01-02", "2024-01-04"])

    flags = CustomSchedule(dates=dates).flags(index)

    assert flags.tolist() == [False, True, False, True, False]


def test_fill_prices_returns_close_for_close_mode() -> None:
    close = pd.DataFrame({"005930": [100.0, 101.0]})

    result = fill_prices(close=close, open_=None, fill_mode="close")

    assert result.equals(close)


def test_fill_prices_uses_next_open_for_next_open_mode() -> None:
    index = pd.date_range("2024-01-01", periods=3, freq="D")
    close = pd.DataFrame({"005930": [100.0, 101.0, 102.0]}, index=index)
    open_ = pd.DataFrame({"005930": [99.0, 100.5, 101.5]}, index=index)

    result = fill_prices(close=close, open_=open_, fill_mode="next_open")

    assert result.equals(open_.shift(-1))


def test_fill_prices_requires_open_for_next_open_mode() -> None:
    close = pd.DataFrame({"005930": [100.0]})

    with pytest.raises(ValueError, match="open prices required for next_open"):
        fill_prices(close=close, open_=None, fill_mode="next_open")
