# 1w1a

1 week 1 alpha repository.

- `raw/`: source market files
- `kis/`: broker and config code

## Quick Start

```python
from pathlib import Path

from backtesting import DataCatalog, DataLoader, LoadRequest, ParquetStore
from backtesting.catalog import DatasetId

catalog = DataCatalog.default()
store = ParquetStore(Path("parquet"))
loader = DataLoader(catalog, store)

# The parquet directory must already be populated by the ingest step
# before calling `loader.load(...)`.
market = loader.load(
    LoadRequest(
        datasets=[DatasetId.QW_ADJ_C, DatasetId.QW_V],
        start="2024-01-02",
        end="2024-01-31",
    )
)

close = market.frames["close"]
volume = market.frames["volume"]
```
