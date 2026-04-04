# Performance Reporting PDF Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the reporting presentation layer so tear sheet and comparison outputs render as PDF-first institutional documents with a spacious cover page, a dense executive spread starting on page 2, and tighter, more legible tables.

**Architecture:** Keep the current `ReportBuilder -> Composer -> HtmlRenderer -> PdfRenderer` pipeline and current analytics assets, but reshape the presentation layer in three places: richer composer contexts, restructured Jinja templates, and a tighter print-first CSS system. Tests should lock in the new cover/executive hierarchy and compact table behavior before changing templates and styles.

**Tech Stack:** Python 3.11, pandas, jinja2, WeasyPrint, pytest, CSS

---

## File Structure

- Modify: `backtesting/reporting/composers.py`
  - Replace the flat `metric_cards/pages/tables` view model with explicit cover metadata, KPI strip items, prioritized executive tables, and interior sections.
- Modify: `backtesting/reporting/templates/tearsheet.html.j2`
  - Split the document into a spacious cover page plus a dense executive spread and interior sections.
- Modify: `backtesting/reporting/templates/comparison.html.j2`
  - Mirror the new system for multi-run comparison, promoting ranked and benchmark-relative content earlier.
- Modify: `backtesting/reporting/styles.css`
  - Replace the oversized hero/card system with compact print-first typography, denser tables, stronger page-break behavior, and lighter chrome.
- Modify: `tests/reporting/test_html.py`
  - Lock in the new template structure, text hierarchy, and fallback behavior.
- Modify: `tests/reporting/test_pdf.py`
  - Keep PDF export coverage and add one smoke assertion that the HTML emitted by the new structure still exports.

---

### Task 1: Add A PDF-First Render Context In The Composer

**Files:**
- Modify: `backtesting/reporting/composers.py:20-260`
- Modify: `tests/reporting/test_html.py:18-173`

- [ ] **Step 1: Write the failing tear sheet and comparison HTML context assertions**

