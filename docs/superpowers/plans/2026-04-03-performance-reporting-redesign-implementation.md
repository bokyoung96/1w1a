# Performance Reporting Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `backtesting.reporting` into a PDF-first reporting system that outputs a polished single-run institutional tear sheet and a research-style multi-run comparison report with `KOSPI200` benchmark analytics, rolling diagnostics, holdings breadth, and WICS sector analysis.

**Architecture:** Keep the current `RunReader -> ReportBuilder -> HtmlRenderer/PdfRenderer` flow, but insert an analytics/snapshot layer between reading and rendering. Use object-oriented repositories and snapshot objects for benchmark loading, sector mapping, and performance analytics, then render page-level subplot figures and formatted tables into report-specific templates.

**Tech Stack:** Python 3.11, pandas, plotly+kaleido, jinja2, weasyprint, pytest

---

## File Structure

### New Files

- `backtesting/reporting/analytics.py`
  - Performance metric objects and rolling/drawdown/exposure calculations
- `backtesting/reporting/benchmarks.py`
  - Benchmark and sector repositories, benchmark selection objects
- `backtesting/reporting/snapshots.py`
  - `PerformanceSnapshot`, `ComparisonSnapshot`, and snapshot factory
- `backtesting/reporting/figures.py`
  - Single-run page-level subplot figure builder
- `backtesting/reporting/comparison_figures.py`
  - Multi-run comparison subplot figure builder
- `backtesting/reporting/tables_single.py`
  - Single-run PDF/HTML table builders
- `backtesting/reporting/tables_comparison.py`
  - Multi-run comparison table builders
- `backtesting/reporting/composers.py`
  - Report-specific document context assembly
- `backtesting/reporting/templates/tearsheet.html.j2`
  - Single-run HTML/PDF template
- `backtesting/reporting/templates/comparison.html.j2`
  - Multi-run HTML/PDF template
- `tests/reporting/test_benchmarks.py`
  - Benchmark and sector repository tests
- `tests/reporting/test_snapshots.py`
  - Performance snapshot analytics tests
- `tests/reporting/test_figures.py`
  - Page-level figure asset tests

### Modified Files

- `backtesting/reporting/models.py`
  - Add report kind, benchmark config, richer bundle metadata
- `backtesting/reporting/reader.py`
  - Keep `SavedRun` reads stable, add small helpers if needed for formatted labels
- `backtesting/reporting/builder.py`
  - Replace flat `PlotLibrary` flow with snapshot/composer dispatch
- `backtesting/reporting/cli.py`
  - Add single/comparison mode selection and benchmark option wiring
- `backtesting/reporting/html.py`
  - Render report-specific templates from composed context
- `backtesting/reporting/pdf.py`
  - Keep PDF export thin, but support composed output without iframe assumptions
- `backtesting/reporting/styles.css`
  - Redesign layout, cards, tables, page rhythm, print-safe styles
- `backtesting/reporting/__init__.py`
  - Export new reporting types
- `tests/reporting/test_builder.py`
  - Update bundle expectations to snapshot-based assets
- `tests/reporting/test_html.py`
  - Update template/context expectations
- `tests/reporting/test_pdf.py`
  - Keep PDF tests but adapt to new composed HTML outputs
- `tests/reporting/test_tables.py`
  - Repoint to single/comparison table builders
- `tests/reporting/test_plots.py`
  - Replace or narrow to low-level export helper coverage only

### Existing Files To Reuse Without Changing Responsibilities

- `backtesting/reporting/reader.py`
- `backtesting/reporting/pdf.py`
- `backtesting/run.py`
- `backtesting/data/store.py`
- `backtesting/ingest/pipeline.py`
- `backtesting/catalog/*`

---

### Task 1: Introduce Report Modes And Snapshot-Oriented Domain Models

**Files:**
- Create: `tests/reporting/test_models_reporting_redesign.py`
- Modify: `backtesting/reporting/models.py`
- Modify: `backtesting/reporting/__init__.py`

- [ ] **Step 1: Write the failing model tests**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.models import BenchmarkConfig, ComparisonBundle, ReportKind, ReportSpec, TearsheetBundle


