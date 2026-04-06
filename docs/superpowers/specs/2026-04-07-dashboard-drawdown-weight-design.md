---
title: Dashboard Drawdown & Detail Follow-up
date: 2026-04-07
author: codex
---

# Goal

Place the drawdown area right under the multi-strategy comparison chart and refocus the research detail panel:

- Add a drawdown strip directly below the hero to show cumulative drawdown for the selected runs without duplicating content.
- Keep the research detail panel for numeric summaries (Sharpe, Calmar, Information Ratio, Hit Rate as daily/weekly win ratios, Profit/Risk as reward-to-risk) plus a normalized sector-weight stack per strategy (100% scale).

# Design

1. **Drawdown strip**
   - Extend `PerformanceStrip` by adding a compact drawdown chart beneath the hero graph. Use `dashboard.performance.drawdowns` for the same run IDs and share the same color palette for clarity.
   - Label axes so the x-axis aligns with the hero and the y-axis reads “Drawdown.”

2. **Research detail metric panel**
   - Replace the current metric rows with the numeric summaries listed above; compute Hit Rate from positive vs total periods in the selected run’s returns and compute Profit/Risk as average gain per positive trade divided by average loss per negative trade (capped to keep the value realistic).
   - Add a stacked area or column showing each strategy’s sector weights normalized to 100% (total weight per date), removing the redundant “sector contribution/yearly excess” notes already covered elsewhere.

3. **Testing**
   - Verify the new drawdown strip appears for multi-run selections, the detail panel renders the numeric summaries and normalized stack, and tests expect the new labels/logics.