```python
def test_html_renderer_uses_tearsheet_template(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(
            name="single-report",
            run_ids=("run-a",),
            title="Momentum Tearsheet",
            benchmark=BenchmarkConfig.default_kospi200(),
        ),
        out_dir=tmp_path / "single-report",
        run_id="run-a",
        display_name="Momentum",
        pages={
            "executive": _write_asset(tmp_path / "single-report" / "pages" / "executive.png"),
            "rolling": _write_asset(tmp_path / "single-report" / "pages" / "rolling.png"),
            "calendar": _write_asset(tmp_path / "single-report" / "pages" / "calendar.png"),
            "exposure": _write_asset(tmp_path / "single-report" / "pages" / "exposure.png"),
        },
        tables={
            "performance_summary": pd.DataFrame(
                [
                    {"metric_key": "cagr", "metric": "CAGR", "value": 0.172},
                    {"metric_key": "sharpe", "metric": "Sharpe", "value": 1.1},
                    {"metric_key": "max_drawdown", "metric": "Max Drawdown", "value": -0.221},
                    {"metric_key": "tracking_error", "metric": "Tracking Error", "value": 0.081},
                    {"metric_key": "final_equity", "metric": "Final Equity", "value": 1234567.0},
                ]
            ),
            "drawdown_episodes": pd.DataFrame([{"start": "2022-01-01", "drawdown": -0.123}]),
            "top_holdings": pd.DataFrame([{"symbol": "AAA", "weight": 0.25}]),
            "sector_weights": pd.DataFrame([{"sector": "Tech", "weight": 0.40}]),
            "validation_appendix": pd.DataFrame([{"note": "missing_factor:run-a"}]),
        },
        notes=("missing_factor:run-a",),
    )

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    assert 'class="report-cover"' in html
    assert 'class="executive-spread"' in html
    assert "Executive Summary" in html
    assert "Performance Summary" in html
    assert "Worst Drawdowns" in html
    assert "Rolling Diagnostics" in html
    assert "Holdings And Sectors" in html
    assert "PDF-First Layout" not in html
    assert "Metric Cards" not in html


def test_html_renderer_uses_comparison_template(tmp_path: Path) -> None:
    bundle = ComparisonBundle(
        spec=ReportSpec(
            name="compare-report",
            run_ids=("run-a", "run-b"),
            title="Strategy Comparison",
            benchmark=BenchmarkConfig.default_kospi200(),
        ),
        out_dir=tmp_path / "compare-report",
        display_names=("Momentum", "OP Fwd Yield"),
        pages={
            "executive": _write_asset(tmp_path / "compare-report" / "pages" / "executive.png"),
            "performance": _write_asset(tmp_path / "compare-report" / "pages" / "performance.png"),
            "rolling": _write_asset(tmp_path / "compare-report" / "pages" / "rolling.png"),
            "exposure": _write_asset(tmp_path / "compare-report" / "pages" / "exposure.png"),
        },
        tables={
            "ranked_summary": pd.DataFrame(
                [
                    {"display_name": "Momentum", "cagr": 0.172, "sharpe": 1.10, "max_drawdown": -0.21, "final_equity": 1234567.0},
                    {"display_name": "OP Fwd Yield", "cagr": 0.150, "sharpe": 1.35, "max_drawdown": -0.18, "final_equity": 1500000.0},
                ]
            ),
            "benchmark_relative": pd.DataFrame([{"display_name": "Momentum", "alpha": 0.032, "beta": 0.88}]),
            "exposure_summary": pd.DataFrame([{"display_name": "Momentum", "holdings_count": 20, "avg_turnover": 0.12}]),
            "sector_summary": pd.DataFrame([{"display_name": "Momentum", "top_sector": "Tech", "top_sector_weight": 0.31}]),
        },
        notes=("missing_split:run-b",),
    )

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    assert 'class="report-cover"' in html
    assert 'class="executive-spread"' in html
    assert "Ranked Summary" in html
    assert "Benchmark Relative Metrics" in html
    assert "Performance Comparison" in html
    assert "Top CAGR" not in html
    assert "Metric Cards" not in html
```

- [ ] **Step 2: Run the HTML tests to verify they fail**

Run: `pytest tests/reporting/test_html.py -v`
Expected: FAIL because the current templates still render `.hero`, `Metric Cards`, and the old flat `report.pages` / `report.tables` structure.

- [ ] **Step 3: Add explicit cover, executive, and interior section contexts in the composer**

```python
@dataclass(frozen=True, slots=True)
class CoverContext:
    report_type: str
    title: str
    subtitle: str
    benchmark_name: str
    report_name: str
    descriptor: str


@dataclass(frozen=True, slots=True)
class MetricStripItem:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class SectionContext:
    title: str
    pages: tuple[PageContext, ...]
    tables: tuple[TableContext, ...]


@dataclass(frozen=True, slots=True)
class TearsheetRenderContext:
    cover: CoverContext
    executive_metrics: tuple[MetricStripItem, ...]
    executive_pages: tuple[PageContext, ...]
    executive_tables: tuple[TableContext, ...]
    sections: tuple[SectionContext, ...]
    notes: tuple[str, ...]


def _split_tearsheet_sections(
    pages: tuple[PageContext, ...],
    tables: tuple[TableContext, ...],
) -> tuple[tuple[PageContext, ...], tuple[TableContext, ...], tuple[SectionContext, ...]]:
    executive_pages = tuple(page for page in pages if page.key == "executive")
    executive_tables = tuple(
        table for table in tables if table.key in {"performance_summary", "drawdown_episodes"}
    )
    sections = (
        SectionContext(
            title="Rolling Diagnostics",
            pages=tuple(page for page in pages if page.key == "rolling"),
            tables=(),
        ),
        SectionContext(
            title="Return Shape",
            pages=tuple(page for page in pages if page.key == "calendar"),
            tables=(),
        ),
        SectionContext(
            title="Holdings And Sectors",
            pages=tuple(page for page in pages if page.key == "exposure"),
            tables=tuple(table for table in tables if table.key in {"top_holdings", "sector_weights"}),
        ),
        SectionContext(
            title="Appendix",
            pages=(),
            tables=tuple(table for table in tables if table.key in {"validation_appendix"}),
        ),
    )
    return executive_pages, executive_tables, tuple(
        section for section in sections if section.pages or section.tables
    )


class TearsheetComposer:
    def compose(self, bundle: TearsheetBundle) -> TearsheetRenderContext:
        pages = _page_contexts(bundle.pages, bundle.out_dir)
        tables = _table_contexts(bundle.tables)
        executive_pages, executive_tables, sections = _split_tearsheet_sections(pages, tables)
        return TearsheetRenderContext(
            cover=CoverContext(
                report_type="Single-Run Tearsheet",
                title=bundle.spec.title or bundle.display_name,
                subtitle=bundle.display_name,
                benchmark_name=bundle.spec.benchmark.name,
                report_name=bundle.spec.name,
                descriptor="Compact research report for print-first review",
            ),
            executive_metrics=_metric_strip(bundle.tables.get("performance_summary", pd.DataFrame())),
            executive_pages=executive_pages,
            executive_tables=executive_tables,
            sections=sections,
            notes=bundle.notes,
        )
```

