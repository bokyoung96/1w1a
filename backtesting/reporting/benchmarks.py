from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data import ParquetStore
from backtesting.ingest import IngestJob
from backtesting.ingest.io import find_raw_path
from root import ROOT

from .models import BenchmarkConfig


@dataclass(frozen=True, slots=True)
class BenchmarkSeries:
    name: str
    prices: pd.Series
    returns: pd.Series


class BenchmarkRepository:
    def __init__(self, prices: pd.DataFrame) -> None:
        self.prices = prices.sort_index()

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
        self.sector = sector.sort_index()

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "SectorRepository":
        return cls(sector=frame)

    @classmethod
    def default(cls) -> "SectorRepository":
        return cls(sector=_load_default_frame(DatasetId.QW_WICS_SEC_BIG))

    def latest_sector_row(self, as_of: pd.Timestamp) -> pd.Series:
        sector_history = self.sector.loc[:as_of]
        if sector_history.empty:
            raise KeyError(f"no sector mapping available on or before {as_of.date()}")
        return sector_history.iloc[-1]

    def latest_sector_counts(self, weights: pd.DataFrame) -> pd.Series:
        aligned = self._latest_aligned_weights(weights)
        counts = (
            aligned.loc[aligned["weight"].ne(0.0)]
            .groupby("sector", sort=False)
            .size()
            .astype(float)
            .rename("count")
        )
        counts.index.name = "sector"
        return counts

    def latest_sector_weights(self, weights: pd.DataFrame) -> pd.Series:
        aligned = self._latest_aligned_weights(weights)
        exposure = aligned.groupby("sector", sort=False)["weight"].sum()
        return exposure.sort_values(ascending=False).rename_axis(None).rename(None)

    def _latest_aligned_weights(self, weights: pd.DataFrame) -> pd.DataFrame:
        latest_date = weights.index.max()
        latest_weight_row = weights.loc[:latest_date].iloc[-1].astype(float)
        latest_sector_row = self.latest_sector_row(latest_date)
        return pd.DataFrame(
            {
                "sector": latest_sector_row.reindex(latest_weight_row.index),
                "weight": latest_weight_row,
            }
        ).dropna(subset=["sector"])


def _load_default_frame(dataset_id: DatasetId) -> pd.DataFrame:
    catalog = DataCatalog.default()
    store = ParquetStore(ROOT.parquet_path)
    parquet_path = ROOT.parquet_path / f"{dataset_id.value}.parquet"
    if not parquet_path.exists():
        raw_path = find_raw_path(ROOT.raw_path, dataset_id.value)
        if dataset_id is DatasetId.QW_BM and raw_path.suffix == ".xlsx":
            frame = _read_quantwise_benchmark_frame(raw_path)
            store.write(dataset_id.value, frame)
            return frame
        IngestJob(catalog=catalog, raw_dir=ROOT.raw_path, parquet_dir=ROOT.parquet_path).run(dataset_id)
    return store.read(dataset_id.value)


def _read_quantwise_benchmark_frame(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, header=None)
    leading = raw.iloc[:, 0].astype(str).str.strip().str.upper()

    code_rows = leading[leading.eq("CODE")]
    date_rows = leading[leading.eq("D A T E")]
    if code_rows.empty or date_rows.empty:
        raise KeyError(f"unable to locate QuantWise benchmark headers in {path.name}")

    code_row = int(code_rows.index[0])
    date_row = int(date_rows.index[0])
    codes = raw.iloc[code_row, 1:]
    valid_columns = [int(column) for column, value in codes.items() if pd.notna(value)]

    frame = raw.loc[date_row + 1 :, [0, *valid_columns]].copy()
    frame.columns = ["date", *[str(codes[column]).strip() for column in valid_columns]]
    frame = frame.dropna(subset=["date"])
    frame["date"] = pd.to_datetime(frame["date"]).dt.normalize()
    frame = frame.sort_values("date").set_index("date")
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame.index.name = "date"
    return frame
