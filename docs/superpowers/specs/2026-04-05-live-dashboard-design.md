# Live Dashboard Design

Date: 2026-04-05
Project: 1w1a live strategy dashboard
Status: Approved design

## Goal

Build a separate interactive dashboard surface for saved backtest runs under `results/backtests/`.

This surface must replace the current report-style HTML and Plotly output for interactive use. It must support:

- single selected strategy
- multiple selected strategies in the same workspace
- manual run selection over current saved runs
- a visually strong, non-generic operator experience that follows the repo's frontend constraints

This first version must not include:

- auto-refresh
- auth
- brokerage integration
- AI summary panels
- user-editable layouts

## Why A Separate Surface

The existing reporting pipeline is optimized for generated artifacts such as HTML and PDF. That is the wrong shape for the requested experience.

The new dashboard should not be built on top of:

- `report.py`
- Jinja report templates
- static Plotly report pages

It should instead be a separate app that reads the same saved run data and benchmark context, while owning its own interaction model, layout, and motion.

## Product Direction

### Visual Thesis

A warm, high-contrast operator surface that reads like a performance film strip, with one dominant market-performance plane, restrained supporting detail, and motion that gives single-to-multi mode changes real presence.

### Chosen Direction

The approved visual direction is `Cinema Strip`.

This direction is preferred over a calmer broadcast-style workspace because it gives the dashboard a distinct identity while still supporting serious analysis. The implementation must stay disciplined so the visual treatment does not outrun utility.

### Hard UI Constraints

The dashboard must follow these constraints:

- the first viewport reads as one composition
- no generic dashboard card mosaic
- no hero-style marketing surface
- no cluttered KPI strips in the first viewport
- strong `1W1A` brand presence in the app chrome
- one dominant visual plane in the first screen
- sections have one job each
- no detached floating badges or decorative overlays on the main chart
- motion is intentional and tied to hierarchy

For this product surface, the first screen should act as an operator workspace, not a landing page.

## Architecture

Use a separate application with a Python backend and a dedicated frontend.

### Recommended Stack

1. Backend: FastAPI
2. Frontend: React + Vite

This is the approved implementation direction.

### Why

- Python already owns run discovery and performance math in this repo
- the frontend needs more visual and interaction control than server-rendered templates or HTMX would provide
- this creates a clean break from the existing report output without duplicating finance logic in the browser

### Rejected Alternatives

#### FastAPI + server-rendered HTMX/Alpine

Lower frontend overhead, but not a good fit for cinematic layout transitions, richer chart interactions, or mode recomposition between one and many selected runs.

#### Static frontend over exported JSON files

Simpler runtime, but it adds a stale export layer and weakens the "interactive over current saved runs" workflow.

## System Shape

### Backend Responsibility

The backend owns:

- scanning `results/backtests/`
- run metadata discovery
- loading selected run bundles
- benchmark alignment
- performance snapshot generation
- payload shaping for the frontend

Where possible, it should reuse the existing reporting-side computation model instead of rewriting finance logic:

- `backtesting/reporting/models.py`
- `backtesting/reporting/snapshots.py`
- supporting analytics and benchmark repositories already used by reporting

### Frontend Responsibility

The frontend owns:

- application shell
- layout and responsive behavior
- run selection state
- motion and transitions
- chart rendering
- single vs multi mode recomposition
- loading, empty, and failure states

### Boundary Rule

The backend returns JSON payloads, not HTML fragments.

The frontend must not depend on:

- report templates
- report section/page abstractions
- pre-rendered Plotly HTML

## Data Model

Saved runs under `results/backtests/` remain the source of truth.

### Required Run Data

- `config.json`
- `summary.json`
- `series/equity.csv`
- `series/returns.csv`
- `series/turnover.csv`
- `positions/weights.parquet`
- `positions/latest_weights.csv` when present

### Derived Data

The backend should expose benchmark-aware and comparison-ready payloads built from `PerformanceSnapshot` and related analytics:

- strategy equity
- benchmark equity
- strategy returns
- benchmark returns
- drawdown timeline and episodes
- rolling Sharpe
- rolling beta
- average turnover and turnover series
- holdings breadth
- latest holdings
- sector weights
- sector counts
- cumulative return
- CAGR
- Sharpe
- max drawdown

## UX Model

### Core Behavior

The dashboard supports manual run selection over current saved runs.

Selection rules:

- one selected run activates single-run mode
- two or more selected runs activate multi-run mode
- the same workspace adapts between these states
- the product must not split into separate single/comparison pages

### Main Areas

#### 1. Top Rail

Contains:

- strong `1W1A` brand signal
- manual run selector entry point
- benchmark context
- timeframe controls

The top rail must stay thin and calm. It cannot become a toolbar jungle.

#### 2. Dominant Performance Strip

This is the loudest visual plane and the center of the composition.