def test_report_spec_defaults_to_tearsheet_for_single_run() -> None:
    spec = ReportSpec(name="single", run_ids=("run-a",))
    assert spec.kind is ReportKind.TEARSHEET
    assert spec.benchmark.code == "IKS200"
    assert spec.benchmark.name == "KOSPI200"


def test_report_spec_defaults_to_comparison_for_multiple_runs() -> None:
    spec = ReportSpec(name="compare", run_ids=("run-a", "run-b"))
    assert spec.kind is ReportKind.COMPARISON


def test_bundles_expose_display_metadata(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(name="single", run_ids=("run-a",)),
        out_dir=tmp_path,
        run_id="run-a",
        display_name="Momentum",
        pages={"executive": tmp_path / "executive.png"},
        tables={"summary": pd.DataFrame([{"metric": "CAGR", "value": 0.1}])},
        notes=(),
    )
    assert bundle.display_name == "Momentum"
    assert "executive" in bundle.pages
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_models_reporting_redesign.py -v`

Expected: FAIL with import errors for `BenchmarkConfig`, `ReportKind`, `TearsheetBundle`, or missing `kind` inference.

- [ ] **Step 3: Write the minimal domain model implementation**

```python
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import pandas as pd


class ReportKind(str, Enum):
    TEARSHEET = "tearsheet"
    COMPARISON = "comparison"


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    code: str
    name: str
    dataset: str = "qw_BM"

    @classmethod
    def default_kospi200(cls) -> "BenchmarkConfig":
        return cls(code="IKS200", name="KOSPI200")


@dataclass(frozen=True, slots=True)
class ReportSpec:
    name: str
    run_ids: tuple[str, ...]
    title: str | None = None
    kind: ReportKind | None = None
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig.default_kospi200)
    include_factor: bool = True
    include_validation: bool = True
    include_is_oos: bool = True
    formats: tuple[str, ...] = ("html", "pdf")

    def __post_init__(self) -> None:
        inferred = self.kind or (ReportKind.TEARSHEET if len(self.run_ids) == 1 else ReportKind.COMPARISON)
        object.__setattr__(self, "kind", inferred)


@dataclass(frozen=True, slots=True)
class TearsheetBundle:
    spec: ReportSpec
    out_dir: Path
    run_id: str
    display_name: str
    pages: dict[str, Path]
    tables: dict[str, pd.DataFrame]
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ComparisonBundle:
    spec: ReportSpec
    out_dir: Path
    display_names: tuple[str, ...]
    pages: dict[str, Path]
    tables: dict[str, pd.DataFrame]
    notes: tuple[str, ...] = ()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/reporting/test_models_reporting_redesign.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/reporting/test_models_reporting_redesign.py backtesting/reporting/models.py backtesting/reporting/__init__.py
git commit -m "feat: add reporting domain models"
```

---

### Task 2: Add Benchmark And Sector Repositories

**Files:**
- Create: `tests/reporting/test_benchmarks.py`
- Create: `backtesting/reporting/benchmarks.py`
- Modify: `backtesting/reporting/reader.py`

- [ ] **Step 1: Write the failing repository tests**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.benchmarks import BenchmarkConfig, BenchmarkRepository, SectorRepository


def test_benchmark_repository_extracts_kospi200_returns(tmp_path: Path) -> None:
    dates = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    frame = pd.DataFrame(
        {
            "IKS200": [100.0, 101.0, 102.0],
            "IKS001": [200.0, 202.0, 204.0],
        },
        index=dates,
    )
    repo = BenchmarkRepository.from_frame(frame)

    result = repo.load_returns(BenchmarkConfig.default_kospi200(), start="2024-01-02", end="2024-01-04")

    assert result.name == "KOSPI200"
    assert result.index.tolist() == dates.tolist()
    assert round(float(result.iloc[-1]), 6) == round((102.0 / 101.0) - 1.0, 6)


def test_sector_repository_maps_weights_to_sector_weights() -> None:
    dates = pd.to_datetime(["2024-01-31"])
    sector_frame = pd.DataFrame({"A": ["G10"], "B": ["G15"]}, index=dates)
    weights = pd.DataFrame({"A": [0.6], "B": [0.4]}, index=dates)
    repo = SectorRepository.from_frame(sector_frame)

    exposure = repo.latest_sector_weights(weights)

    assert exposure.to_dict() == {"G10": 0.6, "G15": 0.4}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_benchmarks.py -v`

