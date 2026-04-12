from __future__ import annotations

import pandas as pd

from backtesting.policy.base import PositionPlan


def validate_position_plan(plan: PositionPlan, tolerance: float = 1e-8) -> None:
    target_totals = plan.target_weights.fillna(0.0).astype(float).sum(axis=1)
    target_totals.index = pd.to_datetime(target_totals.index)

    if plan.bucket_ledger.empty:
        ledger_totals = pd.Series(0.0, index=target_totals.index, dtype=float)
    else:
        ledger_dates = pd.to_datetime(plan.bucket_ledger["date"])
        ledger_weights = pd.to_numeric(plan.bucket_ledger["target_weight"], errors="coerce").fillna(0.0)
        ledger_totals = ledger_weights.groupby(ledger_dates).sum().astype(float)

    all_dates = target_totals.index.union(ledger_totals.index)
    target_totals = target_totals.reindex(all_dates, fill_value=0.0)
    ledger_totals = ledger_totals.reindex(all_dates, fill_value=0.0)
    mismatches = target_totals.sub(ledger_totals).abs().gt(float(tolerance))
    if not mismatches.any():
        return

    details = ", ".join(
        (
            f"{date.date().isoformat()}: "
            f"plan={target_totals.loc[date]:.12g} "
            f"ledger={ledger_totals.loc[date]:.12g}"
        )
        for date in all_dates[mismatches]
    )
    raise ValueError(f"bucket target_weight sums do not match plan target_weights: {details}")