- [ ] **Step 4: Update comparison composition to promote ranked and benchmark-relative content into the executive spread**

```python
class ComparisonComposer:
    def compose(self, bundle: ComparisonBundle) -> ComparisonRenderContext:
        pages = _page_contexts(bundle.pages, bundle.out_dir)
        tables = _table_contexts(bundle.tables)
        executive_pages = tuple(page for page in pages if page.key in {"executive", "performance"})
        executive_tables = tuple(
            table for table in tables if table.key in {"ranked_summary", "benchmark_relative"}
        )
        sections = (
            SectionContext(
                title="Rolling And Relative Diagnostics",
                pages=tuple(page for page in pages if page.key == "rolling"),
                tables=(),
            ),
            SectionContext(
                title="Holdings And Sector Comparison",
                pages=tuple(page for page in pages if page.key == "exposure"),
                tables=tuple(table for table in tables if table.key in {"exposure_summary", "sector_summary"}),
            ),
        )
        return ComparisonRenderContext(
            cover=CoverContext(
                report_type="Comparison Report",
                title=bundle.spec.title or bundle.spec.name,
                subtitle=", ".join(bundle.display_names),
                benchmark_name=bundle.spec.benchmark.name,
                report_name=bundle.spec.name,
                descriptor="Cross-strategy comparison optimized for A4 PDF review",
            ),
            executive_metrics=(),
            executive_pages=executive_pages,
            executive_tables=executive_tables,
            sections=tuple(section for section in sections if section.pages or section.tables),
            notes=bundle.notes,
        )
```

- [ ] **Step 5: Run the HTML tests to verify the context-driven structure passes**

Run: `pytest tests/reporting/test_html.py -v`
Expected: PASS, with new assertions finding `.report-cover`, `.executive-spread`, and the promoted executive section labels.

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/composers.py tests/reporting/test_html.py
git commit -m "refactor: add pdf-first reporting contexts"
```

---

### Task 2: Rebuild The Tearsheet Template Around Cover And Executive Spread

**Files:**
- Modify: `backtesting/reporting/templates/tearsheet.html.j2:1-104`
- Modify: `tests/reporting/test_html.py:18-173`

- [ ] **Step 1: Write a failing tear sheet structure test for cover and executive ordering**

```python
def test_html_renderer_uses_tearsheet_template(tmp_path: Path) -> None:
    ...
    html = path.read_text(encoding="utf-8")
    assert html.index("class=\"report-cover\"") < html.index("class=\"executive-spread\"")
    assert "Document Scope" not in html
    assert "PDF-First Layout" not in html
    assert "Open interactive chart" not in html
    assert "Executive Summary" in html
    assert "Appendix" in html