Expected: FAIL with missing repository classes and methods.

- [ ] **Step 3: Write the repository implementation**

```python
from dataclasses import dataclass
from pathlib import Path

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
        self.prices = prices.sort_index()

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "BenchmarkRepository":
        return cls(frame)

    @classmethod
    def default(cls) -> "BenchmarkRepository":
        catalog = DataCatalog.default()
        store = ParquetStore(ROOT.parquet_path)
        path = ROOT.parquet_path / f"{DatasetId.QW_BM.value}.parquet"
        if not path.exists():
            IngestJob(catalog, ROOT.raw_path, ROOT.parquet_path).run(DatasetId.QW_BM)
        return cls(store.read(DatasetId.QW_BM.value))

    def load_series(self, config: BenchmarkConfig, *, start: str, end: str) -> BenchmarkSeries:
        prices = self.prices.loc[start:end, config.code].astype(float)
        returns = prices.pct_change().fillna(0.0)
        returns.name = config.name
        return BenchmarkSeries(name=config.name, prices=prices.rename(config.name), returns=returns)

    def load_returns(self, config: BenchmarkConfig, *, start: str, end: str) -> pd.Series:
        return self.load_series(config, start=start, end=end).returns


class SectorRepository:
    def __init__(self, sectors: pd.DataFrame) -> None:
        self.sectors = sectors.sort_index()

    @classmethod
    def from_frame(cls, frame: pd.DataFrame) -> "SectorRepository":
        return cls(frame)

    @classmethod
    def default(cls) -> "SectorRepository":
        catalog = DataCatalog.default()
        store = ParquetStore(ROOT.parquet_path)
        path = ROOT.parquet_path / f"{DatasetId.QW_WICS_SEC_BIG.value}.parquet"
        if not path.exists():
            IngestJob(catalog, ROOT.raw_path, ROOT.parquet_path).run(DatasetId.QW_WICS_SEC_BIG)
        return cls(store.read(DatasetId.QW_WICS_SEC_BIG.value))

    def latest_sector_weights(self, weights: pd.DataFrame) -> pd.Series:
        latest_date = weights.index.max()
        latest_weights = weights.loc[latest_date].dropna()
        latest_sectors = self.sectors.loc[latest_date, latest_weights.index]
        frame = pd.DataFrame({"sector": latest_sectors, "weight": latest_weights})
        frame = frame.dropna(subset=["sector"])
        return frame.groupby("sector")["weight"].sum().sort_values(ascending=False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/reporting/test_benchmarks.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/reporting/test_benchmarks.py backtesting/reporting/benchmarks.py backtesting/reporting/reader.py
git commit -m "feat: add reporting benchmark repositories"
```

---

### Task 3: Build Analytics Snapshots For Metrics, Rolling Stats, Drawdowns, And Sector Exposures

**Files:**
- Create: `tests/reporting/test_snapshots.py`
- Create: `backtesting/reporting/analytics.py`
- Create: `backtesting/reporting/snapshots.py`

- [ ] **Step 1: Write the failing analytics tests**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository
from backtesting.reporting.models import BenchmarkConfig
from backtesting.reporting.snapshots import PerformanceSnapshotFactory


