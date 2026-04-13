# Backtesting Reporting Tests

> 84 nodes · cohesion 0.05

## Key Concepts

- **LongOnlyTopN.build()** (26 connections) — `backtesting/construction/long_only.py`
- **RunWriter.write()** (24 connections) — `backtesting/reporting/writer.py`
- **PlotLibrary** (23 connections) — `backtesting/reporting/plots.py`
- **ReportBuilder** (19 connections) — `backtesting/reporting/builder.py`
- **test_plots.py** (19 connections) — `tests/reporting/test_plots.py`
- **PlotLibrary.turnover()** (19 connections) — `backtesting/reporting/plots.py`
- **ReportBuilder.build_legacy()** (15 connections) — `backtesting/reporting/builder.py`
- **RunWriter** (14 connections) — `backtesting/reporting/writer.py`
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
- **test_run_reader_round_trips_writer_bundle_layout()** (7 connections) — `tests/reporting/test_reader.py`
- **ReportBuilder._build_snapshots()** (6 connections) — `backtesting/reporting/builder.py`
- **ComparisonFigureBuilder.build()** (6 connections) — `backtesting/reporting/comparison_figures.py`
- **ComparisonFigureBuilder._build_rolling()** (6 connections) — `backtesting/reporting/comparison_figures.py`
- *... and 59 more nodes in this community*

## Relationships

- [[Docs Superpowers Plans]] (39 shared connections)
- [[Raw Ksdq Csv]] (36 shared connections)
- [[Docs Superpowers Reporting]] (25 shared connections)
- [[Backtesting Reporting Tests]] (19 shared connections)
- [[Docs Superpowers Policy]] (9 shared connections)
- [[Backtesting Reporting Composers]] (9 shared connections)
- [[Tests Test Run.Py Engine]] (6 shared connections)
- [[Tests Dashboard Backend]] (6 shared connections)
- [[Docs Superpowers Performance]] (4 shared connections)
- [[Docs Superpowers Strategy]] (3 shared connections)
- [[Backtesting Reporting Tables_Single]] (2 shared connections)
- [[Tests Dashboard Test_Run]] (1 shared connections)

## Source Files

- `backtesting/construction/long_only.py`
- `backtesting/data/loader.py`
- `backtesting/reporting/builder.py`
- `backtesting/reporting/comparison_figures.py`
- `backtesting/reporting/figures.py`
- `backtesting/reporting/plots.py`
- `backtesting/reporting/tables.py`
- `backtesting/reporting/writer.py`
- `tests/reporting/test_builder.py`
- `tests/reporting/test_figures.py`
- `tests/reporting/test_plots.py`
- `tests/reporting/test_reader.py`

## Audit Trail

- EXTRACTED: 149 (31%)
- INFERRED: 334 (69%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*