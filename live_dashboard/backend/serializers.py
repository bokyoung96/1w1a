from __future__ import annotations

import math

import pandas as pd

from live_dashboard.backend.schemas import (
    CategoryPointModel,
    HoldingModel,
    NamedSeriesModel,
    ValuePointModel,
)


def sanitize_finite_number(value: object) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return numeric


def serialize_value_points(series: pd.Series) -> list[ValuePointModel]:
    points: list[ValuePointModel] = []
    for date, value in series.items():
        numeric = sanitize_finite_number(value)
        if numeric is None:
            continue
        points.append(
            ValuePointModel(
                date=pd.Timestamp(date).date().isoformat(),
                value=numeric,
            )
        )
    return points


def serialize_named_series(series: pd.Series, *, run_id: str, label: str) -> NamedSeriesModel:
    return NamedSeriesModel(
        run_id=run_id,
        label=label,
        points=serialize_value_points(series),
    )


def serialize_latest_holdings(frame: pd.DataFrame | None) -> list[HoldingModel]:
    if frame is None or frame.empty:
        return []
    holdings: list[HoldingModel] = []
    for _, row in frame.iterrows():
        target_weight = sanitize_finite_number(row["target_weight"])
        abs_weight = sanitize_finite_number(row["abs_weight"])
        if target_weight is None or abs_weight is None:
            continue
        holdings.append(
            HoldingModel(
                symbol=str(row["symbol"]),
                target_weight=target_weight,
                abs_weight=abs_weight,
            )
        )
    return holdings


def serialize_named_values(series: pd.Series) -> list[CategoryPointModel]:
    if series.empty:
        return []
    values: list[CategoryPointModel] = []
    for name, value in series.items():
        numeric = sanitize_finite_number(value)
        if numeric is None:
            continue
        values.append(CategoryPointModel(name=str(name), value=numeric))
    return values
