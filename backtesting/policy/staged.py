from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .base import BUCKET_LEDGER_COLUMNS, PositionPlan, PositionPolicy


@dataclass(frozen=True, slots=True)
class BucketDefinition:
    bucket_id: str
    budget_fraction: float


@dataclass(frozen=True, slots=True)
class StagedRuleSet:
    entry_key: str
    add_keys: tuple[str, ...]
    exit_key: str


@dataclass(slots=True)
class BudgetPreservingStagedPolicy(PositionPolicy):
    buckets: tuple[BucketDefinition, ...]
    rules: StagedRuleSet

    def __post_init__(self) -> None:
        if not self.buckets:
            raise ValueError("buckets must not be empty")

        total_fraction = 0.0
        for bucket in self.buckets:
            if bucket.budget_fraction < 0.0:
                raise ValueError("bucket budget_fraction must be non-negative")
            total_fraction += float(bucket.budget_fraction)

        if not np.isclose(total_fraction, 1.0, atol=1e-9):
            raise ValueError("bucket budget_fraction values must sum to 1.0")

        expected_add_keys = max(len(self.buckets) - 1, 0)
        if len(self.rules.add_keys) != expected_add_keys:
            raise ValueError("add_keys must provide one rule for each staged bucket after the first")

    def apply(
        self,
        construction,
        market,
        bundle,
    ) -> PositionPlan:
        base = construction.base_target_weights.fillna(0.0).astype(float)
        close = market.frames["close"].reindex(index=base.index, columns=base.columns)

        dates = base.index
        symbols = list(base.columns)
        n_dates = len(dates)
        n_symbols = len(symbols)
        n_buckets = len(self.buckets)

        entry_mask = self._aligned_mask(bundle.context[self.rules.entry_key], base)
        add_masks = tuple(self._aligned_mask(bundle.context[key], base) for key in self.rules.add_keys)
        exit_mask = self._aligned_mask(bundle.context[self.rules.exit_key], base)

        base_values = base.to_numpy(dtype=float)
        close_values = close.to_numpy(dtype=float)
        target_values = np.zeros((n_dates, n_symbols), dtype=float)
        bucket_values = np.zeros((n_dates, n_buckets, n_symbols), dtype=float)
        active = np.zeros((n_buckets, n_symbols), dtype=bool)

        for date_index in range(n_dates):
            entered = entry_mask[date_index]
            if entered.any():
                active[0, entered] = True

            for bucket_index, add_mask in enumerate(add_masks, start=1):
                activate = add_mask[date_index] & active[bucket_index - 1]
                if activate.any():
                    active[bucket_index, activate] = True

            exited = exit_mask[date_index]
            if exited.any():
                active[:, exited] = False

            for bucket_index, bucket in enumerate(self.buckets):
                bucket_values[date_index, bucket_index, :] = np.where(
                    active[bucket_index],
                    base_values[date_index] * float(bucket.budget_fraction),
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
                    price = float(close_values[date_index, symbol_index])
                    records.append(
                        {
                            "date": date,
                            "symbol": symbol,
                            "side": "long" if value > 0.0 else "short",
                            "bucket_id": bucket.bucket_id,
                            "stage_index": bucket_index,
                            "target_weight": value,
                            "actual_weight": value,
                            "target_qty": 0.0,
                            "actual_qty": 0.0,
                            "entry_price": price,
                            "mark_price": price,
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
