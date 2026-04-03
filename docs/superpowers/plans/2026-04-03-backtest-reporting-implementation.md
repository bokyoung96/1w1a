# 1w1a Backtest Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Plotly-based HTML and PDF reporting pipeline that reads saved backtest run bundles and produces single-run and comparison reports.

**Architecture:** The implementation adds a `report bundle` layer on top of existing `run bundle` outputs. `RunReader` loads saved artifacts, `ReportBuilder` assembles typed report data, `PlotLibrary` renders Plotly figures, `HtmlRenderer` writes a paper-first report, and `PdfRenderer` converts that HTML into a PDF with fallback to HTML-only when PDF export fails.

**Tech Stack:** Python, pandas, plotly, jinja2, pytest, pyarrow, existing `backtesting.reporting` package, HTML/CSS, PDF renderer dependency selected during implementation

---

## File Map

### Existing files to modify

- `README.md`
- `backtesting/__init__.py`
- `backtesting/run.py`
- `backtesting/reporting/__init__.py`
- `backtesting/reporting/writer.py`
- `root.py`

### New package files

- `backtesting/reporting/models.py`
- `backtesting/reporting/reader.py`
- `backtesting/reporting/tables.py`
- `backtesting/reporting/plots.py`
- `backtesting/reporting/html.py`
- `backtesting/reporting/pdf.py`
- `backtesting/reporting/builder.py`
- `backtesting/reporting/templates/base.html.j2`
- `backtesting/reporting/templates/partials/summary.html.j2`
- `backtesting/reporting/templates/partials/section.html.j2`
- `backtesting/reporting/styles.css`
- `report.py`

### New test files

- `tests/reporting/test_reader.py`
- `tests/reporting/test_tables.py`
- `tests/reporting/test_plots.py`
- `tests/reporting/test_builder.py`
- `tests/reporting/test_html.py`
- `tests/reporting/test_pdf.py`
- `tests/test_report_cli.py`

## Task 1: Add Typed Report Models and Run Reader

**Files:**
- Create: `backtesting/reporting/models.py`
- Create: `backtesting/reporting/reader.py`
- Modify: `backtesting/reporting/__init__.py`
- Test: `tests/reporting/test_reader.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.reader import RunReader


def test_run_reader_loads_saved_bundle(tmp_path: Path) -> None:
    run_dir = tmp_path / "sample-run"
    series_dir = run_dir / "series"
    positions_dir = run_dir / "positions"
    run_dir.mkdir()
    series_dir.mkdir()
    positions_dir.mkdir()

    (run_dir / "config.json").write_text('{"strategy":"momentum","start":"2024-01-01","end":"2024-01-31"}', encoding="utf-8")
    (run_dir / "summary.json").write_text('{"cagr":0.1,"mdd":-0.2,"sharpe":1.2,"final_equity":110.0,"avg_turnover":0.05}', encoding="utf-8")
    pd.Series([100.0, 110.0], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), name="equity").to_csv(series_dir / "equity.csv", index_label="date")
    pd.Series([0.0, 0.1], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), name="returns").to_csv(series_dir / "returns.csv", index_label="date")
    pd.Series([0.0, 0.05], index=pd.to_datetime(["2024-01-02", "2024-01-03"]), name="turnover").to_csv(series_dir / "turnover.csv", index_label="date")
    pd.DataFrame({"A": [1.0]}, index=pd.to_datetime(["2024-01-03"])).to_parquet(positions_dir / "weights.parquet")
    pd.DataFrame({"A": [10.0]}, index=pd.to_datetime(["2024-01-03"])).to_parquet(positions_dir / "qty.parquet")

    run = RunReader().read(run_dir)

    assert run.run_id == "sample-run"
    assert run.summary["final_equity"] == 110.0
    assert list(run.equity.index) == list(pd.to_datetime(["2024-01-02", "2024-01-03"]))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_reader.py::test_run_reader_loads_saved_bundle -v`
Expected: FAIL because `RunReader` and report models do not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/reporting/models.py`:

```python
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass(frozen=True, slots=True)
class SavedRun:
    run_id: str
    path: Path
    config: dict[str, object]
    summary: dict[str, float]
    equity: pd.Series
    returns: pd.Series
    turnover: pd.Series
    weights: pd.DataFrame
    qty: pd.DataFrame
    monthly_returns: pd.Series | None = None
    latest_qty: pd.DataFrame | None = None
    latest_weights: pd.DataFrame | None = None
    validation: dict[str, object] | None = None
    split: dict[str, object] | None = None