```

- [ ] **Step 2: Run the tear sheet HTML test to verify it fails**

Run: `pytest tests/reporting/test_html.py::test_html_renderer_uses_tearsheet_template -v`
Expected: FAIL because the template still renders the current hero and figure-grid layout.

- [ ] **Step 3: Replace the tear sheet template with cover, KPI strip, executive grid, and interior sections**

```html
<main class="report-shell report-shell--tearsheet">
  <section class="report-cover">
    <p class="report-cover-kicker">{{ report.cover.report_type }}</p>
    <h1>{{ report.cover.title }}</h1>
    <p class="report-cover-subtitle">{{ report.cover.subtitle }}</p>
    <dl class="report-cover-meta">
      <div><dt>Benchmark</dt><dd>{{ report.cover.benchmark_name }}</dd></div>
      <div><dt>Report</dt><dd>{{ report.cover.report_name }}</dd></div>
    </dl>
    <p class="report-cover-descriptor">{{ report.cover.descriptor }}</p>
  </section>

  <section class="report-section executive-spread">
    <header class="section-header">
      <p class="eyebrow">Executive</p>
      <h2>Executive Summary</h2>
    </header>

    <div class="metric-strip">
      {% for item in report.executive_metrics %}
        <article class="metric-strip-item">
          <p class="metric-strip-label">{{ item.label }}</p>
          <p class="metric-strip-value">{{ item.value }}</p>
        </article>
      {% endfor %}
    </div>

    <div class="executive-layout">
      <div class="executive-visuals">
        {% for page in report.executive_pages %}
          <figure class="page-figure page-figure--primary">
            <figcaption>{{ page.title }}</figcaption>
            <img src="{{ page.path }}" alt="{{ page.title }}">
          </figure>
        {% endfor %}
      </div>
      <div class="executive-tables">
        {% for table in report.executive_tables %}
          {% include "partials/compact-table.html.j2" %}
        {% endfor %}
      </div>
    </div>
  </section>

  {% for section in report.sections %}
    <section class="report-section">
      <header class="section-header">
        <h2>{{ section.title }}</h2>
      </header>
      {% if section.pages %}
        <div class="figure-grid">
          {% for page in section.pages %}
            <figure class="page-figure">
              <figcaption>{{ page.title }}</figcaption>
              <img src="{{ page.path }}" alt="{{ page.title }}">
            </figure>
          {% endfor %}
        </div>
      {% endif %}
      {% for table in section.tables %}
        {% include "partials/compact-table.html.j2" %}
      {% endfor %}
    </section>
  {% endfor %}
</main>
```

- [ ] **Step 4: Add a compact shared table partial used by the new tear sheet structure**

```html
<section class="table-panel">
  <header class="table-panel-header">
    <h3>{{ table.title }}</h3>
  </header>
  <div class="table-wrap">
    <table class="metric-table">
      <thead>
        <tr>
          {% for column in table.columns %}
            <th>{{ column.replace("_", " ").title() }}</th>
          {% endfor %}
        </tr>
      </thead>
      <tbody>
        {% for row in table.rows %}
          <tr>
            {% for column in table.columns %}
              <td>{{ row[column] }}</td>
            {% endfor %}
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</section>
```

- [ ] **Step 5: Run the tear sheet HTML test to verify it passes**

Run: `pytest tests/reporting/test_html.py::test_html_renderer_uses_tearsheet_template -v`
Expected: PASS, with the new cover and executive spread appearing in the emitted HTML.

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/templates/tearsheet.html.j2 backtesting/reporting/templates/partials/compact-table.html.j2 tests/reporting/test_html.py
git commit -m "feat: rebuild tearsheet as pdf-first document"
```

---

### Task 3: Rebuild The Comparison Template With A Dense Executive Spread

