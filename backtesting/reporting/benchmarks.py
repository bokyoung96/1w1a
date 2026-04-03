from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data import ParquetStore
from backtesting.ingest import IngestJob
from root import ROOT

from .models import BenchmarkConfig


@dataclass(frozen=True, slots=True)
class BenchmarkSeries:
    name: str
    prices: pd.Series
    returns: pd.Series


class BenchmarkRepository:
    def __init__(self, prices: pd.DataFrame) -> None:
        self.prices = prices

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "BenchmarkRepository":
        return cls(prices=frame)

    @classmethod
    def default(cls) -> "BenchmarkRepository":
        return cls(prices=_load_default_frame(DatasetId.QW_BM))

    def load_series(self, config: BenchmarkConfig, start: str, end: str) -> BenchmarkSeries:
        prices = self.prices.loc[start:end, config.code].astype(float).rename(config.name).rename_axis("date")
        returns = prices.pct_change().fillna(0.0).rename(config.name).rename_axis("date")
        return BenchmarkSeries(name=config.name, prices=prices, returns=returns)

    def load_returns(self, config: BenchmarkConfig, start: str, end: str) -> pd.Series:
        return self.load_series(config, start, end).returns


class SectorRepository:
    def __init__(self, sector: pd.DataFrame) -> None:
        self.sector = sector

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "SectorRepository":
        return cls(sector=frame)

    @classmethod
    def default(cls) -> "SectorRepository":
        return cls(sector=_load_default_frame(DatasetId.QW_WICS_SEC_BIG))

    def latest_sector_weights(self, weights: pd.DataFrame) -> pd.Series:
        latest_date = weights.index.max()
        latest_weight_row = weights.loc[latest_date]
        if isinstance(latest_weight_row, pd.DataFrame):
            latest_weight_row = latest_weight_row.iloc[-1]
        latest_weight_row = latest_weight_row.astype(float)

        latest_sector_row = self.sector.loc[latest_date]
        if isinstance(latest_sector_row, pd.DataFrame):
            latest_sector_row = latest_sector_row.iloc[-1]
        aligned = pd.DataFrame(
            {
                "sector": latest_sector_row.reindex(latest_weight_row.index),
                "weight": latest_weight_row,
            }
        ).dropna(subset=["sector"])
        exposure = aligned.groupby("sector", sort=False)["weight"].sum()
        return exposure.sort_values(ascending=False).rename_axis(None).rename(None)


def _load_default_frame(dataset_id: DatasetId) -> pd.DataFrame:
    catalog = DataCatalog.default()
    store = ParquetStore(ROOT.parquet_path)
    parquet_path = ROOT.parquet_path / f"{dataset_id.value}.parquet"
    if not parquet_path.exists():
        IngestJob(catalog=catalog, raw_dir=ROOT.raw_path, parquet_dir=ROOT.parquet_path).run(dataset_id)
    return store.read(dataset_id.value)
