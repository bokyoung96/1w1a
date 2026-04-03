from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True, slots=True)
class SavedRun:
    run_id: str
    path: Path
    config: dict[str, object]
    summary: dict[str, float]
    equity: pd.Series
    returns: pd.Series
    turnover: pd.Series
    weights: pd.DataFrame
    qty: pd.DataFrame
    monthly_returns: pd.Series | None = None
    latest_qty: pd.DataFrame | None = None
    latest_weights: pd.DataFrame | None = None
    validation: dict[str, object] | None = None
    split: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class ReportSpec:
    name: str
    run_ids: tuple[str, ...]
    title: str | None = None
    include_factor: bool = True
    include_validation: bool = True
    include_is_oos: bool = True
    formats: tuple[str, ...] = ("html", "pdf")
