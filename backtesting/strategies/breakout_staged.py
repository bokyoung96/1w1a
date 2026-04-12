from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from backtesting.catalog import DatasetId
from backtesting.construction.base import ConstructionResult
from backtesting.data import MarketData
from backtesting.policy.base import BUCKET_LEDGER_COLUMNS, PositionPlan, PositionPolicy
from backtesting.policy.staged import BudgetPreservingStagedPolicy, BucketDefinition, StagedRuleSet
from backtesting.signals.base import SignalBundle

from .composable import ComposableStrategy


@dataclass(frozen=True, slots=True)
class Breakout52WeekStagedSignalProducer:
    breakout_window: int = 252
    exit_window: int = 20
    pullback_ma_window: int = 10

    @property
    def datasets(self) -> tuple[DatasetId, ...]:
        return (DatasetId.QW_ADJ_C,)

    def build(self, market: MarketData) -> SignalBundle:
        close = market.frames["close"].astype(float)
        tradable = close.notna()
        prior_high = close.rolling(self.breakout_window, min_periods=self.breakout_window).max().shift(1)
        prior_low = close.rolling(self.exit_window, min_periods=self.exit_window).min().shift(1)
        ma10 = close.rolling(self.pullback_ma_window, min_periods=self.pullback_ma_window).mean()

        breakout = close.gt(prior_high).fillna(False)
        exit_mask = close.lt(prior_low).fillna(False)
        pullback = close.le(ma10 * 1.01).fillna(False)

        eligible_entry = pd.DataFrame(False, index=close.index, columns=close.columns)
        eligible_add_1 = pd.DataFrame(False, index=close.index, columns=close.columns)
        eligible_add_2 = pd.DataFrame(False, index=close.index, columns=close.columns)

        for symbol in close.columns:
            stage = 0
            armed_for_add = False
            prev_close = np.nan

            for timestamp in close.index:
                if not bool(tradable.at[timestamp, symbol]):
                    prev_close = np.nan
                    continue

                price = float(close.at[timestamp, symbol])
                ma_value = ma10.at[timestamp, symbol]

                if stage == 0 and bool(breakout.at[timestamp, symbol]):
                    eligible_entry.at[timestamp, symbol] = True
                    stage = 1
                    armed_for_add = False
                elif stage > 0 and stage < 3:
                    if bool(pullback.at[timestamp, symbol]):
                        armed_for_add = True
                    elif armed_for_add and pd.notna(prev_close) and pd.notna(ma_value):
                        if price > float(prev_close) and price > float(ma_value):
                            if stage == 1:
                                eligible_add_1.at[timestamp, symbol] = True
                            else:
                                eligible_add_2.at[timestamp, symbol] = True
                            stage += 1
                            armed_for_add = False

                prev_close = price

        return SignalBundle(
            alpha=breakout.astype(float),
            context={
                "close": close,
                "tradable": tradable,
                "breakout": breakout,
                "pullback_to_ma10": pullback,
                "eligible_entry": eligible_entry,
                "eligible_add_1": eligible_add_1,
                "eligible_add_2": eligible_add_2,
                "eligible_exit": exit_mask,
            },
        )


@dataclass(frozen=True, slots=True)
class _Breakout52WeekStagedConstructionRule:
    def build(self, bundle: SignalBundle) -> ConstructionResult:
        close = bundle.context["close"]
        entry = bundle.context["breakout"]
        exit_mask = bundle.context["eligible_exit"]
        tradable = bundle.context["tradable"].reindex(index=close.index, columns=close.columns).fillna(False).astype(bool)

        active = pd.Series(False, index=close.columns, dtype=bool)
        rows: dict[pd.Timestamp, pd.Series] = {}

        for timestamp in close.index:
            tradable_row = tradable.loc[timestamp]
            active = active & tradable_row
            active = active & ~exit_mask.loc[timestamp].fillna(False)
            active = active | (entry.loc[timestamp].fillna(False) & tradable_row)

            weights = pd.Series(0.0, index=close.columns, dtype=float)
            active_count = int(active.sum())
            if active_count > 0:
                weights.loc[active] = 1.0 / active_count
            rows[timestamp] = weights

        base_target_weights = (
            pd.DataFrame.from_dict(rows, orient="index")
            .reindex(index=close.index, columns=close.columns)
            .fillna(0.0)
            .astype(float)
        )
        selection_mask = base_target_weights.ne(0.0)
        return ConstructionResult(
            base_target_weights=base_target_weights,
            selection_mask=selection_mask,
            group_long_budget=None,
            group_short_budget=None,
            meta={},
        )


