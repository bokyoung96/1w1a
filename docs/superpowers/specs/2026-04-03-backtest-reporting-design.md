# 1w1a Backtest Reporting Design

## Goal

Build a reporting layer for `1w1a` that turns saved backtest runs into polished HTML and PDF reports.

The system should support:

- single-strategy reports
- multi-strategy comparison reports
- position and holding summaries
- benchmark-aware performance plots
- factor sections for factor-style strategies
- validation and IS/OOS sections

The primary reading format is PDF, but HTML remains the source format for layout and rendering.

## Why This Layer Exists

The current stack already produces `run bundle` outputs under `results/backtests/<run-id>/`.

That is useful for storage and debugging, but it is not yet a real research report. The missing layer is a `report bundle` that:

- reads one or more saved run bundles
- builds a coherent narrative
- renders modern charts
- saves a shareable PDF

This keeps execution and reporting separate.

## Scope

### In scope

- report generation from saved run bundles
- Plotly-based charts
- HTML report rendering
- PDF export from HTML
- single-run report mode
- multi-run comparison report mode
- summary tables, performance charts, position tables, and appendix blocks
- validation and IS/OOS sections when artifacts exist
- factor sections when the required factor inputs exist

### Out of scope for phase 1

- interactive web dashboards
- live-updating reports
- browser-hosted exploration tools
- full notebook integration
- fully dynamic pagination rules for arbitrarily large appendices

## Reference Patterns

The design should borrow ideas from these sources:

- `QuantStats` for tearsheet-style metric blocks and HTML reporting
  - https://github.com/ranaroussi/quantstats
- `vectorbt` for portfolio and comparison plotting patterns
  - https://github.com/polakowo/vectorbt
- `vectorbt-backtesting-skills` for research-report structure and robustness sections
  - https://github.com/marketcalls/vectorbt-backtesting-skills

The implementation should not copy these structures directly. The goal is to adapt good patterns to the existing `1w1a` bundle model.

## Design Principles

- Keep reporting separate from execution.
- Treat HTML as the source report format and PDF as a final export.
- Use Plotly for primary chart generation.
- Keep objects small and explicit.
- Support comparison reports from existing saved runs instead of rerunning strategies.
- Save all intermediate artifacts so a report can be regenerated or debugged.
- Degrade gracefully: if PDF export fails, the HTML report must still be saved.

## Output Model

### Run bundle

Existing structure remains:

```text
results/backtests/<run-id>/
```

This continues to store execution outputs such as:

- config
- summary
- equity / returns / turnover series
- holdings and weights
- basic plots

### Report bundle

New structure:

```text
results/reports/<report-id>/
  report.json
  report.html
  report.pdf
  plots/
  tables/
  assets/
```

`report.html` is the canonical rendered report. `report.pdf` is generated from it.

## Report Modes

### Single-run report

Reads one run bundle and produces:

- strategy overview
- performance summary
- benchmark section if benchmark data exists
- positions section
- validation section if available
- factor section if available

### Comparison report

Reads two or more run bundles and produces:

- side-by-side summary table
- overlaid equity comparison
- overlaid drawdown comparison
- turnover comparison
- monthly return comparison
- latest weights / holdings comparison
- appendix with each run's config

The comparison report is a first-class mode, not a patched extension.

## Package Layout

Recommended additions:

```text
backtesting/
  reporting/
    __init__.py
    writer.py
    reader.py
    plots.py
    tables.py
    models.py
    html.py
    pdf.py
    builder.py
    templates/
```

## Core Objects

### `RunReader`

Loads a saved run bundle into a typed object.

Responsibilities:

- read config and summary json
- load series csv files
- load weights / qty parquet
- discover optional artifacts

### `ReportSpec`

A `dataclass` describing a report request:

- `name`
- `run_ids`
- `benchmark_mode`
- `include_factor`
- `include_validation`
- `include_is_oos`
- `formats`
- `title`

### `ReportBundle`

A typed assembled model for rendering:

- report metadata
- run metadata
- summary tables
- plot paths
- table paths
- appendix metadata