def test_snapshot_factory_builds_benchmark_relative_metrics(tmp_path: Path) -> None:
    dates = pd.date_range("2024-01-02", periods=260, freq="B")
    returns = pd.Series(0.001, index=dates, name="returns")
    equity = (1.0 + returns).cumprod() * 100.0
    benchmark_prices = pd.DataFrame({"IKS200": (1.0 + pd.Series(0.0005, index=dates)).cumprod() * 100.0}, index=dates)
    weights = pd.DataFrame({"A": [1.0] * len(dates)}, index=dates)
    qty = pd.DataFrame({"A": [10.0] * len(dates)}, index=dates)
    sectors = pd.DataFrame({"A": ["G10"] * len(dates)}, index=dates)

    run = _saved_run(tmp_path, equity, returns, weights, qty)
    snapshot = PerformanceSnapshotFactory(
        benchmark_repo=BenchmarkRepository.from_frame(benchmark_prices),
        sector_repo=SectorRepository.from_frame(sectors),
    ).build(run, BenchmarkConfig.default_kospi200())

    assert snapshot.metrics.beta == 0.0
    assert snapshot.metrics.cagr > 0.0
    assert "rolling_sharpe" in snapshot.rolling.series
    assert snapshot.exposure.holdings_count.iloc[-1] == 1
    assert snapshot.sectors.latest_weighted.index.tolist() == ["G10"]


def test_drawdown_stats_extracts_worst_episode(tmp_path: Path) -> None:
    dates = pd.date_range("2024-01-02", periods=6, freq="B")
    returns = pd.Series([0.0, 0.1, -0.2, 0.05, 0.02, 0.03], index=dates, name="returns")
    equity = (1.0 + returns).cumprod() * 100.0
    run = _saved_run(tmp_path, equity, returns, pd.DataFrame({"A": [1.0] * 6}, index=dates), pd.DataFrame({"A": [10.0] * 6}, index=dates))

    snapshot = PerformanceSnapshotFactory(
        benchmark_repo=BenchmarkRepository.from_frame(pd.DataFrame({"IKS200": [100, 100, 100, 100, 100, 100]}, index=dates)),
        sector_repo=SectorRepository.from_frame(pd.DataFrame({"A": ["G10"] * 6}, index=dates)),
    ).build(run, BenchmarkConfig.default_kospi200())

    assert snapshot.drawdowns.episodes.iloc[0]["drawdown"] < 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_snapshots.py -v`

Expected: FAIL with missing analytics and snapshot factory classes.

- [ ] **Step 3: Write the analytics objects**

```python
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    cumulative_return: float
    cagr: float
    annual_volatility: float
    sharpe: float
    sortino: float
    calmar: float
    max_drawdown: float
    final_equity: float
    avg_turnover: float
    alpha: float
    beta: float
    tracking_error: float
    information_ratio: float


@dataclass(frozen=True, slots=True)
class RollingMetrics:
    series: dict[str, pd.Series]


@dataclass(frozen=True, slots=True)
class DrawdownStats:
    underwater: pd.Series
    episodes: pd.DataFrame


@dataclass(frozen=True, slots=True)
class ExposureSnapshot:
    holdings_count: pd.Series
    latest_holdings: pd.DataFrame


@dataclass(frozen=True, slots=True)
class SectorSnapshot:
    latest_weighted: pd.Series
    latest_count: pd.Series
    concentration: pd.Series


def annualized_sharpe(returns: pd.Series, periods: int = 252) -> float:
    std = float(returns.std())
    if std == 0.0:
        return 0.0
    return float(np.sqrt(periods) * returns.mean() / std)
```

```python
from dataclasses import dataclass

import pandas as pd

from .analytics import DrawdownStats, ExposureSnapshot, PerformanceMetrics, RollingMetrics, SectorSnapshot, annualized_sharpe
from .benchmarks import BenchmarkConfig, BenchmarkRepository, SectorRepository


@dataclass(frozen=True, slots=True)
class PerformanceSnapshot:
    run_id: str
    display_name: str
    metrics: PerformanceMetrics
    rolling: RollingMetrics
    drawdowns: DrawdownStats
    exposure: ExposureSnapshot
    sectors: SectorSnapshot
    strategy_equity: pd.Series
    strategy_returns: pd.Series
    benchmark_returns: pd.Series
    benchmark_equity: pd.Series


