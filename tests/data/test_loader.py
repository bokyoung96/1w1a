from pathlib import Path

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data.loader import DataLoader, LoadRequest
from backtesting.data.store import ParquetStore


def test_loader_returns_market_data(tmp_path: Path) -> None:
    parquet_dir = tmp_path / "parquet"
    parquet_dir.mkdir()
    store = ParquetStore(parquet_dir)
    store.write(
        "qw_adj_c",
        pd.DataFrame(
            {"005930": [100.0, 101.0]},
            index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
        ),
    )

    loader = DataLoader(DataCatalog.default(), store)
    data = loader.load(
        LoadRequest(
            datasets=[DatasetId.QW_ADJ_C],
            start="2024-01-02",
            end="2024-01-03",
        )
    )

    assert "close" in data.frames
    assert list(data.frames["close"].columns) == ["005930"]