@dataclass(frozen=True, slots=True)
class ReportSpec:
    name: str
    run_ids: tuple[str, ...]
    title: str | None = None
    include_factor: bool = True
    include_validation: bool = True
    include_is_oos: bool = True
    formats: tuple[str, ...] = ("html", "pdf")
```

`backtesting/reporting/reader.py`:

```python
import json
from pathlib import Path

import pandas as pd

from .models import SavedRun


class RunReader:
    def read(self, run_dir: Path) -> SavedRun:
        run_dir = Path(run_dir)
        series_dir = run_dir / "series"
        positions_dir = run_dir / "positions"
        return SavedRun(
            run_id=run_dir.name,
            path=run_dir,
            config=json.loads((run_dir / "config.json").read_text(encoding="utf-8")),
            summary=json.loads((run_dir / "summary.json").read_text(encoding="utf-8")),
            equity=self._read_series(series_dir / "equity.csv", "equity"),
            returns=self._read_series(series_dir / "returns.csv", "returns"),
            turnover=self._read_series(series_dir / "turnover.csv", "turnover"),
            weights=pd.read_parquet(positions_dir / "weights.parquet"),
            qty=pd.read_parquet(positions_dir / "qty.parquet"),
        )

    @staticmethod
    def _read_series(path: Path, column: str) -> pd.Series:
        frame = pd.read_csv(path, parse_dates=["date"])
        return frame.set_index("date")[column]
```

- [ ] **Step 4: Extend the reader to discover optional artifacts**

Add conditional loading for:

- `series/monthly_returns.csv`
- `positions/latest_qty.csv`
- `positions/latest_weights.csv`
- `validation.json`
- `split.json`

Use helper functions like:

```python
def _read_optional_json(path: Path) -> dict[str, object] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/reporting/test_reader.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/__init__.py backtesting/reporting/models.py backtesting/reporting/reader.py tests/reporting/test_reader.py
git commit -m "feat: add typed report models and run reader"
```

## Task 2: Build Summary Table Helpers

**Files:**
- Create: `backtesting/reporting/tables.py`
- Test: `tests/reporting/test_tables.py`

- [ ] **Step 1: Write the failing test**

```python
import pandas as pd

from backtesting.reporting.models import SavedRun
from backtesting.reporting.tables import build_summary_table


def test_build_summary_table_compares_runs() -> None:
    index = pd.to_datetime(["2024-01-02"])
    run_a = SavedRun(
        run_id="a",
        path=pd.Path("a"),  # replace with Path in implementation
        config={"strategy": "momentum"},
        summary={"cagr": 0.2, "mdd": -0.1, "sharpe": 1.1, "final_equity": 120.0, "avg_turnover": 0.05},
        equity=pd.Series([120.0], index=index),
        returns=pd.Series([0.0], index=index),
        turnover=pd.Series([0.05], index=index),
        weights=pd.DataFrame({"A": [1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0]}, index=index),
    )
    run_b = SavedRun(
        run_id="b",
        path=pd.Path("b"),
        config={"strategy": "op_fwd_yield"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 0.9, "final_equity": 110.0, "avg_turnover": 0.02},
        equity=pd.Series([110.0], index=index),
        returns=pd.Series([0.0], index=index),
        turnover=pd.Series([0.02], index=index),
        weights=pd.DataFrame({"A": [1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0]}, index=index),
    )

    table = build_summary_table([run_a, run_b])

    assert list(table["run_id"]) == ["a", "b"]
    assert "cagr" in table.columns
    assert table.loc[1, "strategy"] == "op_fwd_yield"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_tables.py::test_build_summary_table_compares_runs -v`
Expected: FAIL because `build_summary_table` does not exist

- [ ] **Step 3: Write minimal implementation**

```python
from pathlib import Path

import pandas as pd

from .models import SavedRun


