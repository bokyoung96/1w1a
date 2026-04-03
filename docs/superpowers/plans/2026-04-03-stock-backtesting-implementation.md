# 1w1a Stock Backtesting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a stock-only parquet-backed backtesting stack for `1w1a`, move broker code into `kis/`, and add analytics, validation, and IS/OOS workflows.

**Architecture:** The work is split into three layers: `kis/` for broker and config code, `backtesting/` for research and simulation, and `raw/ -> parquet/` for typed data access. The engine stays library-first, vectorized where useful, and explicit where execution realism matters.

**Tech Stack:** Python, pandas, pyarrow, pytest, tqdm, openpyxl

---

## File Map

### Existing files to modify

- `root.py`
- `config.py`
- `tools.py`
- `README.md`

### Existing files to move into `kis/`

- `config.py -> kis/config.py`
- `tools.py -> kis/tools.py`

### New package files

- `kis/__init__.py`
- `backtesting/__init__.py`
- `backtesting/catalog/__init__.py`
- `backtesting/catalog/enums.py`
- `backtesting/catalog/specs.py`
- `backtesting/catalog/catalog.py`
- `backtesting/ingest/__init__.py`
- `backtesting/ingest/io.py`
- `backtesting/ingest/normalize.py`
- `backtesting/ingest/report.py`
- `backtesting/ingest/pipeline.py`
- `backtesting/data/__init__.py`
- `backtesting/data/store.py`
- `backtesting/data/policy.py`
- `backtesting/data/loader.py`
- `backtesting/execution/__init__.py`
- `backtesting/execution/costs.py`
- `backtesting/execution/schedule.py`
- `backtesting/execution/fill.py`
- `backtesting/strategy/__init__.py`
- `backtesting/strategy/base.py`
- `backtesting/strategy/cross.py`
- `backtesting/strategy/timeseries.py`
- `backtesting/engine/__init__.py`
- `backtesting/engine/result.py`
- `backtesting/engine/core.py`
- `backtesting/analytics/__init__.py`
- `backtesting/analytics/perf.py`
- `backtesting/analytics/factor.py`
- `backtesting/validation/__init__.py`
- `backtesting/validation/split.py`
- `backtesting/validation/session.py`

### Test files

- `tests/conftest.py`
- `tests/kis/test_root.py`
- `tests/catalog/test_specs.py`
- `tests/ingest/test_pipeline.py`
- `tests/data/test_policy.py`
- `tests/data/test_loader.py`
- `tests/execution/test_schedule.py`
- `tests/execution/test_costs.py`
- `tests/strategy/test_cross.py`
- `tests/strategy/test_timeseries.py`
- `tests/engine/test_core.py`
- `tests/analytics/test_perf.py`
- `tests/analytics/test_factor.py`
- `tests/validation/test_split.py`
- `tests/validation/test_session.py`

## Task 1: Move Broker Code Into `kis/`

**Files:**
- Create: `kis/__init__.py`
- Create: `kis/config.py`
- Create: `kis/tools.py`
- Modify: `root.py`
- Modify: `README.md`
- Test: `tests/kis/test_root.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from root import ROOT


def test_root_exposes_repo_paths():
    assert ROOT.root.name == "1w1a"
    assert ROOT.config_path == ROOT.root / "config" / "config.json"
    assert ROOT.kis_path == ROOT.root / "kis"
    assert ROOT.raw_path == ROOT.root / "raw"
    assert ROOT.parquet_path == ROOT.root / "parquet"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/kis/test_root.py -v`
Expected: FAIL because `kis_path`, `raw_path`, and `parquet_path` do not exist on `RootPaths`

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RootPaths:
    root: Path

    @property
    def config_path(self) -> Path:
        return self.root / "config" / "config.json"

    @property
    def kis_path(self) -> Path:
        return self.root / "kis"

    @property
    def raw_path(self) -> Path:
        return self.root / "raw"

    @property
    def parquet_path(self) -> Path:
        return self.root / "parquet"
```

`kis/__init__.py`:

```python
from .config import KISAuth, KISConfig, setup_logging
from .tools import DataTools, RateLimiter, TimeTools

__all__ = [
    "DataTools",
    "KISAuth",
    "KISConfig",
    "RateLimiter",
    "TimeTools",
    "setup_logging",
]
```

- [ ] **Step 4: Move the current code into `kis/`**

`kis/config.py` should contain the current contents of `config.py`.

`kis/tools.py` should contain the current contents of `tools.py`.

`README.md` should be updated to:

```markdown
# 1w1a

