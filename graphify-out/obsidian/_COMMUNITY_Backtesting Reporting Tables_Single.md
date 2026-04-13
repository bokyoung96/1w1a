---
type: community
cohesion: 0.20
members: 19
---

# Backtesting Reporting Tables_Single

**Cohesion:** 0.20 - loosely connected
**Members:** 19 nodes

## Members
- [[ComparisonTableBuilder]] - code - backtesting/reporting/tables_comparison.py
- [[ComparisonTableBuilder.build()]] - code - backtesting/reporting/tables_comparison.py
- [[TearsheetTableBuilder]] - code - backtesting/reporting/tables_single.py
- [[TearsheetTableBuilder.build()]] - code - backtesting/reporting/tables_single.py
- [[_metric_label()]] - code - backtesting/reporting/tables_single.py
- [[_metric_order()]] - code - backtesting/reporting/tables_single.py
- [[_ordered_columns()]] - code - backtesting/reporting/tables_comparison.py
- [[_ordered_columns()_1]] - code - backtesting/reporting/tables_single.py
- [[build_benchmark_relative_table()]] - code - backtesting/reporting/tables_comparison.py
- [[build_drawdown_episodes_table()]] - code - backtesting/reporting/tables_single.py
- [[build_holdings_turnover_table()]] - code - backtesting/reporting/tables_comparison.py
- [[build_performance_summary_table()]] - code - backtesting/reporting/tables_single.py
- [[build_ranked_summary_table()]] - code - backtesting/reporting/tables_comparison.py
- [[build_sector_comparison_table()]] - code - backtesting/reporting/tables_comparison.py
- [[build_sector_weights_table()]] - code - backtesting/reporting/tables_single.py
- [[build_top_holdings_table()]] - code - backtesting/reporting/tables_single.py
- [[build_validation_appendix_table()]] - code - backtesting/reporting/tables_single.py
- [[tables_comparison.py]] - code - backtesting/reporting/tables_comparison.py
- [[tables_single.py]] - code - backtesting/reporting/tables_single.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Backtesting_Reporting_Tables_Single
SORT file.name ASC
```

## Connections to other communities
- 19 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 2 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 2 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 2 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Performance]]

## Top bridge nodes
- [[ComparisonTableBuilder]] - degree 5, connects to 3 communities
- [[TearsheetTableBuilder]] - degree 5, connects to 3 communities
- [[tables_single.py]] - degree 19, connects to 1 community
- [[tables_comparison.py]] - degree 14, connects to 1 community
- [[build_performance_summary_table()]] - degree 3, connects to 1 community