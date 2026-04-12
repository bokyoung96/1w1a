from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtesting.signals.base import SignalBundle

from .base import ConstructionResult


@dataclass(slots=True)
class SectorNeutralTopBottom:
    top_n: int
    bottom_n: int

    def build(self, bundle: SignalBundle) -> ConstructionResult:
        alpha = bundle.alpha
        sector = bundle.context["sector"]
        weights_by_date: dict[pd.Timestamp, pd.Series] = {}
        group_long_budget_by_date: dict[pd.Timestamp, pd.Series] = {}
        group_short_budget_by_date: dict[pd.Timestamp, pd.Series] = {}
        selected_long_by_date: dict[pd.Timestamp, pd.Series] = {}
        selected_short_by_date: dict[pd.Timestamp, pd.Series] = {}

        for timestamp in alpha.index:
            weights = pd.Series(0.0, index=alpha.columns, dtype=float)
            group_long_budget = pd.Series(dtype=float)
            group_short_budget = pd.Series(dtype=float)

            sector_row = sector.loc[timestamp].dropna()
            signal = alpha.loc[timestamp].dropna().reindex(sector_row.index).dropna()
            sector_membership = sector_row.reindex(signal.index).dropna()
            sector_count = max(int(sector_membership.nunique()), 1)

            for sector_name, members in sector_membership.groupby(sector_membership, sort=False):
                sector_signal = signal.loc[members.index]
                longs = sector_signal.sort_values(ascending=False).head(self.top_n)
                short_pool = sector_signal.drop(index=longs.index, errors="ignore")
                shorts = short_pool.sort_values(ascending=True).head(self.bottom_n)

                if not longs.empty:
                    weights.loc[longs.index] = 1.0 / sector_count / len(longs)
                    group_long_budget.loc[sector_name] = float(weights.loc[longs.index].sum())
                if not shorts.empty:
                    weights.loc[shorts.index] = -1.0 / sector_count / len(shorts)
                    group_short_budget.loc[sector_name] = float(weights.loc[shorts.index].abs().sum())

            weights_by_date[timestamp] = weights
            group_long_budget_by_date[timestamp] = group_long_budget
            group_short_budget_by_date[timestamp] = group_short_budget
            selected_long_by_date[timestamp] = weights.gt(0.0)
            selected_short_by_date[timestamp] = weights.lt(0.0)

        base_target_weights = (
            pd.DataFrame.from_dict(weights_by_date, orient="index")
            .reindex(index=alpha.index, columns=alpha.columns)
            .fillna(0.0)
            .astype(float)
        )
        group_long_budget = (
            pd.DataFrame.from_dict(group_long_budget_by_date, orient="index")
            .reindex(index=alpha.index)
            .fillna(0.0)
            .astype(float)
        )
        group_short_budget = (
            pd.DataFrame.from_dict(group_short_budget_by_date, orient="index")
            .reindex(index=alpha.index)
            .fillna(0.0)
            .astype(float)
        )
        selected_long = (
            pd.DataFrame.from_dict(selected_long_by_date, orient="index")
            .reindex(index=alpha.index, columns=alpha.columns)
            .fillna(False)
            .astype(bool)
        )
        selected_short = (
            pd.DataFrame.from_dict(selected_short_by_date, orient="index")
            .reindex(index=alpha.index, columns=alpha.columns)
            .fillna(False)
            .astype(bool)
        )
        return ConstructionResult(
            base_target_weights=base_target_weights,
            selection_mask=base_target_weights.ne(0.0),
            group_long_budget=group_long_budget,
            group_short_budget=group_short_budget,
            meta={
                "selected_long": selected_long,
                "selected_short": selected_short,
            },
        )