@dataclass(slots=True)
class _Breakout52WeekStagedPolicy(PositionPolicy):
    buckets: tuple[BucketDefinition, ...]
    rules: StagedRuleSet

    def __post_init__(self) -> None:
        BudgetPreservingStagedPolicy(buckets=self.buckets, rules=self.rules)

    def apply(
        self,
        construction: ConstructionResult,
        market: MarketData,
        bundle: SignalBundle,
    ) -> PositionPlan:
        del market

        base = construction.base_target_weights.fillna(0.0).astype(float)
        dates = base.index
        symbols = list(base.columns)
        n_dates = len(dates)
        n_symbols = len(symbols)
        n_buckets = len(self.buckets)

        entry_mask = self._aligned_mask(bundle.context[self.rules.entry_key], base)
        add_masks = tuple(self._aligned_mask(bundle.context[key], base) for key in self.rules.add_keys)
        exit_mask = self._aligned_mask(bundle.context[self.rules.exit_key], base)

        base_values = base.to_numpy(dtype=float)
        target_values = np.zeros((n_dates, n_symbols), dtype=float)
        bucket_values = np.zeros((n_dates, n_buckets, n_symbols), dtype=float)
        active = np.zeros((n_buckets, n_symbols), dtype=bool)
        held_base = np.zeros(n_symbols, dtype=float)

        for date_index in range(n_dates):
            prior_active = active.copy()
            next_active = prior_active.copy()
            base_row = base_values[date_index]
            positive_base = base_row > 0.0

            if positive_base.any():
                held_base[positive_base] = base_row[positive_base]

            entered = entry_mask[date_index] & positive_base
            if entered.any():
                next_active[0, entered] = True

            for bucket_index, add_mask in enumerate(add_masks, start=1):
                activate = add_mask[date_index] & prior_active[bucket_index - 1] & positive_base
                if activate.any():
                    next_active[bucket_index, activate] = True

            exiting = exit_mask[date_index] & next_active.any(axis=0)
            if exiting.any():
                for symbol_index in np.flatnonzero(exiting):
                    active_buckets = np.flatnonzero(next_active[:, symbol_index])
                    if active_buckets.size == 0:
                        continue
                    next_active[active_buckets[-1], symbol_index] = False
                    if not next_active[:, symbol_index].any():
                        held_base[symbol_index] = 0.0

            inactive = ~next_active.any(axis=0)
            held_base[inactive & ~positive_base] = 0.0

            active = next_active
            effective_base = np.where(active.any(axis=0), np.where(positive_base, base_row, held_base), 0.0)

            for bucket_index, bucket in enumerate(self.buckets):
                bucket_values[date_index, bucket_index, :] = np.where(
                    active[bucket_index],
                    effective_base * float(bucket.budget_fraction),
                    0.0,
                )
            target_values[date_index, :] = bucket_values[date_index].sum(axis=0)

        records: list[dict[str, object]] = []
        for date_index, date in enumerate(dates):
            for bucket_index, bucket in enumerate(self.buckets):
                row = bucket_values[date_index, bucket_index]
                for symbol_index, symbol in enumerate(symbols):
                    value = float(row[symbol_index])
                    if value == 0.0:
                        continue
                    records.append(
                        {
                            "date": date,
                            "symbol": symbol,
                            "side": "long",
                            "bucket_id": bucket.bucket_id,
                            "stage_index": bucket_index,
                            "target_weight": value,
                            "actual_weight": value,
                            "target_qty": 0.0,
                            "actual_qty": 0.0,
                            "entry_price": None,
                            "mark_price": None,
                            "bucket_return": 0.0,
                            "state": "active",
                            "event": "staged",
                            "construction_group": None,
                            "budget_id": bucket.bucket_id,
                        }
                    )

        ledger = pd.DataFrame.from_records(records, columns=BUCKET_LEDGER_COLUMNS)
        return PositionPlan(
            target_weights=pd.DataFrame(target_values, index=dates, columns=symbols),
            bucket_ledger=ledger,
            bucket_meta={
                "policy_name": pd.Series(["staged"], name="policy_name"),
                "bucket_count": pd.Series([n_buckets], name="bucket_count"),
            },
            validation={},
        )

    @staticmethod
    def _aligned_mask(frame: pd.DataFrame, base: pd.DataFrame) -> np.ndarray:
        return frame.reindex(index=base.index, columns=base.columns).fillna(False).to_numpy(dtype=bool)


@dataclass(slots=True)
class Breakout52WeekStaged(ComposableStrategy):
    breakout_window: int = 252
    exit_window: int = 20
    pullback_ma_window: int = 10

    def __post_init__(self) -> None:
        self.signal_producer = Breakout52WeekStagedSignalProducer(
            breakout_window=self.breakout_window,
            exit_window=self.exit_window,
            pullback_ma_window=self.pullback_ma_window,
        )
        self.construction_rule = _Breakout52WeekStagedConstructionRule()
        self.position_policy = _Breakout52WeekStagedPolicy(
            buckets=(
                BucketDefinition("entry", 1 / 3),
                BucketDefinition("add_1", 1 / 3),
                BucketDefinition("add_2", 1 / 3),
            ),
            rules=StagedRuleSet(
                entry_key="eligible_entry",
                add_keys=("eligible_add_1", "eligible_add_2"),
                exit_key="eligible_exit",
            ),
        )