**Files:**
- Modify: `backtesting/reporting/templates/comparison.html.j2:1-107`
- Modify: `tests/reporting/test_html.py:68-110`

- [ ] **Step 1: Write a failing comparison structure test**

```python
def test_html_renderer_uses_comparison_template(tmp_path: Path) -> None:
    ...
    html = path.read_text(encoding="utf-8")
    assert html.index("class=\"report-cover\"") < html.index("class=\"executive-spread\"")
    assert "Participants" not in html
    assert "Research-Style Comparison" not in html
    assert "Ranked Summary" in html
    assert "Benchmark Relative Metrics" in html
    assert "Holdings And Sector Comparison" in html
```

- [ ] **Step 2: Run the comparison HTML test to verify it fails**

Run: `pytest tests/reporting/test_html.py::test_html_renderer_uses_comparison_template -v`
Expected: FAIL because the template still uses the current hero/participant list and metric card blocks.

- [ ] **Step 3: Replace the comparison template with the same document system used by the tear sheet**

```html
<main class="report-shell report-shell--comparison">
  <section class="report-cover">
    <p class="report-cover-kicker">{{ report.cover.report_type }}</p>
    <h1>{{ report.cover.title }}</h1>
    <p class="report-cover-subtitle">{{ report.cover.subtitle }}</p>
    <dl class="report-cover-meta">
      <div><dt>Benchmark</dt><dd>{{ report.cover.benchmark_name }}</dd></div>
      <div><dt>Report</dt><dd>{{ report.cover.report_name }}</dd></div>
    </dl>
    <p class="report-cover-descriptor">{{ report.cover.descriptor }}</p>
  </section>

  <section class="report-section executive-spread">
    <header class="section-header">
      <p class="eyebrow">Executive</p>
      <h2>Executive Summary</h2>
    </header>

    <div class="executive-layout executive-layout--comparison">
      <div class="executive-visuals">
        {% for page in report.executive_pages %}
          <figure class="page-figure {{ 'page-figure--primary' if loop.first else '' }}">
            <figcaption>{{ page.title }}</figcaption>
            <img src="{{ page.path }}" alt="{{ page.title }}">
          </figure>
        {% endfor %}
      </div>
      <div class="executive-tables">
        {% for table in report.executive_tables %}
          {% include "partials/compact-table.html.j2" %}
        {% endfor %}
      </div>
    </div>
  </section>

  {% for section in report.sections %}
    <section class="report-section">
      <header class="section-header">
        <h2>{{ section.title }}</h2>
      </header>
      {% if section.pages %}
        <div class="figure-grid">
          {% for page in section.pages %}
            <figure class="page-figure">
              <figcaption>{{ page.title }}</figcaption>
              <img src="{{ page.path }}" alt="{{ page.title }}">
            </figure>
          {% endfor %}
        </div>
      {% endif %}
      {% for table in section.tables %}
        {% include "partials/compact-table.html.j2" %}
      {% endfor %}
    </section>
  {% endfor %}
</main>
```

- [ ] **Step 4: Keep HTML asset fallback behavior covered after the template rewrite**

```python
def test_html_renderer_supports_html_page_asset_fallback_for_new_templates(tmp_path: Path) -> None:
    ...
    html = path.read_text(encoding="utf-8")
    assert '<iframe class="plot-frame"' in html
    assert "pages/executive.html" in html
```

```html
{% if page.kind == "html" %}
  <iframe class="plot-frame" src="{{ page.path }}" title="{{ page.title }}"></iframe>
{% else %}
  <img src="{{ page.path }}" alt="{{ page.title }}">
{% endif %}
```

- [ ] **Step 5: Run the full HTML test module to verify both templates pass**

