from __future__ import annotations

import math

import pandas as pd

from live_dashboard.backend.schemas import CategoryPointModel, HoldingModel, SeriesPointModel


def serialize_series(series: pd.Series, *, run_id: str, label: str) -> list[SeriesPointModel]:
    points: list[SeriesPointModel] = []
    for date, value in series.items():
        numeric = float(value)
        if math.isnan(numeric):
            continue
        points.append(
            SeriesPointModel(
                date=pd.Timestamp(date).date().isoformat(),
                value=numeric,
                run_id=run_id,
                label=label,
            )
        )
    return points


def serialize_latest_holdings(frame: pd.DataFrame | None) -> list[HoldingModel]:
    if frame is None or frame.empty:
        return []
    return [
        HoldingModel(
            symbol=str(row["symbol"]),
            target_weight=float(row["target_weight"]),
            abs_weight=float(row["abs_weight"]),
        )
        for _, row in frame.iterrows()
    ]


def serialize_named_values(series: pd.Series) -> list[CategoryPointModel]:
    if series.empty:
        return []
    return [CategoryPointModel(name=str(name), value=float(value)) for name, value in series.items()]