### `ReportBuilder`

Transforms one or more loaded runs into a report bundle.

Responsibilities:

- align time series
- compute comparison tables
- generate plot inputs
- decide which sections are included

### `PlotLibrary`

Generates Plotly figures for:

- equity curve
- excess return curve
- drawdown curve
- turnover curve
- monthly return heatmap
- top weights / holdings
- factor quantile and IC plots when available

### `HtmlRenderer`

Renders the report bundle with HTML templates.

### `PdfRenderer`

Converts rendered HTML to PDF.

This layer should be isolated so the HTML rendering path still works even if PDF export dependencies fail.

## Report Sections

### Cover

- report title
- generation timestamp
- included run names
- date range
- strategy count

### Executive Summary

Comparison table including:

- CAGR
- MDD
- Sharpe
- final equity
- average turnover

### Performance

- cumulative equity chart
- benchmark-relative or excess equity chart
- drawdown chart
- monthly returns table or heatmap

### Trading / Risk

- turnover time series
- rolling risk metric block
- holdings count over time if available

### Positions

- latest holdings table
- latest target weights table
- top weights bar chart

### Factor Section

Only included when factor artifacts exist.

- quantile returns
- IC or rank IC
- long-short spread summary

### Validation

Only included when validation artifacts exist.

- warnings summary
- lag coverage block
- stale gap warnings
- sparse signal warnings

### IS / OOS

Only included when split artifacts exist.

- IS/OOS summary table
- equity comparison by split
- stability delta block

### Appendix

- config dump
- dataset list
- source run bundle paths
- artifact inventory

## Plotting Approach

Plotly is the primary plotting backend.

Reasons:

- better visual quality for comparison charts
- cleaner multi-strategy overlays
- more modern styling for static export
- better fit for HTML-first reports

The system should generate static images or HTML-embedded charts depending on the section. PDF output must preserve the intended appearance.

If Plotly export fails, the report generation should still keep:

- `report.html`
- raw tables
- metadata json

## HTML and PDF Pipeline

Recommended flow:

1. Load one or more run bundles.
2. Build a report bundle.
3. Generate Plotly figures and save assets.
4. Render `report.html` from a template.
5. Convert HTML to `report.pdf`.

The HTML template should be styled for paper-first reading:

- predictable page width
- readable typography
- compact metric tables
- page-break-safe sections
- chart sizing that works in PDF

## CLI Shape

Two workflows should exist:

### Existing

```powershell
python run.py ...
```

This produces a run bundle.

### New

```powershell
python report.py --runs <run-id-1> <run-id-2>
```

or equivalent subcommand wiring through the main runner.

This produces a report bundle and PDF.

The report command should never rerun strategies by default. It operates on saved bundles.

## Data Dependencies

Phase 1 report generation should depend only on saved bundle outputs.

That means a report can be rebuilt without re-accessing:

- `raw/`
- `parquet/`
- KIS code

If a section needs missing information that was not saved in the run bundle, the bundle format should be extended rather than reaching back into execution code at report time.

## Failure Handling

The reporting pipeline should fail in a controlled order.

### If a section is unavailable

- omit the section
- add a note to report metadata

### If PDF conversion fails

- keep `report.html`
- keep all plots and tables
- write failure details into `report.json`

### If one run bundle is malformed in a comparison report

- stop with a clear error before rendering

## Testing Strategy

The reporting layer should be tested at three levels.

### Unit tests

- load run bundle fixtures
- build summary tables
- build report bundle objects
- verify section inclusion rules

### Integration tests

- generate a single-run report
- generate a comparison report
- verify expected files exist

### Smoke tests

- run `run.py` to create one or two bundles
- generate HTML and PDF
- verify PDF path exists

## Success Criteria

- A saved run bundle can be turned into a polished HTML report.
- The same report can be exported to PDF.
- Two or more run bundles can be turned into a comparison report.
- Reports include positions and holdings sections.
- Plot quality is strong enough for PDF-first reading.
- Validation and IS/OOS sections appear when relevant artifacts exist.
- The system works without rerunning the original backtest.
