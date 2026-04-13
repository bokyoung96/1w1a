# Backtesting Reporting Tests

> 79 nodes · cohesion 0.05

## Key Concepts

- **LongOnlyTopN.build()** (26 connections) — `backtesting/construction/long_only.py`
- **PlotLibrary** (23 connections) — `backtesting/reporting/plots.py`
- **ReportBuilder** (19 connections) — `backtesting/reporting/builder.py`
- **test_plots.py** (19 connections) — `tests/reporting/test_plots.py`
- **PlotLibrary.turnover()** (19 connections) — `backtesting/reporting/plots.py`
- **ReportBuilder.build_legacy()** (15 connections) — `backtesting/reporting/builder.py`
- **ComparisonFigureBuilder** (12 connections) — `backtesting/reporting/comparison_figures.py`
- **TearsheetFigureBuilder** (12 connections) — `backtesting/reporting/figures.py`
- **PlotLibrary.monthly_heatmap()** (12 connections) — `backtesting/reporting/plots.py`
- **_sample_run()** (10 connections) — `tests/reporting/test_builder.py`
- **tables.py** (9 connections) — `backtesting/reporting/tables.py`
- **test_plot_library_preserves_flat_plot_contract()** (8 connections) — `tests/reporting/test_plots.py`
- **ReportBuilder._build_comparison_bundle()** (7 connections) — `backtesting/reporting/builder.py`
- **ReportBuilder._build_tearsheet_bundle()** (7 connections) — `backtesting/reporting/builder.py`
- **ComparisonFigureBuilder._build_exposure()** (7 connections) — `backtesting/reporting/comparison_figures.py`
- **PlotLibrary.top_weights()** (7 connections) — `backtesting/reporting/plots.py`
- **PlotLibrary._write_png()** (7 connections) — `backtesting/reporting/plots.py`
- **_sample_run_named()** (7 connections) — `tests/reporting/test_plots.py`
- **test_plot_library_writes_all_expected_plots()** (7 connections) — `tests/reporting/test_plots.py`
- **ReportBundle** (6 connections) — `backtesting/reporting/models.py`
- **ReportBuilder._build_snapshots()** (6 connections) — `backtesting/reporting/builder.py`
- **ComparisonFigureBuilder.build()** (6 connections) — `backtesting/reporting/comparison_figures.py`
- **ComparisonFigureBuilder._build_rolling()** (6 connections) — `backtesting/reporting/comparison_figures.py`
- **TearsheetFigureBuilder.build()** (6 connections) — `backtesting/reporting/figures.py`
- **build_latest_weights_table()** (6 connections) — `backtesting/reporting/tables.py`
- *... and 54 more nodes in this community*

## Relationships

- [[Backtesting Reporting Frontend]] (42 shared connections)
- [[Docs Superpowers Reporting]] (26 shared connections)
- [[Tests Reporting Analytics]] (14 shared connections)
- [[Docs Superpowers Plans]] (12 shared connections)
- [[Backtesting Reporting Composers]] (10 shared connections)
- [[Docs Superpowers Policy]] (8 shared connections)
- [[Tests Dashboard Backend]] (7 shared connections)
- [[Docs Superpowers Backtest]] (4 shared connections)
- [[Docs Superpowers Kosdaq150]] (4 shared connections)
- [[Docs Superpowers Performance]] (3 shared connections)
- [[Tests Test Run.Py Engine]] (3 shared connections)
- [[Raw Ksdq Csv]] (2 shared connections)

## Source Files

- `backtesting/construction/long_only.py`
- `backtesting/data/loader.py`
- `backtesting/reporting/builder.py`
- `backtesting/reporting/comparison_figures.py`
- `backtesting/reporting/figures.py`
- `backtesting/reporting/models.py`
- `backtesting/reporting/plots.py`
- `backtesting/reporting/tables.py`
- `backtesting/strategies/composable.py`
- `tests/reporting/test_builder.py`
- `tests/reporting/test_plots.py`

## Audit Trail

- EXTRACTED: 139 (32%)
- INFERRED: 296 (68%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*