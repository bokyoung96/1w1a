# Dashboard Analytics Refresh Design

## Goal

Refresh the dashboard so the research and exposure sections surface the launch configuration, make the analytics easier to read, and restore broken sector and yearly charts without removing the sector-oriented analytics that already exist.

The updated dashboard should:

- surface the dashboard launch global config in the top comparison area
- move metadata out of the lower detail clutter and into a single top-level source of truth
- replace the smoothed return distribution with visibly binned distributions
- show both daily and monthly return distributions
- add rolling correlation alongside rolling Sharpe and rolling beta
- show latest-holdings winners and losers based on the latest rebalance cohort
- preserve and improve sector contribution and sector weight analytics
- add a sector weight donut for the latest snapshot without replacing the existing sector series

## Scope

This design covers:

1. Dashboard payload expansion for launch metadata and new analytics
2. Frontend layout changes in the comparison, research, and exposure sections
3. Repair and presentation improvements for yearly excess return and sector charts
4. Test coverage for the new payload fields and chart behavior

## Requirements

### Launch Metadata Visibility

- The dashboard must expose the launch-level global config used by the default dashboard launcher.
- The top comparison area must show small metadata items for:
  - configured start date
  - configured end date
  - capital
  - schedule
  - fill mode
  - benchmark context
  - as-of date
- This replaces the old lower-page metadata emphasis. The top metadata rail becomes the primary display location for this information.
- Run-specific context such as benchmark name and actual visible range still remains available in the payload for per-run display and tooltips.

### Return Distribution Readability

- The return distribution must render as explicit bins rather than a smoothed curve.
- The dashboard must show both daily and monthly return distributions.
- The chart must visually communicate bin density with bar or histogram-style marks so users can see how returns cluster.
- Distribution tooltips must continue to format return values and frequencies as percentages.

### Rolling Risk Coverage

- The research workspace must show rolling Sharpe, rolling correlation, and rolling beta.
- Rolling correlation is defined as rolling correlation between strategy returns and the selected benchmark returns over the same window used for rolling Sharpe and beta.
- Rolling beta remains visible; it is not replaced by correlation.
- The rolling risk section should feel like one family of diagnostics rather than unrelated charts.

### Latest Holdings Winners And Losers

- Latest holdings remain anchored to the latest available holdings snapshot.
- For each selected run, the dashboard must compute the best and worst five holdings from the latest holdings cohort.
- Ranking is based on each held symbol's return from the last rebalance date that produced the latest holdings composition through the run's as-of date.
- The exposure section must show:
  - latest holdings with target and absolute weight
  - top 5 winners since latest rebalance
  - top 5 losers since latest rebalance
- If the required price history cannot be resolved for a symbol, the symbol should be skipped rather than poisoning the whole list.

### Sector Analytics Preservation

- Existing sector contribution and sector weight time-series analytics must remain in the dashboard.
- New visuals such as the sector donut are additive and must not replace the existing sector contribution or sector weight series.
- Sector drill-down behavior must continue to work across the preserved charts.
- Charts that currently fail to render or render misleadingly must be corrected at the payload or option-construction layer.

### Yearly Excess Returns Reliability

- Yearly excess returns must render as a valid comparative bar chart when data exists.
- The chart should use the actual available years from the payload and avoid misleading empty-year scaffolding.
- Missing values for a run in a year should be shown as absent or neutral in a way that does not suppress valid years from other runs.

## Architecture

## 1. Payload Expansion

`dashboard.backend.services.dashboard_payload.DashboardPayloadService` remains the backend composition point.

The payload will be extended in three places:

- `context`
  - keep per-run visible start, end, benchmark, and as-of metadata
  - add shared dashboard launch metadata derived from `dashboard/strategies.py`
- `rolling`
  - add `rollingCorrelation`
- `research` / `exposure`
  - add monthly return distribution bins
  - add latest-holdings leaders and laggards based on latest rebalance cohort
  - keep existing sector contribution and sector weight series

This keeps the frontend thin and avoids re-deriving benchmark-relative or holdings-relative calculations in the browser.

