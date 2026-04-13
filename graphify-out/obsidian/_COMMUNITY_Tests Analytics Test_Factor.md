---
type: community
cohesion: 0.31
members: 11
---

# Tests Analytics Test_Factor

**Cohesion:** 0.31 - loosely connected
**Members:** 11 nodes

## Members
- [[factor.py]] - code - backtesting/analytics/factor.py
- [[quantile_returns()]] - code - backtesting/analytics/factor.py
- [[rank_ic()]] - code - backtesting/analytics/factor.py
- [[test_factor.py]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_drops_duplicate_signals_without_error()]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_returns_empty_frame_without_overlap()]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_returns_empty_frame_without_shared_columns()]] - code - tests/analytics/test_factor.py
- [[test_quantile_returns_uses_overlap_and_keeps_sparse_rows()]] - code - tests/analytics/test_factor.py
- [[test_rank_ic_returns_empty_series_without_overlap()]] - code - tests/analytics/test_factor.py
- [[test_rank_ic_returns_empty_series_without_shared_columns()]] - code - tests/analytics/test_factor.py
- [[test_rank_ic_uses_common_overlap_and_returns_nan_when_empty()]] - code - tests/analytics/test_factor.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tests_Analytics_Test_Factor
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 2 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Policy]]

## Top bridge nodes
- [[quantile_returns()]] - degree 7, connects to 2 communities
- [[rank_ic()]] - degree 6, connects to 2 communities
- [[test_factor.py]] - degree 12, connects to 1 community
- [[factor.py]] - degree 4, connects to 1 community
- [[test_quantile_returns_drops_duplicate_signals_without_error()]] - degree 3, connects to 1 community