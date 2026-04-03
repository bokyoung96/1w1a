import pandas as pd


def expand_monthly_frame(
    frame: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    validity: str,
) -> pd.DataFrame:
    if validity != "month_only":
        raise ValueError(f"unsupported validity: {validity}")

    out = pd.DataFrame(index=calendar, columns=frame.columns)
    for ts, row in frame.iterrows():
        month_mask = (calendar.year == ts.year) & (calendar.month == ts.month)
        out.loc[month_mask, :] = row.values
    return out