1 week 1 alpha repository.

- `raw/`: source market files
- `kis/`: broker and config code
- `backtesting/`: research, simulation, analytics, validation
```

- [ ] **Step 5: Remove obsolete top-level modules**

Delete the contents of `config.py` and `tools.py` from the repo after their imports have been migrated. Do not keep duplicate wrapper modules unless a test proves they are still required.

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/kis/test_root.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add root.py README.md kis/__init__.py kis/config.py kis/tools.py tests/kis/test_root.py
git rm config.py tools.py
git commit -m "refactor: move broker code into kis package"
```

## Task 2: Add Core Types and Dataset Catalog

**Files:**
- Create: `backtesting/__init__.py`
- Create: `backtesting/types.py`
- Create: `backtesting/catalog/__init__.py`
- Create: `backtesting/catalog/enums.py`
- Create: `backtesting/catalog/specs.py`
- Create: `backtesting/catalog/catalog.py`
- Test: `tests/catalog/test_specs.py`

- [ ] **Step 1: Write the failing test**

```python
from backtesting.catalog import DataCatalog, DatasetId


def test_catalog_returns_known_spec():
    catalog = DataCatalog.default()
    spec = catalog.get(DatasetId.QW_ADJ_C)

    assert spec.id is DatasetId.QW_ADJ_C
    assert spec.stem == "qw_adj_c"
    assert spec.freq == "D"
    assert spec.kind == "price"
    assert spec.axis == "date_symbol"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/catalog/test_specs.py::test_catalog_returns_known_spec -v`
Expected: FAIL because the catalog package does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/catalog/enums.py`:

```python
from enum import Enum, unique


@unique
class DatasetId(str, Enum):
    QW_ADJ_C = "qw_adj_c"
    QW_ADJ_O = "qw_adj_o"
    QW_ADJ_H = "qw_adj_h"
    QW_ADJ_L = "qw_adj_l"
    QW_V = "qw_v"
    QW_MKTCAP = "qw_mktcap"
    QW_K200_YN = "qw_k200_yn"
```

`backtesting/catalog/specs.py`:

```python
from dataclasses import dataclass

from .enums import DatasetId


@dataclass(frozen=True, slots=True)
class DatasetSpec:
    id: DatasetId
    stem: str
    freq: str
    kind: str
    fill: str
    validity: str
    lag: int
    dtype: str
    axis: str = "date_symbol"
```

`backtesting/catalog/catalog.py`:

```python
from dataclasses import dataclass

from .enums import DatasetId
from .specs import DatasetSpec


@dataclass(slots=True)
class DataCatalog:
    specs: dict[DatasetId, DatasetSpec]

    @classmethod
    def default(cls) -> "DataCatalog":
        specs = {
            DatasetId.QW_ADJ_C: DatasetSpec(
                id=DatasetId.QW_ADJ_C,
                stem="qw_adj_c",
                freq="D",
                kind="price",
                fill="none",
                validity="daily",
                lag=0,
                dtype="float64",
            ),
        }
        return cls(specs=specs)

    def get(self, dataset_id: DatasetId) -> DatasetSpec:
        return self.specs[dataset_id]
```

- [ ] **Step 4: Expand the default catalog**

Add initial specs for:

- `qw_adj_o`
- `qw_adj_h`
- `qw_adj_l`
- `qw_v`
- `qw_mktcap`
- `qw_k200_yn`

Use short, explicit metadata values. Keep policy values as strings for the first iteration; richer enums can be added later if tests force it.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/catalog/test_specs.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/__init__.py backtesting/catalog/__init__.py backtesting/catalog/enums.py backtesting/catalog/specs.py backtesting/catalog/catalog.py tests/catalog/test_specs.py
git commit -m "feat: add dataset catalog and core types"
```

## Task 3: Build Raw-to-Parquet Ingestion and Reporting