## 2. Snapshot Calculations

`backtesting.reporting.snapshots.PerformanceSnapshotFactory` will own the new derived analytics because it already has access to strategy returns, benchmark returns, run weights, and sector repositories.

New calculations:

- rolling correlation:
  - 252-day rolling correlation between strategy returns and benchmark returns
- monthly return distribution:
  - distribution bins built from monthly returns, parallel to the existing daily distribution
- latest holdings rebalance window:
  - find the latest rebalance date that produced the final non-zero holdings vector
  - compute symbol returns from that date to the run as-of date using the sector repository price frame
- holdings winners and losers:
  - rank current holdings by that rebalance-window return
  - keep top 5 and bottom 5

The latest holdings leaderboard is intentionally tied to the latest holdings cohort only. It does not attempt to describe historical winners across symbols no longer held.

## 3. Frontend Layout

The existing shell stays intact, but the research and exposure blocks are reorganized for readability.

### Comparison Plane

- keep the hero performance comparison chart
- insert a compact metadata rail under the section copy or adjacent to it
- show global config items in small pills or compact definition rows

### Research Workspace

Reorganize into four conceptual blocks:

1. Return and drawdown overview
2. Distribution and heatmap
3. Rolling risk and yearly excess returns
4. Sector analytics

Detailed expectations:

- Return distribution card:
  - show daily and monthly binned distributions together
- Rolling risk area:
  - show Sharpe, correlation, and beta as coordinated diagnostics
- Sector analytics area:
  - preserve sector contribution series
  - preserve sector weight series
  - add latest sector weight donut as a complementary snapshot

### Exposure Band

Promote the exposure section from a plain latest-holdings table into a current-position summary:

- latest holdings
- top 5 winners since latest rebalance
- top 5 losers since latest rebalance
- latest sector weights list or donut-supported summary

Sector row drill-down remains available from this section.

## Data Flow

1. `dashboard/strategies.py` remains the source of dashboard launch defaults.
2. The dashboard payload service reads selected runs and also resolves the default launch metadata.
3. The snapshot factory computes rolling correlation, monthly return distributions, and latest-holdings leaderboards.
4. Serializers emit the new fields in the existing camelCase API contract.
5. The frontend renders the top metadata rail, histogram-style distributions, rolling diagnostics, repaired yearly excess chart, preserved sector charts, and holdings winners/losers.
6. Focus changes continue to drive strategy and sector drill-down without route changes.

## Error Handling

- Missing launch metadata must degrade to omitted pills, not broken headers.
- Missing monthly returns should fall back to derivation from daily returns, consistent with the existing reporting path.
- Missing sector price history for holdings leaderboards should skip unsupported symbols and still return partial winners/losers.
- Missing or empty series for rolling correlation, yearly excess returns, sector contribution, or sector weights should only blank the affected figure.
- Sector donut and leaderboard panels must tolerate empty latest holdings snapshots.

## Testing Strategy

### Backend

- API tests for top metadata fields in the dashboard payload
- API tests for rolling correlation serialization
- API tests for monthly return distribution serialization
- API tests for latest-holdings winners and losers based on the latest rebalance cohort
- API tests that preserved sector contribution and sector weight series still serialize correctly

### Frontend

- component tests for top metadata rail rendering
- component tests for histogram/bar-style return distributions
- component tests for daily plus monthly distribution presentation
- component tests for rolling risk charts including Sharpe, correlation, and beta
- component tests for winners/losers panels
- component tests ensuring sector contribution and sector weight charts still render
- component tests for sector donut rendering and sector drill-down preservation

### Verification

- `pytest tests/dashboard/backend/test_dashboard_api.py tests/dashboard/test_run.py`
- `cd dashboard/frontend && npm test -- --run src/components/App.test.tsx`
- `cd dashboard/frontend && npm run build`

## Non-Goals

- Changing the dashboard launcher workflow
- Replacing the preserved sector charts with snapshot-only visuals
- Introducing real-time live holdings or intraday analytics
- Building user-editable dashboard metadata from the UI
