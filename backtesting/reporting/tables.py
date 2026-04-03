from __future__ import annotations

import math

import pandas as pd

from .models import SavedRun

__all__ = (
    "build_appendix_table",
    "build_latest_qty_table",
    "build_latest_weights_table",
    "build_summary_table",
)


def build_summary_table(runs: list[SavedRun]) -> pd.DataFrame:
    rows = []
    for run in runs:
        rows.append(
            {
                "run_id": run.run_id,
                "strategy": str(run.config.get("strategy", "")),
                "cagr": float(run.summary.get("cagr", math.nan)),
                "mdd": float(run.summary.get("mdd", math.nan)),
                "sharpe": float(run.summary.get("sharpe", math.nan)),
                "final_equity": float(run.summary.get("final_equity", math.nan)),
                "avg_turnover": float(run.summary.get("avg_turnover", math.nan)),
            }
        )
    return pd.DataFrame(rows)


def build_latest_weights_table(run: SavedRun) -> pd.DataFrame:
    if run.latest_weights is not None:
        return run.latest_weights.copy()
    return _build_latest_table(run.weights, value_column="target_weight", abs_column="abs_weight")


def build_latest_qty_table(run: SavedRun) -> pd.DataFrame:
    if run.latest_qty is not None:
        return run.latest_qty.copy()
    return _build_latest_table(run.qty, value_column="qty", abs_column="abs_qty")


def build_appendix_table(runs: list[SavedRun]) -> pd.DataFrame:
    rows = []
    for run in runs:
        rows.append(
            {
                "run_id": run.run_id,
                "path": str(run.path),
                "strategy": str(run.config.get("strategy", "")),
                "start": str(run.config.get("start", "")),
                "end": str(run.config.get("end", "")),
            }
        )
    return pd.DataFrame(rows)


def _build_latest_table(frame: pd.DataFrame, *, value_column: str, abs_column: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["symbol", value_column, abs_column])

    latest = frame.iloc[-1]
    table = pd.DataFrame({"symbol": latest.index, value_column: latest.values})
    table = table.loc[table[value_column].ne(0.0)].copy()
    table[abs_column] = table[value_column].abs()
    return table.sort_values([abs_column, "symbol"], ascending=[False, True]).reset_index(drop=True)
