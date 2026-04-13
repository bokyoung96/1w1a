---
type: community
cohesion: 0.07
members: 64
---

# Backtesting Reporting Composers

**Cohesion:** 0.07 - loosely connected
**Members:** 64 nodes

## Members
- [[BenchmarkConfig.default_kospi200()]] - code - backtesting/reporting/models.py
- [[ComparisonBundle]] - code - backtesting/reporting/models.py
- [[ComparisonComposer]] - code - backtesting/reporting/composers.py
- [[ComparisonComposer.compose()]] - code - backtesting/reporting/composers.py
- [[ComparisonRenderContext]] - code - backtesting/reporting/composers.py
- [[CoverContext]] - code - backtesting/reporting/composers.py
- [[DashboardPayloadService.__init__()]] - code - dashboard/backend/services/dashboard_payload.py
- [[HtmlRenderer]] - code - backtesting/reporting/html.py
- [[HtmlRenderer.__init__()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._plot_context()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._render_comparison()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._render_legacy()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._render_tearsheet()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._run_context()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._table()]] - code - backtesting/reporting/html.py
- [[HtmlRenderer._write_stylesheet()]] - code - backtesting/reporting/html.py
- [[MetricStripItem]] - code - backtesting/reporting/composers.py
- [[PageContext]] - code - backtesting/reporting/composers.py
- [[ReportCli.__init__()]] - code - backtesting/reporting/cli.py
- [[ReportSpec]] - code - backtesting/reporting/models.py
- [[RunReader]] - code - backtesting/reporting/reader.py
- [[RunReader._read_optional_frame()]] - code - backtesting/reporting/reader.py
- [[RunReader._read_optional_parquet()]] - code - backtesting/reporting/reader.py
- [[RunReader._read_optional_series()]] - code - backtesting/reporting/reader.py
- [[SectionContext]] - code - backtesting/reporting/composers.py
- [[TableContext]] - code - backtesting/reporting/composers.py
- [[TearsheetBundle]] - code - backtesting/reporting/models.py
- [[TearsheetComposer]] - code - backtesting/reporting/composers.py
- [[TearsheetComposer.compose()]] - code - backtesting/reporting/composers.py
- [[TearsheetRenderContext]] - code - backtesting/reporting/composers.py
- [[_comparison_metric_strip()]] - code - backtesting/reporting/composers.py
- [[_default_benchmark()]] - code - backtesting/reporting/snapshots.py
- [[_format_metric_value()]] - code - backtesting/reporting/composers.py
- [[_format_table_cell()]] - code - backtesting/reporting/composers.py
- [[_format_value()]] - code - backtesting/reporting/composers.py
- [[_is_internal_column()]] - code - backtesting/reporting/composers.py
- [[_metric_cards_from_strip()]] - code - backtesting/reporting/composers.py
- [[_metric_strip()]] - code - backtesting/reporting/composers.py
- [[_page_contexts()]] - code - backtesting/reporting/composers.py
- [[_split_comparison_sections()]] - code - backtesting/reporting/composers.py
- [[_split_tearsheet_sections()]] - code - backtesting/reporting/composers.py
- [[_table_contexts()]] - code - backtesting/reporting/composers.py
- [[_write_asset()]] - code - tests/reporting/test_html.py
- [[composers.py]] - code - backtesting/reporting/composers.py
- [[html.py]] - code - backtesting/reporting/html.py
- [[test_bundles_expose_display_metadata()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_comparison_bundle_exposes_basic_metadata()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_comparison_composer_builds_pdf_first_context()]] - code - tests/reporting/test_html.py
- [[test_html.py]] - code - tests/reporting/test_html.py
- [[test_html_renderer_keeps_composed_report_asset_paths_relative()]] - code - tests/reporting/test_html.py
- [[test_html_renderer_keeps_legacy_reportbundle_path_styled()]] - code - tests/reporting/test_html.py
- [[test_html_renderer_supports_html_page_asset_fallback_for_new_templates()]] - code - tests/reporting/test_html.py
- [[test_html_renderer_uses_comparison_template()]] - code - tests/reporting/test_html.py
- [[test_html_renderer_uses_tearsheet_template()]] - code - tests/reporting/test_html.py
- [[test_models_reporting_redesign.py]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_defaults_to_comparison_for_multiple_runs()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_defaults_to_tearsheet_for_single_run()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_normalizes_string_kind_to_enum()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_positional_arguments_remain_backward_compatible()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_rejects_comparison_with_one_run()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_rejects_empty_run_ids()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_rejects_invalid_kind_values()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_report_spec_rejects_tearsheet_with_multiple_runs()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_tearsheet_composer_builds_pdf_first_context()]] - code - tests/reporting/test_html.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Backtesting_Reporting_Composers
SORT file.name ASC
```

## Connections to other communities
- 39 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 23 edges to [[_COMMUNITY_Backtesting Reporting Frontend]]
- 14 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 13 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 10 edges to [[_COMMUNITY_Tests Reporting Analytics]]
- 10 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 10 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 8 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 6 edges to [[_COMMUNITY_Docs Superpowers Performance]]
- 3 edges to [[_COMMUNITY_Dashboard Frontend App]]
- 3 edges to [[_COMMUNITY_Docs Superpowers Backtest]]
- 3 edges to [[_COMMUNITY_Docs Superpowers Kosdaq150]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Live]]
- 2 edges to [[_COMMUNITY_Dashboard Backend Schemas]]
- 1 edge to [[_COMMUNITY_Tests Reporting Test_Pdf]]
- 1 edge to [[_COMMUNITY_Tests Test Run.Py Engine]]

## Top bridge nodes
- [[ReportSpec]] - degree 28, connects to 7 communities
- [[BenchmarkConfig.default_kospi200()]] - degree 23, connects to 7 communities
- [[HtmlRenderer]] - degree 21, connects to 5 communities
- [[ComparisonComposer.compose()]] - degree 18, connects to 5 communities
- [[RunReader]] - degree 15, connects to 5 communities