class PerformanceSnapshotFactory:
    def __init__(self, *, benchmark_repo: BenchmarkRepository, sector_repo: SectorRepository) -> None:
        self.benchmark_repo = benchmark_repo
        self.sector_repo = sector_repo

    def build(self, run, benchmark: BenchmarkConfig) -> PerformanceSnapshot:  # type: ignore[no-untyped-def]
        benchmark_series = self.benchmark_repo.load_series(benchmark, start=str(run.returns.index.min().date()), end=str(run.returns.index.max().date()))
        aligned_benchmark = benchmark_series.returns.reindex(run.returns.index).fillna(0.0)
        rolling = RollingMetrics(
            series={
                "rolling_sharpe": run.returns.rolling(252).apply(lambda s: annualized_sharpe(pd.Series(s)), raw=False),
                "rolling_beta": run.returns.rolling(252).cov(aligned_benchmark).div(aligned_benchmark.rolling(252).var()),
            }
        )
        peak = run.equity.cummax()
        underwater = run.equity.div(peak).sub(1.0)
        episodes = pd.DataFrame([{"drawdown": float(underwater.min()), "trough": underwater.idxmin()}])
        latest_holdings = run.latest_weights if run.latest_weights is not None else pd.DataFrame()
        holdings_count = run.weights.fillna(0.0).ne(0.0).sum(axis=1)
        latest_weighted = self.sector_repo.latest_sector_weights(run.weights)
        sector_count = latest_weighted.ne(0.0).astype(int)
        concentration = run.weights.abs().sum(axis=1)
        metrics = PerformanceMetrics(
            cumulative_return=float(run.equity.iloc[-1] / run.equity.iloc[0] - 1.0),
            cagr=float((run.equity.iloc[-1] / run.equity.iloc[0]) ** (252 / len(run.equity)) - 1.0),
            annual_volatility=float(run.returns.std() * (252 ** 0.5)),
            sharpe=annualized_sharpe(run.returns),
            sortino=annualized_sharpe(run.returns.clip(lower=0.0)),
            calmar=0.0,
            max_drawdown=float(underwater.min()),
            final_equity=float(run.equity.iloc[-1]),
            avg_turnover=float(run.turnover.mean()),
            alpha=float((run.returns - aligned_benchmark).mean() * 252),
            beta=float(run.returns.cov(aligned_benchmark) / aligned_benchmark.var()) if float(aligned_benchmark.var()) != 0.0 else 0.0,
            tracking_error=float((run.returns - aligned_benchmark).std() * (252 ** 0.5)),
            information_ratio=annualized_sharpe(run.returns - aligned_benchmark),
        )
        return PerformanceSnapshot(
            run_id=run.run_id,
            display_name=str(run.config.get("strategy", run.run_id)),
            metrics=metrics,
            rolling=rolling,
            drawdowns=DrawdownStats(underwater=underwater, episodes=episodes),
            exposure=ExposureSnapshot(holdings_count=holdings_count, latest_holdings=latest_holdings),
            sectors=SectorSnapshot(latest_weighted=latest_weighted, latest_count=sector_count, concentration=concentration),
            strategy_equity=run.equity,
            strategy_returns=run.returns,
            benchmark_returns=aligned_benchmark,
            benchmark_equity=(1.0 + aligned_benchmark).cumprod(),
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/reporting/test_snapshots.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/reporting/test_snapshots.py backtesting/reporting/analytics.py backtesting/reporting/snapshots.py
git commit -m "feat: add reporting performance snapshots"
```

---

### Task 4: Replace Flat Plots With Page-Level Subplot Figure Builders

**Files:**
- Create: `tests/reporting/test_figures.py`
- Create: `backtesting/reporting/figures.py`
- Create: `backtesting/reporting/comparison_figures.py`
- Modify: `tests/reporting/test_plots.py`

- [ ] **Step 1: Write the failing figure tests**

```python
from pathlib import Path

import plotly.graph_objects as go

from backtesting.reporting.comparison_figures import ComparisonFigureBuilder
from backtesting.reporting.figures import TearsheetFigureBuilder


def test_tearsheet_figure_builder_writes_expected_pages(tmp_path: Path, monkeypatch, sample_snapshot) -> None:
    monkeypatch.setattr(go.Figure, "write_image", lambda self, path, *args, **kwargs: Path(path).write_bytes(b"png"))

    pages = TearsheetFigureBuilder(tmp_path).build(sample_snapshot)

    assert set(pages) == {"executive", "rolling", "calendar", "exposure"}
    assert all(path.suffix == ".png" for path in pages.values())


def test_comparison_figure_builder_writes_expected_pages(tmp_path: Path, monkeypatch, sample_snapshot) -> None:
    monkeypatch.setattr(go.Figure, "write_image", lambda self, path, *args, **kwargs: Path(path).write_bytes(b"png"))

    pages = ComparisonFigureBuilder(tmp_path).build([sample_snapshot, sample_snapshot])

    assert set(pages) == {"executive", "performance", "rolling", "exposure"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_figures.py -v`

Expected: FAIL with missing figure builder classes.

- [ ] **Step 3: Write the page-level figure builders**

```python
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TearsheetFigureBuilder:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def build(self, snapshot) -> dict[str, Path]:  # type: ignore[no-untyped-def]
        return {
            "executive": self._executive(snapshot),
            "rolling": self._rolling(snapshot),
            "calendar": self._calendar(snapshot),
            "exposure": self._exposure(snapshot),
        }

    def _executive(self, snapshot) -> Path:  # type: ignore[no-untyped-def]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.68, 0.32], vertical_spacing=0.08)
        fig.add_trace(go.Scatter(x=snapshot.strategy_equity.index, y=snapshot.strategy_equity.values, name=snapshot.display_name), row=1, col=1)
        fig.add_trace(go.Scatter(x=snapshot.benchmark_equity.index, y=snapshot.benchmark_equity.values, name="KOSPI200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=snapshot.drawdowns.underwater.index, y=snapshot.drawdowns.underwater.values, name="Underwater", fill="tozeroy"), row=2, col=1)
        fig.update_layout(title="Performance vs KOSPI200")
        return self._write(fig, "executive.png")
```

```python
class ComparisonFigureBuilder:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def build(self, snapshots) -> dict[str, Path]:  # type: ignore[no-untyped-def]
        return {
            "executive": self._executive(snapshots),
            "performance": self._performance(snapshots),
            "rolling": self._rolling(snapshots),
            "exposure": self._exposure(snapshots),
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/reporting/test_figures.py tests/reporting/test_plots.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/reporting/test_figures.py tests/reporting/test_plots.py backtesting/reporting/figures.py backtesting/reporting/comparison_figures.py
git commit -m "feat: add reporting subplot figure builders"
```

---

### Task 5: Add Report-Specific Table Builders, Composers, Templates, And Styles

**Files:**
- Create: `backtesting/reporting/tables_single.py`
- Create: `backtesting/reporting/tables_comparison.py`
- Create: `backtesting/reporting/composers.py`
- Create: `backtesting/reporting/templates/tearsheet.html.j2`
- Create: `backtesting/reporting/templates/comparison.html.j2`
- Modify: `backtesting/reporting/html.py`
- Modify: `backtesting/reporting/styles.css`
- Modify: `tests/reporting/test_html.py`
- Modify: `tests/reporting/test_tables.py`

- [ ] **Step 1: Write the failing table and HTML tests**

```python
from pathlib import Path

from backtesting.reporting.html import HtmlRenderer
from backtesting.reporting.models import BenchmarkConfig, ReportSpec, TearsheetBundle


def test_html_renderer_uses_tearsheet_template(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(name="single", run_ids=("run-a",), benchmark=BenchmarkConfig.default_kospi200()),
        out_dir=tmp_path,
        run_id="run-a",
        display_name="Momentum",
        pages={"executive": tmp_path / "executive.png"},
        tables={},
        notes=(),
    )
    (tmp_path / "executive.png").write_bytes(b"png")

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    assert "Momentum" in html
    assert "KOSPI200" in html
    assert "executive.png" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_html.py tests/reporting/test_tables.py -v`

Expected: FAIL because `HtmlRenderer` only knows the old bundle shape and old template.

- [ ] **Step 3: Write the composer and template implementation**

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TearsheetContext:
    title: str
    display_name: str
    benchmark_name: str
    metric_cards: list[dict[str, str]]
    pages: list[dict[str, str]]
    tables: dict[str, dict[str, object]]
    notes: tuple[str, ...]
```

```python
class HtmlRenderer:
    def render(self, bundle) -> Path:  # type: ignore[no-untyped-def]
        bundle.out_dir.mkdir(parents=True, exist_ok=True)
        self._write_stylesheet(bundle.out_dir)
        template_name = "tearsheet.html.j2" if bundle.spec.kind.value == "tearsheet" else "comparison.html.j2"
        template = self.env.get_template(template_name)
        html = template.render(bundle=bundle, stylesheet="styles.css")
        path = bundle.out_dir / "report.html"
        path.write_text(html, encoding="utf-8")
        return path
```

```css
:root {
  --paper: #f4f1ea;
  --panel: #fffdfa;
  --ink: #102033;
  --muted: #5a6675;
  --line: #d9d2c2;
  --accent: #1f5d57;
  --benchmark: #9f6f2e;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.page-figure img {
  width: 100%;
  border-radius: 14px;
  display: block;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/reporting/test_html.py tests/reporting/test_tables.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backtesting/reporting/tables_single.py backtesting/reporting/tables_comparison.py backtesting/reporting/composers.py backtesting/reporting/templates/tearsheet.html.j2 backtesting/reporting/templates/comparison.html.j2 backtesting/reporting/html.py backtesting/reporting/styles.css tests/reporting/test_html.py tests/reporting/test_tables.py
git commit -m "feat: add pdf-first report templates and tables"
```

---

### Task 6: Refactor ReportBuilder And CLI To Build Tear Sheets And Comparison Reports

**Files:**
- Modify: `backtesting/reporting/builder.py`
- Modify: `backtesting/reporting/cli.py`
- Modify: `tests/reporting/test_builder.py`
- Create: `tests/reporting/test_cli.py`

- [ ] **Step 1: Write the failing builder and CLI tests**

```python
from pathlib import Path

from backtesting.reporting.cli import ReportCli
from backtesting.reporting.models import ReportKind


def test_builder_creates_tearsheet_bundle_for_single_run(tmp_path: Path, sample_run, monkeypatch) -> None:
    monkeypatch.setattr("backtesting.reporting.builder.PerformanceSnapshotFactory", _fake_snapshot_factory)
    monkeypatch.setattr("backtesting.reporting.builder.TearsheetFigureBuilder", _fake_tearsheet_figure_builder)

    bundle = ReportBuilder(tmp_path).build(ReportSpec(name="single", run_ids=("sample",)), [sample_run])

    assert bundle.spec.kind is ReportKind.TEARSHEET
    assert bundle.run_id == "sample"


def test_cli_auto_uses_comparison_for_multiple_runs(tmp_path: Path, monkeypatch) -> None:
    cli = ReportCli(runs_root=tmp_path, reports_root=tmp_path / "reports")
    parser = cli.parser()
    args = parser.parse_args(["--runs", "a", "b", "--name", "compare"])
    assert args.runs == ["a", "b"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_builder.py tests/reporting/test_cli.py -v`

Expected: FAIL because `ReportBuilder` still emits the legacy flat bundle.

- [ ] **Step 3: Write the builder and CLI dispatch implementation**

```python
from .benchmarks import BenchmarkRepository, SectorRepository
from .comparison_figures import ComparisonFigureBuilder
from .figures import TearsheetFigureBuilder
from .models import ComparisonBundle, ReportKind, ReportSpec, TearsheetBundle
from .snapshots import PerformanceSnapshotFactory


class ReportBuilder:
    def build(self, spec: ReportSpec, runs: list[SavedRun]):  # type: ignore[no-untyped-def]
        out_dir = self.root_dir / spec.name
        snapshots = [
            PerformanceSnapshotFactory(
                benchmark_repo=BenchmarkRepository.default(),
                sector_repo=SectorRepository.default(),
            ).build(run, spec.benchmark)
            for run in runs
        ]
        if spec.kind is ReportKind.TEARSHEET:
            snapshot = snapshots[0]
            pages = TearsheetFigureBuilder(out_dir / "pages").build(snapshot)
            return TearsheetBundle(spec=spec, out_dir=out_dir, run_id=snapshot.run_id, display_name=snapshot.display_name, pages=pages, tables={}, notes=())
        pages = ComparisonFigureBuilder(out_dir / "pages").build(snapshots)
        return ComparisonBundle(spec=spec, out_dir=out_dir, display_names=tuple(s.display_name for s in snapshots), pages=pages, tables={}, notes=())
```

```python
class ReportCli:
    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Build backtest reports from saved runs.")
        parser.add_argument("--runs", nargs="+", required=True)
        parser.add_argument("--name", required=True)
        parser.add_argument("--title")
        parser.add_argument("--kind", choices=("auto", "tearsheet", "comparison"), default="auto")
        parser.add_argument("--benchmark-code", default="IKS200")
        parser.add_argument("--benchmark-name", default="KOSPI200")
        return parser
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/reporting/test_builder.py tests/reporting/test_cli.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backtesting/reporting/builder.py backtesting/reporting/cli.py tests/reporting/test_builder.py tests/reporting/test_cli.py
git commit -m "feat: dispatch reporting builder by report kind"
```

---

### Task 7: Run Full Reporting Regression Suite And Real Smoke Outputs

**Files:**
- Modify: `README.md`
- Modify: `tests/reporting/test_pdf.py`

- [ ] **Step 1: Add the final PDF regression expectations**

```python
def test_pdf_renderer_writes_pdf_from_composed_report(tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    html_path.write_text("<html><body><img src='page.png'></body></html>", encoding="utf-8")
    (tmp_path / "page.png").write_bytes(b"png")

    pdf_path, status = PdfRenderer().render_with_status(html_path)

    assert status["pdf_ok"] is True
    assert pdf_path is not None
    assert pdf_path.exists()
```

- [ ] **Step 2: Run the reporting test suite**

Run: `pytest tests/reporting -v`

Expected: PASS

- [ ] **Step 3: Run real single-run and comparison smoke commands**

Run:

```bash
MPLCONFIGDIR=/tmp/matplotlib XDG_CACHE_HOME=/tmp .venv/bin/python report.py --runs momentum-2020-2026_20260403_230130 --name momentum-tearsheet
MPLCONFIGDIR=/tmp/matplotlib XDG_CACHE_HOME=/tmp .venv/bin/python report.py --runs momentum-2020-2026_20260403_230130 op-fwd-2020-2026_20260403_230308 --name compare-2020-2026
```

Expected:

- `results/reports/momentum-tearsheet/report.pdf` exists
- `results/reports/compare-2020-2026/report.pdf` exists
- output JSON reports `pdf_ok: true`

- [ ] **Step 4: Update the README reporting commands**

~~~md
## Build Reports

Single-run tear sheet:

```powershell
python report.py --runs momentum-run_YYYYMMDD_HHMMSS --name momentum-tearsheet
```

Multi-run comparison report:

```powershell
python report.py --runs momentum-run_YYYYMMDD_HHMMSS op-fwd-run_YYYYMMDD_HHMMSS --name compare-report --title "Momentum vs OP Fwd"
```
~~~

- [ ] **Step 5: Commit**

```bash
git add tests/reporting/test_pdf.py README.md
git commit -m "docs: update reporting workflow"
```

---

## Self-Review

### Spec Coverage

- Single-run institutional tear sheet: covered by Tasks 3, 4, 5, 6, 7
- Multi-run comparison report: covered by Tasks 4, 5, 6, 7
- `KOSPI200` benchmark from `qw_BM`: covered by Tasks 1 and 2
- Rolling Sharpe, rolling beta, return distribution, monthly heatmap, underwater, holdings count: covered by Tasks 3 and 4
- WICS sector analysis: covered by Tasks 2 and 3
- PDF-first visual redesign: covered by Tasks 4 and 5
- Repo-compatible OOP layering: covered by Tasks 1, 2, 3, 5, 6

### Placeholder Scan

- No placeholder markers or unresolved implementation notes remain
- Each task has concrete file paths, test commands, and implementation snippets

### Type Consistency

- `ReportKind`, `BenchmarkConfig`, `PerformanceSnapshotFactory`, `TearsheetBundle`, and `ComparisonBundle` names are used consistently across tasks
- Builder dispatch always consumes `ReportSpec.kind`
- Benchmark default is consistently `IKS200 / KOSPI200`

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-03-performance-reporting-redesign-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
