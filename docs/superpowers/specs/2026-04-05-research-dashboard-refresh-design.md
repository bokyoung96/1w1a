# Research Dashboard Refresh Design

## Goal

Upgrade the dashboard into a research-grade multi-strategy workspace that:

- reuses or auto-runs saved strategies without duplicate active runs
- computes strategy signals with enough warmup history while only showing the requested display range
- supports strategy-specific benchmarks
- exposes richer analytical payloads and drill-down interactions
- documents how to run and maintain the system

## Scope

This design covers four areas:

1. Backtest execution and saved-run lifecycle
2. Dashboard strategy presets and benchmark configuration
3. Dashboard API payload expansion and analytics calculations
4. Frontend information architecture and drill-down workspace

## Requirements

### Warmup-Aware Backtests

- Each dashboard strategy preset must declare enough historical warmup to support its signal construction.
- Warmup is internal only: data load, signal construction, benchmark alignment, and rolling analytics use the extended range.
- Persisted and displayed outputs must be trimmed back to the requested user range so the first visible date does not show unstable AUM or partial-history artefacts.
- The warmup model must be extensible enough to support simple lookback rules first, without blocking later additions such as fundamental lag buffers.

### Strategy-Specific Benchmarks

- Benchmarks are configured per dashboard strategy preset, not as one global benchmark.
- The dashboard payload must provide benchmark context and series per selected strategy.
- Multi-strategy overview charts must show strategy lines and their corresponding benchmark lines together.
- Research views must include benchmark-relative analytics such as yearly excess returns.

### Duplicate Run Hygiene

- Saved-run signatures are determined by normalized strategy configuration:
  - strategy identifier
  - global execution config
  - strategy params
  - benchmark config where it affects research payload semantics
- Only the newest run in a signature group is active.
- Older duplicates are automatically moved to `results/backtests/_archived/` during dashboard launch.
- `/api/runs` and dashboard selection UI must never show duplicate active runs for the same strategy/config signature.

### Research Workspace

- The page remains a multi-strategy comparison dashboard first.
- A full-width research workspace expands below the overview and renders richer analytics for the current selection.
- Default mode compares all selected strategies.
- Clicking a strategy-oriented overview element changes focus to that strategy inside the same workspace.
- Clicking sector-oriented detail changes focus to that sector across the selected strategies.
- No modal-based detail flow; drill-down remains in-page.

### Analytics Coverage

The research workspace must support, at minimum:

- return and max-drawdown as a shared subplot layout
- benchmark overlays in overview comparison
- rolling Sharpe
- return distribution
- monthly return heatmap
- yearly excess returns
- sector performance time series
- sector weight time series
- richer tables for drawdowns and benchmark-relative metrics

### Documentation

README must explain:

- how to run the dashboard
- where dashboard strategies are configured
- where backtest strategies live
- how benchmark configuration works
- how duplicate run archival works

## Architecture

## 1. Strategy Preset Model

`dashboard/strategies.py` becomes the single dashboard orchestration source of truth.

Each preset will define:

- strategy name
- display label
- enabled flag
- strategy params
- benchmark config
- warmup config

Global launch config remains responsible for shared execution defaults such as start/end/schedule/fill mode.

## 2. Execution Pipeline

`dashboard/run.py` will:

1. build the frontend
2. deduplicate/archive saved runs under the dashboard result root
3. resolve the newest active run for each enabled preset
4. execute only missing or stale presets
5. create the API app with default selected runs and built frontend assets

Backtest execution will convert preset warmup metadata into an internal load start date before calling the existing backtest runner.

`backtesting/run.py` remains the main execution engine, but it will accept a display range distinct from load range so saved outputs are trimmed after computation.

## 3. Snapshot / Payload Layer

The current `PerformanceSnapshot` path is sufficient for overview metrics but not for research analytics.

This design adds dashboard-oriented research snapshot structures that can be computed from `SavedRun` plus benchmark and sector repositories. Where possible, these calculations should reuse existing reporting conventions rather than inventing parallel formulas.

Expected additions:

- benchmark overlay bundles per run
- monthly matrix / heatmap data
- yearly excess return tables/series
- return distribution bins
- sector contribution or performance series
- sector weight time series
- research focus metadata used by the frontend

The dashboard API will keep a lightweight overview payload and add research fields rather than forcing the frontend to reconstruct analytics client-side.

## 4. Frontend Layout

The frontend keeps the current cinematic overview shell but reduces it to a selection-and-summary role.

Below that, a new research workspace renders:

1. overview comparison figure
2. return + drawdown subplot pair
3. distribution and heatmap row
4. rolling and excess-return row
5. sector performance and sector-weight row
6. tables / episodes / context drill-down row

The workspace responds to focus changes:

- `all-selected`
- `strategy:<runId>`
- `sector:<sectorName>`

## Data Flow

1. Strategy presets define warmup + benchmark + params.
2. Launcher deduplicates runs, resolves newest active signatures, and runs missing presets.
3. Dashboard API reads active saved runs only.
4. Snapshot services compute overview and research analytics using trimmed display ranges.
5. Frontend fetches runs, session bootstrap, and analytics payload, then renders overview plus research workspace.
6. User clicks change research focus without leaving the page.

## Error Handling

- Missing benchmark data must degrade to explicit empty-state annotations, not silent chart corruption.
- Archived runs must not break legacy direct-run lookups; only active run indices are filtered.
- Invalid or malformed saved configs remain ignored during resolution and dedupe.
- Research charts must tolerate missing optional data by hiding only the affected panel.

## Testing Strategy

- Unit tests for warmup-to-load-range calculation and trimmed output persistence
- Unit tests for run dedupe/archive semantics
- API tests for strategy-specific benchmark payloads and research sections
- Frontend tests for focus switching, duplicate suppression, and research workspace rendering
- End-to-end verification for launcher reuse vs rerun behavior

## Non-Goals

- Full report-builder replacement inside the dashboard
- Arbitrary user-authored dashboard presets from the UI
- Real-time streaming data