**Files:**
- Create: `backtesting/ingest/__init__.py`
- Create: `backtesting/ingest/io.py`
- Create: `backtesting/ingest/normalize.py`
- Create: `backtesting/ingest/report.py`
- Create: `backtesting/ingest/pipeline.py`
- Create: `backtesting/data/store.py`
- Test: `tests/ingest/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.ingest.pipeline import IngestJob


def test_ingest_writes_parquet_and_report(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    parquet_dir = tmp_path / "parquet"
    raw_dir.mkdir()
    parquet_dir.mkdir()

    frame = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03"],
            "005930": [100.0, 101.0],
            "000660": [50.0, 49.5],
        }
    )
    frame.to_csv(raw_dir / "qw_adj_c.csv", index=False)

    job = IngestJob(
        catalog=DataCatalog.default(),
        raw_dir=raw_dir,
        parquet_dir=parquet_dir,
    )

    result = job.run(DatasetId.QW_ADJ_C)

    assert (parquet_dir / "qw_adj_c.parquet").exists()
    assert result.rows == 2
    assert result.columns == 2
    assert result.date_start.isoformat() == "2024-01-02"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/ingest/test_pipeline.py::test_ingest_writes_parquet_and_report -v`
Expected: FAIL because the ingestion pipeline does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/ingest/report.py`:

```python
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class IngestResult:
    stem: str
    rows: int
    columns: int
    date_start: date
    date_end: date
    missing: int
```

`backtesting/data/store.py`:

```python
from pathlib import Path

import pandas as pd


class ParquetStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, stem: str, frame: pd.DataFrame) -> Path:
        path = self.root / f"{stem}.parquet"
        frame.to_parquet(path, engine="pyarrow")
        return path

    def read(self, stem: str) -> pd.DataFrame:
        return pd.read_parquet(self.root / f"{stem}.parquet", engine="pyarrow")
```

`backtesting/ingest/pipeline.py`:

```python
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data.store import ParquetStore
from .report import IngestResult


@dataclass(slots=True)
class IngestJob:
    catalog: DataCatalog
    raw_dir: Path
    parquet_dir: Path

    def run(self, dataset_id: DatasetId) -> IngestResult:
        spec = self.catalog.get(dataset_id)
        path = self.raw_dir / f"{spec.stem}.csv"
        frame = pd.read_csv(path)
        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame.sort_values("date").set_index("date")

        store = ParquetStore(self.parquet_dir)
        store.write(spec.stem, frame)

        return IngestResult(
            stem=spec.stem,
            rows=len(frame),
            columns=len(frame.columns),
            date_start=frame.index.min().date(),
            date_end=frame.index.max().date(),
            missing=int(frame.isna().sum().sum()),
        )
