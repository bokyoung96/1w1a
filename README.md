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

## Manual Validation

The smoke checks below use the current implementation and a small real subset of `raw/qw_adj_c.csv` from the repo root.

```powershell
python -c "from pathlib import Path; import tempfile; import pandas as pd; from root import ROOT; from backtesting.catalog import DataCatalog, DatasetId; from backtesting.ingest.pipeline import IngestJob; raw_path = ROOT.raw_path if ROOT.raw_path.exists() else ROOT.root.parents[1] / 'raw'; frame = pd.read_csv(raw_path / 'qw_adj_c.csv', nrows=5); frame = frame.rename(columns={frame.columns[0]: 'date'}); tmp = Path(tempfile.mkdtemp()); raw_dir = tmp / 'raw'; parquet_dir = tmp / 'parquet'; raw_dir.mkdir(); parquet_dir.mkdir(); frame.to_csv(raw_dir / 'qw_adj_c.csv', index=False); print(IngestJob(DataCatalog.default(), raw_dir, parquet_dir).run(DatasetId.QW_ADJ_C).to_dict())"
```

```powershell
python -c "import pandas as pd; from backtesting.engine.core import BacktestEngine; from backtesting.execution.costs import CostModel; close = pd.DataFrame({'A':[100,101,102],'B':[100,99,98]}, index=pd.date_range('2024-01-01', periods=3)); weights = pd.DataFrame({'A':[0.5,0.5,0.5],'B':[0.5,0.5,0.5]}, index=close.index); result = BacktestEngine(CostModel()).run(close=close, weights=weights, capital=1000.0, fill_mode='close'); print(result.equity.tail(1))"
```

```powershell
python -c "import pandas as pd; from backtesting.validation.session import ValidationSession; signal = pd.DataFrame({'A':[1.0,2.0]}, index=pd.date_range('2024-01-01', periods=2)); print(ValidationSession().run(signal=signal, lag_sensitive_datasets=['qw_eps_nfy1'], lag_map={}))"
```