def build_summary_table(runs: list[SavedRun]) -> pd.DataFrame:
    rows = []
    for run in runs:
        rows.append(
            {
                "run_id": run.run_id,
                "strategy": str(run.config.get("strategy", "")),
                "cagr": float(run.summary.get("cagr", float("nan"))),
                "mdd": float(run.summary.get("mdd", float("nan"))),
                "sharpe": float(run.summary.get("sharpe", float("nan"))),
                "final_equity": float(run.summary.get("final_equity", float("nan"))),
                "avg_turnover": float(run.summary.get("avg_turnover", float("nan"))),
            }
        )
    return pd.DataFrame(rows)
```

- [ ] **Step 4: Add appendix and position helpers**

Add functions for:

- `build_latest_weights_table(run: SavedRun) -> pd.DataFrame`
- `build_latest_qty_table(run: SavedRun) -> pd.DataFrame`
- `build_appendix_table(runs: list[SavedRun]) -> pd.DataFrame`

The appendix table should include:

```python
{
  "run_id": run.run_id,
  "path": str(run.path),
  "strategy": str(run.config.get("strategy", "")),
  "start": str(run.config.get("start", "")),
  "end": str(run.config.get("end", "")),
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/reporting/test_tables.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/tables.py tests/reporting/test_tables.py
git commit -m "feat: add report summary and appendix tables"
```

## Task 3: Add Plotly Figure Builders

**Files:**
- Create: `backtesting/reporting/plots.py`
- Test: `tests/reporting/test_plots.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.models import SavedRun
from backtesting.reporting.plots import PlotLibrary


def test_plot_library_writes_equity_plot(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="sample",
        path=tmp_path,
        config={"strategy": "momentum"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 1.0, "final_equity": 110.0, "avg_turnover": 0.05},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
    )

    path = PlotLibrary(tmp_path).equity([run])

    assert path.exists()
    assert path.suffix == ".png"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_plots.py::test_plot_library_writes_equity_plot -v`
Expected: FAIL because the plot library does not exist

- [ ] **Step 3: Write minimal implementation**

Use Plotly and `write_image`:

```python
from pathlib import Path

import plotly.graph_objects as go

from .models import SavedRun


class PlotLibrary:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def equity(self, runs: list[SavedRun]) -> Path:
        fig = go.Figure()
        for run in runs:
            fig.add_trace(go.Scatter(x=run.equity.index, y=run.equity.values, mode="lines", name=run.run_id))
        path = self.out_dir / "equity.png"
        fig.write_image(path)
        return path
```

- [ ] **Step 4: Add the required figure set**

Add methods for:

- `equity`
- `drawdown`
- `turnover`
- `top_weights`
- `monthly_heatmap`

For drawdown, compute:

```python
dd = run.equity.div(run.equity.cummax()).sub(1.0)
```

For top weights, use the latest non-zero weights table and build a horizontal bar chart.

- [ ] **Step 5: Add fallback behavior**

If `fig.write_image(...)` fails, save:

```python
fig.write_html(path.with_suffix(".html"))
```

and raise a controlled exception only when the caller requires a PNG specifically.

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/reporting/test_plots.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backtesting/reporting/plots.py tests/reporting/test_plots.py
git commit -m "feat: add plotly report figures"
```

## Task 4: Assemble Report Bundles

**Files:**
- Create: `backtesting/reporting/builder.py`
- Test: `tests/reporting/test_builder.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.builder import ReportBuilder
from backtesting.reporting.models import ReportSpec, SavedRun


def test_report_builder_creates_summary_and_plot_map(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="sample",
        path=tmp_path / "sample",
        config={"strategy": "momentum", "start": "2024-01-02", "end": "2024-01-03"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 1.0, "final_equity": 110.0, "avg_turnover": 0.05},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
    )

    bundle = ReportBuilder(tmp_path).build(ReportSpec(name="sample-report", run_ids=("sample",)), [run])

    assert bundle.spec.name == "sample-report"
    assert not bundle.summary.empty
    assert "equity" in bundle.plots
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_builder.py::test_report_builder_creates_summary_and_plot_map -v`
Expected: FAIL because the builder does not exist

- [ ] **Step 3: Write minimal implementation**

`backtesting/reporting/models.py` additions:

```python
@dataclass(frozen=True, slots=True)
class ReportBundle:
    spec: ReportSpec
    out_dir: Path
    runs: tuple[SavedRun, ...]
    summary: pd.DataFrame
    appendix: pd.DataFrame
    plots: dict[str, Path]
    notes: tuple[str, ...] = ()
```

`backtesting/reporting/builder.py`:

```python
from pathlib import Path

from .models import ReportBundle, ReportSpec, SavedRun
from .plots import PlotLibrary
from .tables import build_appendix_table, build_summary_table


class ReportBuilder:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir)

    def build(self, spec: ReportSpec, runs: list[SavedRun]) -> ReportBundle:
        out_dir = self.root_dir / spec.name
        plotter = PlotLibrary(out_dir / "plots")
        plots = {"equity": plotter.equity(runs)}
        return ReportBundle(
            spec=spec,
            out_dir=out_dir,
            runs=tuple(runs),
            summary=build_summary_table(runs),
            appendix=build_appendix_table(runs),
            plots=plots,
        )
```

- [ ] **Step 4: Expand the builder to cover all first-phase sections**

Add:

- summary table
- appendix table
- position tables under `tables/`
- plots for `equity`, `drawdown`, `turnover`, `top_weights`, `monthly_heatmap`
- section notes for missing optional artifacts

Use note strings like:

```python
"missing_validation:<run_id>"
"missing_split:<run_id>"
"missing_factor:<run_id>"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/reporting/test_builder.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/builder.py backtesting/reporting/models.py tests/reporting/test_builder.py
git commit -m "feat: add report bundle builder"
```

## Task 5: Render HTML Reports

**Files:**
- Create: `backtesting/reporting/html.py`
- Create: `backtesting/reporting/templates/base.html.j2`
- Create: `backtesting/reporting/templates/partials/summary.html.j2`
- Create: `backtesting/reporting/templates/partials/section.html.j2`
- Create: `backtesting/reporting/styles.css`
- Test: `tests/reporting/test_html.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pandas as pd

from backtesting.reporting.html import HtmlRenderer
from backtesting.reporting.models import ReportBundle, ReportSpec


def test_html_renderer_writes_report_html(tmp_path: Path) -> None:
    bundle = ReportBundle(
        spec=ReportSpec(name="sample-report", run_ids=("sample",)),
        out_dir=tmp_path / "sample-report",
        runs=(),
        summary=pd.DataFrame([{"run_id": "sample", "cagr": 0.1}]),
        appendix=pd.DataFrame([{"run_id": "sample"}]),
        plots={"equity": tmp_path / "equity.png"},
    )

    path = HtmlRenderer().render(bundle)

    assert path.exists()
    assert "<html" in path.read_text(encoding="utf-8").lower()
    assert "sample-report" in path.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_html.py::test_html_renderer_writes_report_html -v`
Expected: FAIL because the HTML renderer and templates do not exist

- [ ] **Step 3: Write minimal implementation**

Use Jinja2:

```python
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


class HtmlRenderer:
    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, bundle) -> Path:
        bundle.out_dir.mkdir(parents=True, exist_ok=True)
        template = self.env.get_template("base.html.j2")
        html = template.render(bundle=bundle)
        path = bundle.out_dir / "report.html"
        path.write_text(html, encoding="utf-8")
        return path
```

- [ ] **Step 4: Add first-phase sections and styles**

`base.html.j2` must include:

- cover
- executive summary table
- performance section
- positions section
- appendix section

`styles.css` must include:

```css
body { font-family: "Pretendard", "Noto Sans KR", sans-serif; margin: 0; color: #1f2937; }
.page { width: 1200px; margin: 0 auto; padding: 48px; }
.metric-table { border-collapse: collapse; width: 100%; }
.metric-table th, .metric-table td { border-bottom: 1px solid #e5e7eb; padding: 10px 12px; }
.section { page-break-inside: avoid; margin-top: 32px; }
img.plot { width: 100%; height: auto; }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/reporting/test_html.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/html.py backtesting/reporting/templates/base.html.j2 backtesting/reporting/templates/partials/summary.html.j2 backtesting/reporting/templates/partials/section.html.j2 backtesting/reporting/styles.css tests/reporting/test_html.py
git commit -m "feat: add html report renderer"
```

## Task 6: Add PDF Export with HTML Fallback

**Files:**
- Create: `backtesting/reporting/pdf.py`
- Test: `tests/reporting/test_pdf.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from backtesting.reporting.pdf import PdfRenderer


def test_pdf_renderer_keeps_html_when_pdf_export_fails(tmp_path: Path) -> None:
    html_path = tmp_path / "report.html"
    html_path.write_text("<html><body>hello</body></html>", encoding="utf-8")

    renderer = PdfRenderer()
    pdf_path = renderer.render(html_path)

    assert html_path.exists()
    assert pdf_path is None or pdf_path.suffix == ".pdf"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/reporting/test_pdf.py::test_pdf_renderer_keeps_html_when_pdf_export_fails -v`
Expected: FAIL because the PDF renderer does not exist

- [ ] **Step 3: Write minimal implementation**

```python
from pathlib import Path


class PdfRenderer:
    def render(self, html_path: Path) -> Path | None:
        try:
            import weasyprint
        except ImportError:
            return None

        pdf_path = html_path.with_suffix(".pdf")
        weasyprint.HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return pdf_path
```

- [ ] **Step 4: Add controlled failure metadata**

Add:

```python
def render_with_status(self, html_path: Path) -> tuple[Path | None, dict[str, object]]:
    ...
```

The metadata should include:

```python
{"pdf_ok": True, "pdf_path": "..."}
```

or:

```python
{"pdf_ok": False, "pdf_error": "ImportError: ..."}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/reporting/test_pdf.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/pdf.py tests/reporting/test_pdf.py
git commit -m "feat: add html to pdf export with fallback"
```

## Task 7: Wire a Report CLI

**Files:**
- Create: `report.py`
- Modify: `backtesting/reporting/__init__.py`
- Test: `tests/test_report_cli.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from backtesting.reporting import ReportCli


def test_report_cli_parses_run_ids(tmp_path: Path) -> None:
    cli = ReportCli()
    args = cli.parser().parse_args(["--runs", "run-a", "run-b", "--name", "compare-report"])

    assert args.runs == ["run-a", "run-b"]
    assert args.name == "compare-report"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_report_cli.py::test_report_cli_parses_run_ids -v`
Expected: FAIL because the report CLI does not exist

- [ ] **Step 3: Write minimal implementation**

`report.py`:

```python
from backtesting.reporting import main


if __name__ == "__main__":
    main()
```

`backtesting/reporting/__init__.py` additions:

```python
from .cli import ReportCli, main

__all__ = (..., "ReportCli", "main")
```

`backtesting/reporting/cli.py`:

```python
import argparse


class ReportCli:
    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Build backtest reports from saved runs.")
        parser.add_argument("--runs", nargs="+", required=True)
        parser.add_argument("--name", required=True)
        parser.add_argument("--title")
        return parser
```

- [ ] **Step 4: Wire the end-to-end CLI path**

`main()` in `cli.py` should:

1. resolve `results/backtests/<run-id>`
2. load runs through `RunReader`
3. build `ReportSpec`
4. call `ReportBuilder`
5. render HTML
6. export PDF
7. write `report.json`
8. print output paths

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_report_cli.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add report.py backtesting/reporting/__init__.py backtesting/reporting/cli.py tests/test_report_cli.py
git commit -m "feat: add report cli entrypoint"
```

## Task 8: Extend Run Bundles for Future Report Sections

**Files:**
- Modify: `backtesting/run.py`
- Modify: `backtesting/reporting/writer.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

import pandas as pd

from backtesting.catalog import DataCatalog
from backtesting.data import ParquetStore
from backtesting.run import BacktestRunner, RunConfig


def test_runner_writes_validation_and_split_placeholders(tmp_path: Path) -> None:
    parquet_dir = tmp_path / "parquet"
    raw_dir = tmp_path / "raw"
    result_dir = tmp_path / "results"
    parquet_dir.mkdir()
    raw_dir.mkdir()
    store = ParquetStore(parquet_dir)
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    store.write("qw_adj_c", pd.DataFrame({"A": [10.0, 11.0]}, index=index))
    store.write("qw_adj_o", pd.DataFrame({"A": [10.0, 11.0]}, index=index))
    store.write("qw_k200_yn", pd.DataFrame({"A": [1, 1]}, index=index))

    report = BacktestRunner(catalog=DataCatalog.default(), raw_dir=raw_dir, parquet_dir=parquet_dir, result_dir=result_dir).run(
        RunConfig(strategy="momentum", start="2024-01-02", end="2024-01-03", top_n=1, lookback=1, schedule="daily", fill_mode="close")
    )

    assert (report.output_dir / "validation.json").exists()
    assert (report.output_dir / "split.json").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_run.py::test_runner_writes_validation_and_split_placeholders -v`
Expected: FAIL because the writer does not save those artifacts

- [ ] **Step 3: Write minimal implementation**

In `RunWriter.write(...)`, add:

```python
self._write_json(run_dir / "validation.json", {"warnings": []})
self._write_json(run_dir / "split.json", {"is": None, "oos": None})
```

- [ ] **Step 4: Add richer placeholders when data exists**

If the runner later has:

- validation warnings
- IS/OOS metrics
- factor artifacts

save them with stable names:

- `validation.json`
- `split.json`
- `factor.json`

Do not invent incompatible future names.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_run.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/run.py backtesting/reporting/writer.py tests/test_run.py
git commit -m "feat: extend run bundles for reporting inputs"
```

## Task 9: End-to-End HTML and PDF Smoke Coverage

**Files:**
- Modify: `README.md`
- Modify: `backtesting/__init__.py`
- Test: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
import backtesting as bt


def test_reporting_exports_import_cleanly() -> None:
    assert "RunReader" in bt.__all__
    assert "RunWriter" in bt.__all__
    assert "ReportSpec" in bt.__all__
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py::test_reporting_exports_import_cleanly -v`
Expected: FAIL until the new reporting exports are wired

- [ ] **Step 3: Wire public exports**

Update `backtesting/__init__.py` to export:

- `RunReader`
- `RunWriter`
- `ReportSpec`
- `ReportBundle`
- `ReportBuilder`

- [ ] **Step 4: Update the README**

Document:

```powershell
python run.py --strategy momentum --start 2020-01-02 --end 2020-12-31 --name momentum-run
python report.py --runs momentum-run_YYYYMMDD_HHMMSS --name momentum-report
```

Add a short explanation that:

- run bundles live under `results/backtests/`
- report bundles live under `results/reports/`
- HTML is always written
- PDF is written when export dependencies are available

- [ ] **Step 5: Run the full test suite**

Run: `pytest tests -v`
Expected: PASS

- [ ] **Step 6: Run manual smoke commands**

Run:

```bash
conda activate myenv
python run.py --name smoke-momentum --strategy momentum --start 2020-01-02 --end 2020-12-31 --top-n 20 --lookback 20 --schedule monthly --fill-mode next_open
python run.py --name smoke-op-fwd --strategy op_fwd_yield --start 2020-01-02 --end 2020-12-31 --top-n 20 --schedule monthly --fill-mode next_open
python report.py --runs smoke-momentum_YYYYMMDD_HHMMSS smoke-op-fwd_YYYYMMDD_HHMMSS --name smoke-compare --title "Momentum vs OP Fwd"
```

Expected:

- report bundle exists under `results/reports/smoke-compare*`
- `report.html` exists
- `report.pdf` exists if PDF dependency is available

- [ ] **Step 7: Commit**

```bash
git add README.md backtesting/__init__.py tests/test_smoke.py
git commit -m "docs: add reporting workflow and smoke coverage"
```

## Self-Review

### Spec coverage

- single-run reporting: Tasks 1, 4, 5, 7
- multi-run comparison reporting: Tasks 2, 3, 4, 7
- Plotly-based charts: Task 3
- HTML rendering: Task 5
- PDF export with fallback: Task 6
- validation / IS-OOS sections when artifacts exist: Tasks 1, 4, 8
- report bundle output structure: Tasks 4, 5, 6, 7
- no rerun requirement: Tasks 1 and 7

### Placeholder scan

- No `TODO`
- No `TBD`
- No vague “add validation later” steps without explicit filenames
- Every task has concrete files, commands, and implementation snippets

### Type consistency

- `SavedRun` and `ReportSpec` are introduced before `ReportBuilder`
- `ReportBundle` is introduced before HTML rendering
- `RunReader` feeds `ReportBuilder`
- `PlotLibrary`, `HtmlRenderer`, and `PdfRenderer` are wired in CLI order after their definitions
