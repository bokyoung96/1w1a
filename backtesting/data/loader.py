from dataclasses import dataclass

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId, DatasetSpec
from backtesting.data.policy import expand_monthly_frame
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
    FRAME_KEYS = {
        DatasetId.QW_ADJ_C: "close",
        DatasetId.QW_ADJ_O: "open",
        DatasetId.QW_ADJ_H: "high",
        DatasetId.QW_ADJ_L: "low",
        DatasetId.QW_V: "volume",
        DatasetId.QW_MKTCAP: "market_cap",
        DatasetId.QW_K200_YN: "k200_yn",
    }

    def __init__(self, catalog: DataCatalog, store: ParquetStore) -> None:
        self.catalog = catalog
        self.store = store

    def load(self, request: LoadRequest) -> MarketData:
        if request.price_mode != "adj":
            raise ValueError(f"unsupported price_mode: {request.price_mode}")

        frames: dict[str, pd.DataFrame] = {}
        for dataset_id in request.datasets:
            spec = self.catalog.get(dataset_id)
            frame = self._load_frame(spec, request)
            key = self.FRAME_KEYS.get(dataset_id, spec.stem)
            frames[key] = frame
        return MarketData(
            frames=frames,
            universe=request.universe,
            benchmark=request.benchmark,
        )

    def _load_frame(self, spec: DatasetSpec, request: LoadRequest) -> pd.DataFrame:
        frame = self.store.read(spec.stem)
        if spec.validity == "daily":
            return frame.loc[request.start : request.end]
        if spec.validity == "month_only":
            calendar = pd.date_range(request.start, request.end, freq="D")
            return expand_monthly_frame(frame=frame, calendar=calendar, validity=spec.validity)
        raise ValueError(f"unsupported validity: {spec.validity}")
