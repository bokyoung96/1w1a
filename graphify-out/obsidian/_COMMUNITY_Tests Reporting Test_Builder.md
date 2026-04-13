---
type: community
cohesion: 0.06
members: 70
---

# Tests Reporting Test_Builder

**Cohesion:** 0.06 - loosely connected
**Members:** 70 nodes

## Members
- [[DataLoader.__init__()]] - code - backtesting/data/loader.py
- [[LongOnlyTopN.build()]] - code - backtesting/construction/long_only.py
- [[PlotExportError]] - code - backtesting/reporting/plots.py
- [[PlotExportError.__init__()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary]] - code - backtesting/reporting/plots.py
- [[PlotLibrary.__init__()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary._line_trace()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary._monthly_heatmap_trace()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary._monthly_returns()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary._vertical_spacing()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary._write_png()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary.drawdown()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary.equity()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary.monthly_heatmap()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary.top_weights()]] - code - backtesting/reporting/plots.py
- [[PlotLibrary.turnover()]] - code - backtesting/reporting/plots.py
- [[ReportBuilder]] - code - backtesting/reporting/builder.py
- [[ReportBuilder.__init__()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder._build_comparison_bundle()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder._build_notes()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder._build_snapshots()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder._build_tearsheet_bundle()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder._write_legacy_table()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder._write_tables()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder.build()]] - code - backtesting/reporting/builder.py
- [[ReportBuilder.build_legacy()]] - code - backtesting/reporting/builder.py
- [[SavedRun]] - code - backtesting/reporting/models.py
- [[_FakeComparisonFigureBuilder]] - code - tests/reporting/test_builder.py
- [[_FakeComparisonFigureBuilder.__init__()]] - code - tests/reporting/test_builder.py
- [[_FakeComparisonFigureBuilder.build()]] - code - tests/reporting/test_builder.py
- [[_FakeComparisonTableBuilder]] - code - tests/reporting/test_builder.py
- [[_FakeComparisonTableBuilder.build()]] - code - tests/reporting/test_builder.py
- [[_FakeFactory]] - code - tests/reporting/test_builder.py
- [[_FakeFactory.__init__()]] - code - tests/reporting/test_builder.py
- [[_FakeFactory.build()]] - code - tests/reporting/test_builder.py
- [[_FakeTearsheetFigureBuilder]] - code - tests/reporting/test_builder.py
- [[_FakeTearsheetFigureBuilder.__init__()]] - code - tests/reporting/test_builder.py
- [[_FakeTearsheetFigureBuilder.build()]] - code - tests/reporting/test_builder.py
- [[_FakeTearsheetTableBuilder]] - code - tests/reporting/test_builder.py
- [[_FakeTearsheetTableBuilder.build()]] - code - tests/reporting/test_builder.py
- [[_build_latest_table()]] - code - backtesting/reporting/tables.py
- [[_coerce_metric()]] - code - backtesting/reporting/tables.py
- [[_fake_resolver()]] - code - tests/reporting/test_builder.py
- [[_make_plotter()]] - code - tests/reporting/test_builder.py
- [[_plot()]] - code - tests/reporting/test_builder.py
- [[_sample_run()]] - code - tests/reporting/test_builder.py
- [[_sample_run()_1]] - code - tests/reporting/test_plots.py
- [[_sample_run_named()]] - code - tests/reporting/test_plots.py
- [[_write_image_success()_1]] - code - tests/reporting/test_plots.py
- [[build_appendix_table()]] - code - backtesting/reporting/tables.py
- [[build_latest_qty_table()]] - code - backtesting/reporting/tables.py
- [[build_latest_weights_table()]] - code - backtesting/reporting/tables.py
- [[build_summary_table()]] - code - backtesting/reporting/tables.py
- [[capture_write_image()]] - code - tests/reporting/test_plots.py
- [[fail_write_image()]] - code - tests/reporting/test_plots.py
- [[plots.py]] - code - backtesting/reporting/plots.py
- [[tables.py]] - code - backtesting/reporting/tables.py
- [[test_builder.py]] - code - tests/reporting/test_builder.py
- [[test_plot_library_preserves_flat_plot_contract()]] - code - tests/reporting/test_plots.py
- [[test_plot_library_strict_png_mode_raises_controlled_exception()]] - code - tests/reporting/test_plots.py
- [[test_plot_library_supports_many_run_monthly_heatmap()]] - code - tests/reporting/test_plots.py
- [[test_plot_library_supports_multi_run_equity_chart()]] - code - tests/reporting/test_plots.py
- [[test_plot_library_writes_all_expected_plots()]] - code - tests/reporting/test_plots.py
- [[test_plot_library_writes_equity_plot()]] - code - tests/reporting/test_plots.py
- [[test_plot_library_writes_html_fallback_when_image_export_fails()]] - code - tests/reporting/test_plots.py
- [[test_plots.py]] - code - tests/reporting/test_plots.py
- [[test_report_builder_creates_comparison_bundle_for_multiple_runs()]] - code - tests/reporting/test_builder.py
- [[test_report_builder_creates_tearsheet_bundle_and_persists_tables()]] - code - tests/reporting/test_builder.py
- [[test_report_builder_legacy_path_remains_available()]] - code - tests/reporting/test_builder.py
- [[test_report_builder_uses_universe_specific_repositories()]] - code - tests/reporting/test_builder.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tests_Reporting_Test_Builder
SORT file.name ASC
```

## Connections to other communities
- 45 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 36 edges to [[_COMMUNITY_Backtesting Reporting Frontend]]
- 28 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 11 edges to [[_COMMUNITY_Tests Reporting Analytics]]
- 10 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 8 edges to [[_COMMUNITY_Backtesting Strategies Tests]]
- 4 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 4 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Strategy]]
- 1 edge to [[_COMMUNITY_Tests Test Run.Py Engine]]

## Top bridge nodes
- [[PlotLibrary.turnover()]] - degree 19, connects to 6 communities
- [[PlotLibrary.equity()]] - degree 16, connects to 6 communities
- [[LongOnlyTopN.build()]] - degree 26, connects to 5 communities
- [[PlotLibrary.drawdown()]] - degree 25, connects to 4 communities
- [[SavedRun]] - degree 14, connects to 4 communities