Run: `pytest tests/reporting/test_html.py -v`
Expected: PASS, including the fallback iframe case.

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/templates/comparison.html.j2 tests/reporting/test_html.py
git commit -m "feat: rebuild comparison report layout"
```

---

### Task 4: Replace The Oversized Card Styling With Compact Print-First CSS

**Files:**
- Modify: `backtesting/reporting/styles.css:1-260`
- Modify: `tests/reporting/test_html.py:113-173`
- Modify: `tests/reporting/test_pdf.py:9-75`

- [ ] **Step 1: Write failing style and PDF smoke assertions**

```python
def test_html_renderer_keeps_legacy_reportbundle_path_styled(tmp_path: Path) -> None:
    ...
    css = path.parent.joinpath("styles.css").read_text(encoding="utf-8")
    assert ".report-cover" in css
    assert ".executive-spread" in css
    assert ".metric-strip" in css
    assert ".table-panel" in css
    assert ".metric-cards" not in css


def test_pdf_renderer_writes_pdf_from_composed_report(monkeypatch, tmp_path: Path) -> None:
    ...
    html_path.write_text(
        "<html><body><section class='report-cover'></section><section class='executive-spread'></section></body></html>",
        encoding="utf-8",
    )
    ...
    assert status["pdf_ok"] is True
```

- [ ] **Step 2: Run the HTML and PDF tests to verify they fail**

Run: `pytest tests/reporting/test_html.py::test_html_renderer_keeps_legacy_reportbundle_path_styled tests/reporting/test_pdf.py::test_pdf_renderer_writes_pdf_from_composed_report -v`
Expected: FAIL because the stylesheet still contains `.metric-cards` and does not define the new document classes.

- [ ] **Step 3: Rewrite the stylesheet around cover, executive spread, compact tables, and print-safe density**

```css
@page {
  size: A4;
  margin: 12mm 13mm;
}

:root {
  --ink: #152031;
  --muted: #5c6776;
  --line: #d7d9dd;
  --paper: #f4f1ea;
  --panel: #fffdf9;
  --panel-alt: #f6f2ea;
  --accent: #2f5b52;
}

body {
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: "Pretendard", "Noto Sans KR", sans-serif;
  font-size: 13px;
  line-height: 1.42;
}

.report-shell {
  width: 1120px;
  max-width: calc(100% - 72px);
  margin: 0 auto;
  padding: 28px 36px 52px;
}

.report-cover,
.report-section,
.table-panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: none;
  break-inside: avoid;
  page-break-inside: avoid;
}

.report-cover {
  min-height: 240mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 26mm 22mm;
}

.report-cover h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.08;
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 14px;
}

.metric-strip-item {
  padding: 9px 10px;
  border: 1px solid var(--line);
  background: #fff;
}

.metric-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.metric-table th,
.metric-table td {
  padding: 6px 8px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}

.metric-table th {
  text-align: left;
  font-size: 10.5px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted);
  background: var(--panel-alt);
}

.metric-table td:is(:last-child),
.metric-table th:is(:last-child) {
  text-align: right;
}
```

- [ ] **Step 4: Add responsive adjustments that preserve the same hierarchy on web without reintroducing oversized cards**

```css
@media screen and (max-width: 960px) {
  .report-shell {
    max-width: calc(100% - 32px);
    padding: 16px 0 32px;
  }

  .metric-strip,
  .executive-layout,
  .figure-grid {
    grid-template-columns: 1fr;
  }

  .report-cover {
    min-height: auto;
    padding: 32px 22px;
  }

  .table-wrap {
    overflow-x: auto;
  }
}
```

- [ ] **Step 5: Run targeted tests to verify the stylesheet and PDF export still pass**

Run: `pytest tests/reporting/test_html.py tests/reporting/test_pdf.py -v`
Expected: PASS, with CSS assertions finding `.report-cover`, `.executive-spread`, `.metric-strip`, and `.table-panel`.

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/styles.css tests/reporting/test_html.py tests/reporting/test_pdf.py
git commit -m "style: tighten reporting layout for pdf readability"
```

---

### Task 5: Verify Real Report Output And Preserve HTML/PDF Rendering

