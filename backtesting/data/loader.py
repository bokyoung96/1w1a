from dataclasses import dataclass

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data.store import ParquetStore


@dataclass(frozen=True, slots=True)
class LoadRequest:
    datasets: list[DatasetId]
    start: str
    end: str
    universe: pd.DataFrame | None = None
    benchmark: pd.Series | None = None
    price_mode: str = "adj"


@dataclass(slots=True)
class MarketData:
    frames: dict[str, pd.DataFrame]
    universe: pd.DataFrame | None
    benchmark: pd.Series | None


class DataLoader:
    def __init__(self, catalog: DataCatalog, store: ParquetStore) -> None:
        self.catalog = catalog
        self.store = store

    def load(self, request: LoadRequest) -> MarketData:
        frames: dict[str, pd.DataFrame] = {}
        for dataset_id in request.datasets:
            spec = self.catalog.get(dataset_id)
            frame = self.store.read(spec.stem).loc[request.start : request.end]
            key = "close" if spec.stem == "qw_adj_c" else spec.stem
            frames[key] = frame
        return MarketData(
            frames=frames,
            universe=request.universe,
            benchmark=request.benchmark,
        )
