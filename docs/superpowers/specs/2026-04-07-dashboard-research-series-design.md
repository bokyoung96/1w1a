---
title: Dashboard Research Series Refinement
date: 2026-04-07
author: codex
---

# Goal

Finish the remaining research-focused polish so the detail strip and charts show only the most valuable summaries:
1. Compact the research detail panel into a single line of stats (cumulative return, max drawdown, Sharpe, Calmar, Information Ratio, Hit Rate, Profit/Risk) plus the "toughest drawdown" note so it clearly communicates the most important telemetry without wasting vertical space.
2. Move every sector-level trend into the research chart area: each strategy should render its own normalized sector-weight series (stacked to 100%) and its cumulative sector-contribution series so sector behavior aligns with strategy focus instead of repeating inside the detail panel.

# Context

- **PerformanceStrip** already handles the hero cumulative return / drawdown view and the trimmed launch metadata; this work leaves that structure untouched aside from ensuring the drawdown chart sits directly underneath the multi-strategy comparison as requested earlier.
- **ResearchDetailPanel** currently mixes per-strategy sector charts with the metric summary; we now need to remove those charts and reframe the panel around the condensed stat row plus the "toughest drawdown" explanation.
- **ResearchWorkspace** already includes reusable helpers for normalized sector weights and sector contributions (see `buildNormalizedSectorWeightsOption`/`buildCumulativeContributionOption`), so we can reuse them to render the new strategy-specific charts.

# Design

1. **Research detail panel**
   - Replace the existing columnar "metric chip" grid with a single responsive row (wraps on small screens) that lists the seven values in this order: `Cumulative return`, `Max drawdown`, `Sharpe`, `Calmar`, `Information Ratio`, `Hit Rate`, `Profit / Risk`. Each chip will continue to show a label above the value to keep the typography consistent with the existing detail strip.
   - `Hit Rate` is computed from the same point-to-point diffs that the panel already calculates; format it as a percentage with one decimal place. `Profit / Risk` stays in the format like `2.34:1`, with `n/a` if data is missing.
   - Keep the "toughest drawdown" banner under the stat row but tighten the language: mention only the single worst open drawdown (prefer longer duration when open, otherwise highest magnitude) and the number of days it has been open or a completed recovery time if available. Remove the per-run contribution/weight charts from this panel so it purely communicates numbers, not time series.
2. **Research chart area**
   - For each selected strategy, render two adjacent chart cards: (a) a normalized sector-weight area chart that stacks contributions so the sum is 100% every date, and (b) a cumulative sector-contribution line/area chart that accumulates each sector's contribution over time to emphasize secular trends. Hide none of these charts; strategy-level granularity is the goal.
   - Reuse the existing sector palette and chart builders, but ensure the normalized weights chart uses `stack` and `areaStyle` to visually fill to 100% while showing how each sector share shifts over time. Label the cards as "Sector weights (normalized 100%)" and "Sector contribution (cumulative)" so it is unmistakable what each view represents.
   - Remove the earlier "Research plots" for sector weights and contributions from the detail panel so the new chart cards are the sole location for those series. The research workspace still begins with the heatmap and distributions, but the sector weight/contribution rows now live in a dedicated "Strategy sector trends" section just above the detail panel.

# Testing & Verification

- Update `ResearchDetailPanel` tests (and any other motivated snapshot/DOM tests) to reflect the seven-chip row and the revised toughest-drawdown line. Remove assertions that expect the per-strategy sector charts to appear inside `ResearchDetailPanel`.
- Ensure any `App`/`PerformanceStrip` tests covering metadata or focus copy still pass; no behavior change is expected there, but the selectors may shift as the adjacent DOM now looks different.
- Run the suite (`npm run test -- --watch=false`) after the UI adjustments plus `npm run build` to confirm TypeScript and bundler correctness.

Please review this spec before implementation. Once approved, I will create an implementation plan (via `writing-plans`) and then proceed with the code changes.