**Files:**
- Modify: `backtesting/reporting/html.py`
- Modify: `backtesting/reporting/pdf.py`
- Modify: `tests/reporting/test_html.py`
- Modify: `tests/reporting/test_pdf.py`

- [ ] **Step 1: Add one regression test that the renderer still writes `styles.css` once and keeps relative asset paths intact**

```python
def test_html_renderer_uses_relative_paths_for_composed_assets(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(name="relative-report", run_ids=("run-a",), title="Relative Tearsheet"),
        out_dir=tmp_path / "relative-report",
        run_id="run-a",
        display_name="Momentum",
        pages={"executive": _write_asset(tmp_path / "relative-report" / "pages" / "executive.png")},
        tables={"performance_summary": pd.DataFrame([{"metric_key": "cagr", "metric": "CAGR", "value": 0.172}])},
        notes=(),
    )

    html_path = HtmlRenderer().render(bundle)
    html = html_path.read_text(encoding="utf-8")
    assert "pages/executive.png" in html
    assert "styles.css" in html
```

- [ ] **Step 2: Run the targeted regression test to verify current behavior or expose needed renderer changes**

Run: `pytest tests/reporting/test_html.py::test_html_renderer_uses_relative_paths_for_composed_assets -v`
Expected: PASS, or FAIL only if the template rewrite accidentally hardcoded absolute paths.

- [ ] **Step 3: Apply only minimal renderer changes if tests reveal a path or PDF issue**

```python
class HtmlRenderer:
    def _render_tearsheet(self, bundle: TearsheetBundle) -> Path:
        bundle.out_dir.mkdir(parents=True, exist_ok=True)
        self._write_stylesheet(bundle.out_dir)
        template = self.env.get_template("tearsheet.html.j2")
        html = template.render(
            report=TearsheetComposer().compose(bundle),
            stylesheet="styles.css",
        )
        path = bundle.out_dir / "report.html"
        path.write_text(html, encoding="utf-8")
        return path
```

- [ ] **Step 4: Generate real reports and verify the PDF-first hierarchy manually**

Run: `python report.py --runs momentum-2020-2026 --name momentum-tearsheet-pdf-polish`
Expected: writes `results/reports/momentum-tearsheet-pdf-polish/report.html` and, when WeasyPrint is available, `report.pdf`

Run: `python report.py --runs momentum-2020-2026 op-fwd-2020-2026 --name compare-2020-2026-pdf-polish --title "Momentum vs OP Fwd 2020-2026"`
Expected: writes `results/reports/compare-2020-2026-pdf-polish/report.html` and, when WeasyPrint is available, `report.pdf`

- [ ] **Step 5: Run full reporting tests**

Run: `pytest tests/reporting/test_html.py tests/reporting/test_pdf.py tests/reporting/test_builder.py tests/reporting/test_cli.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backtesting/reporting/html.py backtesting/reporting/pdf.py tests/reporting/test_html.py tests/reporting/test_pdf.py
git commit -m "test: verify polished reports render end to end"
```

---

## Self-Review

### Spec Coverage

- PDF-first priority is covered by Tasks 1-5 through explicit cover/executive structure, print-first CSS, and PDF regression checks.
- Hybrid Compact Research direction is covered by Tasks 1-4 through the new context model, compact KPI strip, and reduced chrome.
- Spacious cover page is covered by Tasks 2-4.
- Dense executive spread on page 2 is covered by Tasks 1-3.
- Institutional table density is covered by Tasks 1, 2, and 4.
- Shared but PDF-led web behavior is covered by Tasks 4 and 5.

### Placeholder Scan

- No `TODO`, `TBD`, or “implement later” placeholders remain.
- Every task includes file paths, concrete tests, concrete commands, and concrete code snippets.

### Type Consistency

- `CoverContext`, `MetricStripItem`, `SectionContext`, `TearsheetRenderContext`, and `ComparisonRenderContext` are used consistently across composer and template tasks.
- `executive_metrics`, `executive_pages`, `executive_tables`, and `sections` are the names used throughout the plan.
