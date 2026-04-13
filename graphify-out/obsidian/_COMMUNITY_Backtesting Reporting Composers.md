---
type: community
cohesion: 0.08
members: 55
---

# Backtesting Reporting Composers

**Cohesion:** 0.08 - loosely connected
**Members:** 55 nodes

## Members
- [[ComparisonBundle]] - code - backtesting/reporting/models.py
- [[ComparisonComposer]] - code - backtesting/reporting/composers.py
- [[ComparisonComposer.compose()]] - code - backtesting/reporting/composers.py
- [[ComparisonRenderContext]] - code - backtesting/reporting/composers.py
- [[CoverContext]] - code - backtesting/reporting/composers.py
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
- [[ReportBundle]] - code - backtesting/reporting/models.py
- [[ReportSpec]] - code - backtesting/reporting/models.py
- [[SectionContext]] - code - backtesting/reporting/composers.py
- [[TableContext]] - code - backtesting/reporting/composers.py
- [[TearsheetBundle]] - code - backtesting/reporting/models.py
- [[TearsheetComposer]] - code - backtesting/reporting/composers.py
- [[TearsheetComposer.compose()]] - code - backtesting/reporting/composers.py
- [[TearsheetRenderContext]] - code - backtesting/reporting/composers.py
- [[_comparison_metric_strip()]] - code - backtesting/reporting/composers.py
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
- [[test_bundles_expose_display_metadata()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_comparison_bundle_exposes_basic_metadata()]] - code - tests/reporting/test_models_reporting_redesign.py
- [[test_comparison_composer_builds_pdf_first_context()]] - code - tests/reporting/test_html.py
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
- 30 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 25 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 12 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 11 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 9 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 9 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 9 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 5 edges to [[_COMMUNITY_Docs Superpowers Performance]]
- 4 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 4 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 2 edges to [[_COMMUNITY_Tests Dashboard Test_Run]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Live]]

## Top bridge nodes
- [[ReportSpec]] - degree 28, connects to 7 communities
- [[HtmlRenderer]] - degree 21, connects to 7 communities
- [[ComparisonComposer.compose()]] - degree 18, connects to 5 communities
- [[TearsheetComposer.compose()]] - degree 14, connects to 5 communities
- [[test_html_renderer_uses_tearsheet_template()]] - degree 9, connects to 5 communities