Single-run mode:

- strategy equity vs benchmark
- integrated drawdown context
- clear active selection and benchmark labeling

Multi-run mode:

- normalized or directly comparable performance strip across selected runs
- stronger color separation
- clearer run legend behavior

This strip must dominate the first viewport. It is the dashboard's primary visual anchor.

#### 3. Secondary Diagnostic Strip

This synchronized strip sits directly under the dominant strip.

Single-run mode should prioritize:

- rolling Sharpe
- rolling beta
- turnover rhythm

Multi-run mode should prioritize:

- ranking shifts
- comparative spread or lead/lag behavior
- drawdown comparison or cumulative advantage

The strip must support linked hover/scrub behavior with the dominant chart.

#### 4. Detail Band

This lower region contains:

- holdings breadth
- latest holdings concentration
- sector composition
- sector concentration

It must use plain layout regions, columns, and dividers. It must not revert to a grid of cards.

#### 5. Context Drawer Or Side Sheet

Expanded details live here:

- run metadata
- config details
- validation info
- lower-priority summary facts

This keeps the main workspace clean while preserving access to context.

## Single Vs Multi Recomposition

The page must recompose rather than simply append more modules.

### Single-Run Mode Emphasis

- equity vs benchmark story
- drawdown depth and recovery
- rolling diagnostics
- current holdings and sector posture

### Multi-Run Mode Emphasis

- relative performance
- leadership and ranking changes
- drawdown comparison
- breadth and concentration differences across strategies

### Explicit Rule

Multi-run mode must not appear as "single mode plus extra cards". The dominant strip, secondary strip, and detail band should all shift emphasis.

## Components

The app should be broken into focused units:

- `DashboardShell`
- `RunSelector`
- `PerformanceStrip`
- `DiagnosticStrip`
- `ExposureBand`
- `ContextDrawer`

Each unit should have one responsibility and a clear interface.

## Styling

### Color

Avoid:

- purple bias
- default dark crypto gradients
- generic white SaaS panel styling

Preferred palette:

- carbon
- smoke
- warm ivory
- burnt amber
- muted signal green
- restrained red

### Typography

Use no more than two typefaces:

- one more expressive face for `1W1A`
- one sharp, readable face for interface text

### Surface Treatment

Charts should feel embedded into the product surface, not pasted screenshots or framed widgets.

## Motion

Ship at least these motions:

1. Load reveal
The performance strip resolves first, then the secondary strip, then the detail band.

2. Mode transition
When selection changes between one and many runs, geometry and emphasis shift smoothly.

3. Linked interaction
Hovering or scrubbing the main strip propagates the active date to supporting views.

Motion rules:

- noticeable in a quick recording
- smooth on mobile
- fast and restrained
- removed if ornamental

## Backend API Shape

The exact routes can change, but the backend should support at least:

- run index list
- selected run detail payload
- selected multi-run comparison payload

Payload design rules:

- no raw HTML
- stable identifiers for runs
- chart-ready time series structures
- explicit benchmark metadata
- explicit missing-data flags when a module cannot render fully

## Error Handling

### Empty State

If no runs exist under `results/backtests/`, show a deliberate empty workspace explaining that there are no selectable backtest bundles.

### Partial Data Failure

If one selected run cannot be parsed, isolate the failure in the selector or context drawer instead of breaking the whole dashboard.

### Missing Benchmark Or Sector Data

If benchmark or sector data is unavailable, degrade the affected module with an inline explanation and keep the shell stable.

## Testing

### Backend

- run discovery tests
- snapshot serialization tests
- single-selection payload tests
- multi-selection payload tests
- missing-data behavior tests

### Frontend

- selector state tests
- single-to-multi recomposition tests
- empty state tests
- partial failure tests

### Manual Verification

Verify at desktop and mobile widths that:

- the first viewport stays one composition
- the dashboard does not collapse into a card grid
- single mode and multi mode both remain legible
- motion improves hierarchy rather than adding noise

## Scope Boundaries

This design is for the first interactive dashboard version only.

Out of scope:

- auto-refresh when new result files land
- auth or multi-user state
- live trading integration
- user-customizable layout builders
- AI-generated summaries

## Implementation Notes

The dashboard should live as a new surface rather than inside `backtesting/reporting/`.

A reasonable structure is:

- `live_dashboard/backend/`
- `live_dashboard/frontend/`

The backend may still import existing reporting analytics modules if those abstractions remain clean and reusable.

The frontend should own the full presentation layer and should not inherit the report styling or report templates.

## Success Criteria

The first version is successful if:

- a user can select one or many saved runs manually
- the same screen handles both modes cleanly
- the dominant performance strip becomes the unmistakable center of the product
- the UI feels distinct from the existing HTML/PDF reporting output
- the layout remains disciplined under the frontend constraints