```

- [ ] **Step 4: Add normalization and report detail**

Add support for:

- CSV and XLSX dispatch in `io.py`
- sorted date index
- duplicate date detection
- dtype summary
- shape summary
- report serialization helper

The report serializer should write a JSON file next to the parquet file:

```python
{
  "stem": "qw_adj_c",
  "rows": 2,
  "columns": 2,
  "missing": 0,
  "date_start": "2024-01-02",
  "date_end": "2024-01-03"
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/ingest/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/ingest/__init__.py backtesting/ingest/io.py backtesting/ingest/normalize.py backtesting/ingest/report.py backtesting/ingest/pipeline.py backtesting/data/store.py tests/ingest/test_pipeline.py
git commit -m "feat: add raw to parquet ingestion pipeline"
```

## Task 4: Add Policy-Aware Loading for Daily and Low-Frequency Data

**Files:**
- Create: `backtesting/data/__init__.py`
- Create: `backtesting/data/policy.py`
- Create: `backtesting/data/loader.py`
- Test: `tests/data/test_policy.py`
- Test: `tests/data/test_loader.py`

- [ ] **Step 1: Write the failing test for invalid-gap protection**

```python
import pandas as pd

from backtesting.data.policy import expand_monthly_frame


def test_expand_monthly_frame_keeps_missing_gap():
    frame = pd.DataFrame(
        {
            "005930": [1.0, 3.0],
        },
        index=pd.to_datetime(["2024-03-31", "2024-05-31"]),
    )

    expanded = expand_monthly_frame(
        frame,
        calendar=pd.date_range("2024-03-01", "2024-05-31", freq="D"),
        validity="month_only",
    )

    assert expanded.loc["2024-04-15", "005930"] != expanded.loc["2024-03-15", "005930"]
    assert pd.isna(expanded.loc["2024-04-15", "005930"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/data/test_policy.py::test_expand_monthly_frame_keeps_missing_gap -v`
Expected: FAIL because the policy module does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/data/policy.py`:

```python
import pandas as pd


def expand_monthly_frame(
    frame: pd.DataFrame,
    calendar: pd.DatetimeIndex,
    validity: str,
) -> pd.DataFrame:
    if validity != "month_only":
        raise ValueError(f"unsupported validity: {validity}")

    out = pd.DataFrame(index=calendar, columns=frame.columns, dtype="float64")
    for ts, row in frame.iterrows():
        month_mask = (calendar.year == ts.year) & (calendar.month == ts.month)
        out.loc[month_mask, :] = row.values
    return out
```

- [ ] **Step 4: Write the failing loader test**

```python
from pathlib import Path

import pandas as pd

from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data.loader import DataLoader, LoadRequest
from backtesting.data.store import ParquetStore


def test_loader_returns_market_data(tmp_path: Path):
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
```

- [ ] **Step 5: Implement the loader**

`backtesting/data/loader.py`:

```python
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
            frame = self.store.read(spec.stem).loc[request.start:request.end]
            key = "close" if spec.stem == "qw_adj_c" else spec.stem
            frames[key] = frame
        return MarketData(frames=frames, universe=request.universe, benchmark=request.benchmark)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/data/test_policy.py tests/data/test_loader.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backtesting/data/__init__.py backtesting/data/policy.py backtesting/data/loader.py tests/data/test_policy.py tests/data/test_loader.py
git commit -m "feat: add policy aware data loading"
```

## Task 5: Add Scheduling, Fill Rules, and Cost Model

**Files:**
- Create: `backtesting/execution/__init__.py`
- Create: `backtesting/execution/schedule.py`
- Create: `backtesting/execution/fill.py`
- Create: `backtesting/execution/costs.py`
- Test: `tests/execution/test_schedule.py`
- Test: `tests/execution/test_costs.py`

- [ ] **Step 1: Write the failing schedule test**

```python
import pandas as pd

from backtesting.execution.schedule import WeeklySchedule


def test_weekly_schedule_marks_rebalance_dates():
    index = pd.date_range("2024-01-01", periods=10, freq="D")
    schedule = WeeklySchedule()
    flags = schedule.flags(index)

    assert flags.sum() >= 1
    assert flags.index.equals(index)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/execution/test_schedule.py::test_weekly_schedule_marks_rebalance_dates -v`
Expected: FAIL because the execution schedule module does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/execution/schedule.py`:

```python
from dataclasses import dataclass

import pandas as pd


class RebalanceSchedule:
    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        raise NotImplementedError


@dataclass(slots=True)
class WeeklySchedule(RebalanceSchedule):
    weekday: int = 4

    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        return pd.Series(index.weekday == self.weekday, index=index)
```

- [ ] **Step 4: Write the failing cost test**

```python
from backtesting.execution.costs import CostModel, TradeCost


def test_cost_model_applies_fee_tax_and_slippage():
    model = CostModel(fee=0.001, sell_tax=0.002, slippage=0.001)
    cost = model.calc(price=100.0, qty=10.0, side="sell")

    assert isinstance(cost, TradeCost)
    assert round(cost.total, 4) == 4.0
```

- [ ] **Step 5: Implement the cost model**

`backtesting/execution/costs.py`:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TradeCost:
    fee: float
    tax: float
    slippage: float

    @property
    def total(self) -> float:
        return self.fee + self.tax + self.slippage


@dataclass(frozen=True, slots=True)
class CostModel:
    fee: float = 0.0
    sell_tax: float = 0.0
    slippage: float = 0.0
    borrow: float = 0.0

    def calc(self, price: float, qty: float, side: str) -> TradeCost:
        gross = abs(price * qty)
        fee = gross * self.fee
        tax = gross * self.sell_tax if side == "sell" else 0.0
        slip = gross * self.slippage
        return TradeCost(fee=fee, tax=tax, slippage=slip)
```

- [ ] **Step 6: Add daily, monthly, and custom schedules**

Extend `schedule.py` with:

```python
@dataclass(slots=True)
class DailySchedule(RebalanceSchedule):
    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        return pd.Series(True, index=index)


@dataclass(slots=True)
class MonthlySchedule(RebalanceSchedule):
    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        month_change = pd.Series(index.to_period("M"), index=index).ne(
            pd.Series(index.to_period("M"), index=index).shift(-1)
        )
        return month_change.fillna(True)


@dataclass(slots=True)
class CustomSchedule(RebalanceSchedule):
    dates: pd.DatetimeIndex

    def flags(self, index: pd.DatetimeIndex) -> pd.Series:
        return pd.Series(index.isin(self.dates), index=index)
```

`backtesting/execution/fill.py`:

```python
import pandas as pd


def fill_prices(
    close: pd.DataFrame,
    open_: pd.DataFrame | None,
    fill_mode: str,
) -> pd.DataFrame:
    if fill_mode == "close":
        return close
    if fill_mode == "next_open":
        if open_ is None:
            raise ValueError("open prices required for next_open")
        return open_.shift(-1)
    raise ValueError(f"unsupported fill_mode: {fill_mode}")
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/execution/test_schedule.py tests/execution/test_costs.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backtesting/execution/__init__.py backtesting/execution/schedule.py backtesting/execution/fill.py backtesting/execution/costs.py tests/execution/test_schedule.py tests/execution/test_costs.py
git commit -m "feat: add execution schedule and cost model"
```

## Task 6: Add Strategy Interfaces and Basic Implementations

**Files:**
- Create: `backtesting/strategy/__init__.py`
- Create: `backtesting/strategy/base.py`
- Create: `backtesting/strategy/cross.py`
- Create: `backtesting/strategy/timeseries.py`
- Test: `tests/strategy/test_cross.py`
- Test: `tests/strategy/test_timeseries.py`

- [ ] **Step 1: Write the failing cross-sectional test**

```python
import pandas as pd

from backtesting.strategy.cross import RankLongOnly


def test_rank_long_only_selects_top_names():
    factor = pd.Series({"A": 1.0, "B": 3.0, "C": 2.0})
    strategy = RankLongOnly(top_n=2)

    weights = strategy.target_weights(factor)

    assert weights["B"] == 0.5
    assert weights["C"] == 0.5
    assert weights.get("A", 0.0) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/strategy/test_cross.py::test_rank_long_only_selects_top_names -v`
Expected: FAIL because the strategy module does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/strategy/base.py`:

```python
import pandas as pd


class BaseStrategy:
    def target_weights(self, signal: pd.Series) -> pd.Series:
        raise NotImplementedError
```

`backtesting/strategy/cross.py`:

```python
from dataclasses import dataclass

import pandas as pd

from .base import BaseStrategy


@dataclass(slots=True)
class RankLongOnly(BaseStrategy):
    top_n: int

    def target_weights(self, signal: pd.Series) -> pd.Series:
        winners = signal.sort_values(ascending=False).head(self.top_n)
        return pd.Series(1.0 / len(winners), index=winners.index)
```

- [ ] **Step 4: Add long-short and time-series extension points**

Add:

```python
@dataclass(slots=True)
class RankLongShort(BaseStrategy):
    top_n: int
    bottom_n: int

    def target_weights(self, signal: pd.Series) -> pd.Series:
        long_leg = signal.sort_values(ascending=False).head(self.top_n)
        short_leg = signal.sort_values(ascending=True).head(self.bottom_n)
        weights = pd.Series(0.0, index=signal.index)
        weights.loc[long_leg.index] = 1.0 / self.top_n
        weights.loc[short_leg.index] = -1.0 / self.bottom_n
        return weights
```

`backtesting/strategy/timeseries.py`:

```python
from dataclasses import dataclass

import pandas as pd

from .base import BaseStrategy


@dataclass(slots=True)
class ThresholdTrend(BaseStrategy):
    threshold: float = 0.0

    def target_weights(self, signal: pd.Series) -> pd.Series:
        return signal.gt(self.threshold).astype(float)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/strategy/test_cross.py tests/strategy/test_timeseries.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/strategy/__init__.py backtesting/strategy/base.py backtesting/strategy/cross.py backtesting/strategy/timeseries.py tests/strategy/test_cross.py tests/strategy/test_timeseries.py
git commit -m "feat: add strategy interfaces and baseline strategies"
```

## Task 7: Build the Backtest Engine

**Files:**
- Create: `backtesting/engine/__init__.py`
- Create: `backtesting/engine/result.py`
- Create: `backtesting/engine/core.py`
- Test: `tests/engine/test_core.py`

- [ ] **Step 1: Write the failing engine test**

```python
import pandas as pd

from backtesting.engine.core import BacktestEngine
from backtesting.execution.costs import CostModel


def test_engine_tracks_equity_from_weights():
    close = pd.DataFrame(
        {
            "A": [100.0, 110.0],
            "B": [100.0, 90.0],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    weights = pd.DataFrame(
        {
            "A": [0.5, 0.5],
            "B": [0.5, 0.5],
        },
        index=close.index,
    )

    engine = BacktestEngine(cost=CostModel())
    result = engine.run(close=close, weights=weights, capital=1000.0)

    assert result.equity.iloc[0] == 1000.0
    assert round(result.equity.iloc[-1], 2) == 1000.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/engine/test_core.py::test_engine_tracks_equity_from_weights -v`
Expected: FAIL because the backtest engine does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/engine/result.py`:

```python
from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    weights: pd.DataFrame
    qty: pd.DataFrame
    turnover: pd.Series
```

`backtesting/engine/core.py`:

```python
from dataclasses import dataclass

import pandas as pd

from backtesting.engine.result import BacktestResult
from backtesting.execution.costs import CostModel


@dataclass(slots=True)
class BacktestEngine:
    cost: CostModel

    def run(
        self,
        close: pd.DataFrame,
        weights: pd.DataFrame,
        capital: float,
    ) -> BacktestResult:
        weights = weights.reindex_like(close).fillna(0.0)
        returns = close.pct_change().fillna(0.0)
        port_ret = (weights.shift().fillna(0.0) * returns).sum(axis=1)
        equity = capital * (1.0 + port_ret).cumprod()
        qty = weights.mul(equity, axis=0).div(close.replace(0.0, pd.NA)).fillna(0.0)
        turnover = weights.diff().abs().sum(axis=1).fillna(weights.abs().sum(axis=1))
        return BacktestResult(equity=equity, returns=port_ret, weights=weights, qty=qty, turnover=turnover)
```

- [ ] **Step 4: Add execution realism**

Expand `BacktestEngine.run` to accept:

- `open: pd.DataFrame | None = None`
- `tradable: pd.DataFrame | None = None`
- `fill_mode: str = "next_open"`
- `allow_fractional: bool = True`
- `show_progress: bool = False`

When `show_progress=True`, wrap the rebalancing loop with:

```python
from tqdm.auto import tqdm

for ts in tqdm(index[1:], desc="backtest", disable=not show_progress):
    ...
```

If `allow_fractional` is `False`, quantize target quantity using:

```python
target_qty = target_qty.fillna(0.0).round(0)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/engine/test_core.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/engine/__init__.py backtesting/engine/result.py backtesting/engine/core.py tests/engine/test_core.py
git commit -m "feat: add backtest engine core"
```

## Task 8: Add General and Factor Analytics

**Files:**
- Create: `backtesting/analytics/__init__.py`
- Create: `backtesting/analytics/perf.py`
- Create: `backtesting/analytics/factor.py`
- Test: `tests/analytics/test_perf.py`
- Test: `tests/analytics/test_factor.py`

- [ ] **Step 1: Write the failing performance test**

```python
import pandas as pd

from backtesting.analytics.perf import summarize_perf


def test_summarize_perf_returns_core_metrics():
    returns = pd.Series([0.0, 0.01, -0.02, 0.03], index=pd.date_range("2024-01-01", periods=4))
    summary = summarize_perf(returns)

    assert "cagr" in summary
    assert "mdd" in summary
    assert "sharpe" in summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/analytics/test_perf.py::test_summarize_perf_returns_core_metrics -v`
Expected: FAIL because the analytics module does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/analytics/perf.py`:

```python
import numpy as np
import pandas as pd


def summarize_perf(returns: pd.Series) -> dict[str, float]:
    equity = (1.0 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    years = max(len(returns) / 252.0, 1 / 252.0)
    cagr = equity.iloc[-1] ** (1 / years) - 1.0
    sharpe = 0.0 if returns.std() == 0 else np.sqrt(252.0) * returns.mean() / returns.std()
    return {
        "cagr": float(cagr),
        "mdd": float(drawdown.min()),
        "sharpe": float(sharpe),
    }
```

- [ ] **Step 4: Add factor analytics**

`backtesting/analytics/factor.py`:

```python
import pandas as pd


def quantile_returns(signal: pd.DataFrame, fwd_returns: pd.DataFrame, q: int = 5) -> pd.DataFrame:
    rows = []
    for ts in signal.index.intersection(fwd_returns.index):
        ranked = pd.qcut(signal.loc[ts].rank(method="first"), q=q, labels=False, duplicates="drop")
        frame = pd.DataFrame({"bucket": ranked, "ret": fwd_returns.loc[ts]})
        rows.append(frame.groupby("bucket")["ret"].mean().rename(ts))
    return pd.DataFrame(rows)


def rank_ic(signal: pd.DataFrame, fwd_returns: pd.DataFrame) -> pd.Series:
    out = {}
    for ts in signal.index.intersection(fwd_returns.index):
        out[ts] = signal.loc[ts].corr(fwd_returns.loc[ts], method="spearman")
    return pd.Series(out)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/analytics/test_perf.py tests/analytics/test_factor.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/analytics/__init__.py backtesting/analytics/perf.py backtesting/analytics/factor.py tests/analytics/test_perf.py tests/analytics/test_factor.py
git commit -m "feat: add performance and factor analytics"
```

## Task 9: Add Validation Session and IS/OOS Split Tools

**Files:**
- Create: `backtesting/validation/__init__.py`
- Create: `backtesting/validation/split.py`
- Create: `backtesting/validation/session.py`
- Test: `tests/validation/test_split.py`
- Test: `tests/validation/test_session.py`

- [ ] **Step 1: Write the failing split test**

```python
import pandas as pd

from backtesting.validation.split import SplitConfig, split_frame


def test_split_frame_returns_is_and_oos():
    frame = pd.DataFrame({"x": range(10)}, index=pd.date_range("2024-01-01", periods=10))
    config = SplitConfig(is_start="2024-01-01", is_end="2024-01-05", oos_start="2024-01-06", oos_end="2024-01-10")

    split = split_frame(frame, config)

    assert len(split.is_frame) == 5
    assert len(split.oos_frame) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/validation/test_split.py::test_split_frame_returns_is_and_oos -v`
Expected: FAIL because the validation package does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/validation/split.py`:

```python
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class SplitConfig:
    is_start: str
    is_end: str
    oos_start: str
    oos_end: str


@dataclass(frozen=True, slots=True)
class SplitResult:
    is_frame: pd.DataFrame
    oos_frame: pd.DataFrame


def split_frame(frame: pd.DataFrame, config: SplitConfig) -> SplitResult:
    return SplitResult(
        is_frame=frame.loc[config.is_start:config.is_end],
        oos_frame=frame.loc[config.oos_start:config.oos_end],
    )
```

- [ ] **Step 4: Write the failing validation session test**

```python
import pandas as pd

from backtesting.validation.session import ValidationSession


def test_validation_session_flags_missing_lag():
    signal = pd.DataFrame({"A": [1.0, 2.0]}, index=pd.date_range("2024-01-01", periods=2))
    session = ValidationSession()
    report = session.run(signal=signal, lag_sensitive=["qw_eps_nfy1"], lag_map={})

    assert report["warnings"] == ["missing_lag:qw_eps_nfy1"]
```

- [ ] **Step 5: Implement the validation session**

`backtesting/validation/session.py`:

```python
from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class ValidationSession:
    warnings: list[str] = field(default_factory=list)

    def run(
        self,
        signal: pd.DataFrame,
        lag_sensitive: list[str],
        lag_map: dict[str, int],
    ) -> dict[str, list[str]]:
        warnings = []
        for name in lag_sensitive:
            if name not in lag_map:
                warnings.append(f"missing_lag:{name}")
        if signal.index.has_duplicates:
            warnings.append("duplicate_index")
        return {"warnings": warnings}
```

- [ ] **Step 6: Extend validation checks beyond missing lag**

Add explicit checks for:

- stale-value propagation warnings when an expanded low-frequency dataset fills dates outside its declared validity period
- missing benchmark alignment warnings when benchmark index does not cover the signal index
- suspicious sparse coverage warnings when a signal row is mostly missing

Use short warning names:

```python
"stale_gap:<dataset>"
"short_benchmark"
"sparse_signal"
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/validation/test_split.py tests/validation/test_session.py -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backtesting/validation/__init__.py backtesting/validation/split.py backtesting/validation/session.py tests/validation/test_split.py tests/validation/test_session.py
git commit -m "feat: add validation session and split tools"
```

## Task 10: Add End-to-End Smoke Coverage and Docs

**Files:**
- Modify: `README.md`
- Create: `tests/conftest.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
def test_import_smoke():
    from backtesting.catalog import DataCatalog
    from backtesting.engine.core import BacktestEngine
    from backtesting.validation.session import ValidationSession
    from kis import KISConfig

    assert DataCatalog is not None
    assert BacktestEngine is not None
    assert ValidationSession is not None
    assert KISConfig is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL until all package exports are wired correctly

- [ ] **Step 3: Wire package exports**

Each package `__init__.py` should export short, stable public names. Example:

```python
from .catalog import DataCatalog
from .catalog.enums import DatasetId
from .engine.core import BacktestEngine

__all__ = ["BacktestEngine", "DataCatalog", "DatasetId"]
```

- [ ] **Step 4: Update the README with the new workflow**

Add a short usage block:

```python
from root import ROOT
from backtesting.catalog import DataCatalog, DatasetId
from backtesting.data.loader import DataLoader, LoadRequest
from backtesting.data.store import ParquetStore

catalog = DataCatalog.default()
store = ParquetStore(ROOT.parquet_path)
loader = DataLoader(catalog, store)
data = loader.load(LoadRequest(datasets=[DatasetId.QW_ADJ_C], start="2020-01-01", end="2020-12-31"))
```

- [ ] **Step 5: Run the full test suite**

Run: `pytest tests -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add README.md tests/conftest.py tests/test_smoke.py backtesting/__init__.py backtesting/catalog/__init__.py backtesting/data/__init__.py backtesting/execution/__init__.py backtesting/strategy/__init__.py backtesting/engine/__init__.py backtesting/analytics/__init__.py backtesting/validation/__init__.py
git commit -m "test: add smoke coverage and package exports"
```

## Task 11: Run Manual Validation and Example Sessions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Run ingestion on a small real dataset subset**

Run:

```bash
python -c "from root import ROOT; from backtesting.catalog import DataCatalog, DatasetId; from backtesting.ingest.pipeline import IngestJob; job = IngestJob(DataCatalog.default(), ROOT.raw_path, ROOT.parquet_path); print(job.run(DatasetId.QW_ADJ_C))"
```

Expected: prints a result object with dates, rows, columns, and missing counts

- [ ] **Step 2: Run a tiny interactive backtest**

Run:

```bash
python -c "import pandas as pd; from backtesting.engine.core import BacktestEngine; from backtesting.execution.costs import CostModel; close = pd.DataFrame({'A':[100,101,102],'B':[100,99,98]}, index=pd.date_range('2024-01-01', periods=3)); weights = pd.DataFrame({'A':[0.5,0.5,0.5],'B':[0.5,0.5,0.5]}, index=close.index); result = BacktestEngine(CostModel()).run(close=close, weights=weights, capital=1000.0); print(result.equity.tail(1))"
```

Expected: prints the final equity series without exceptions

- [ ] **Step 3: Run a validation session**

Run:

```bash
python -c "import pandas as pd; from backtesting.validation.session import ValidationSession; signal = pd.DataFrame({'A':[1.0,2.0]}, index=pd.date_range('2024-01-01', periods=2)); print(ValidationSession().run(signal=signal, lag_sensitive=['qw_eps_nfy1'], lag_map={}))"
```

Expected: prints `{'warnings': ['missing_lag:qw_eps_nfy1']}`

- [ ] **Step 4: Add these commands to the README**

Document:

- ingest smoke command
- backtest smoke command
- validation smoke command

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add manual validation workflow"
```

## Self-Review

### Spec coverage

- `raw -> parquet` with validation report: Task 3
- `kis/` package move: Task 1
- `DatasetId`, `DatasetSpec`, `DataCatalog`: Task 2
- low-frequency validity and lag protection: Task 4 and Task 9
- cross-sectional engine and time-series extension: Task 6 and Task 7
- daily, weekly, monthly, custom schedules: Task 5
- cost, tax, slippage, borrow hooks: Task 5 and Task 7
- quantity-based engine with optional fractional support: Task 7
- benchmark and universe injection: Task 4 and Task 7
- qlib-style analytics and factor research: Task 8
- validation session: Task 9
- IS/OOS workflow: Task 9
- interactive-window-friendly library API: Task 1 and Task 10

### Placeholder scan

- No `TODO`
- No `TBD`
- No "implement later"
- All tasks include explicit files, commands, and code snippets

### Type consistency

- `DatasetId`, `DatasetSpec`, `DataCatalog` are introduced before use
- `LoadRequest` and `MarketData` are introduced before engine usage
- `BacktestResult` is introduced before analytics references it
- `SplitConfig` and `ValidationSession` are introduced before manual workflow references them
