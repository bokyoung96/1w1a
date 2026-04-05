# Live Dashboard Single-Command Launch Design

Date: 2026-04-05
Project: 1w1a live dashboard launcher and saved-run orchestration
Status: Approved design

## Goal

Make the live dashboard runnable with a single Python command that:

- reuses previously saved backtest runs under `results/backtests/` when they match the current dashboard launch config
- auto-runs missing or stale default strategies when matching saved runs do not exist
- serves the built frontend and the API from one FastAPI process

This removes the current two-process developer workflow from the normal user path.

## User Experience

The normal launch path becomes:

```bash
python live_dashboard/run.py
```

When the command starts:

1. The frontend production bundle is built if needed for the current launch.
2. Saved runs under `results/backtests/` are scanned.
3. For each configured default strategy, the launcher chooses the newest saved run whose effective config matches the current desired config.
4. If no matching saved run exists for a strategy, that strategy is executed and saved automatically.
5. The dashboard starts and preloads the resolved run ids.

This should feel like an operator command, not a development bootstrap sequence.

## Matching Rules

Saved-run reuse is determined by an exact config match on:

- global launch config
- strategy name
- strategy-specific params

The comparison must use a normalized config signature, not loose field checks scattered across the code.

### Reuse policy

- If a matching saved run exists for a strategy, reuse the newest one.
- If several matching runs exist, choose the newest by run timestamp.
- If only some configured strategies have matching runs, reuse those and execute only the missing ones.
- If the global config changes, every strategy becomes stale and must be re-executed.
- If a strategy's own params change, only that strategy becomes stale and must be re-executed.

## Default Strategy Set

The launcher owns a default dashboard strategy set rather than relying on ad hoc CLI flags.

The first version keeps the default set aligned with the existing registered strategies already used in the dashboard-adjacent work:

- `momentum`
- `op_fwd_yield`

Each default strategy entry includes:

- enabled toggle
- strategy name
- display label
- strategy params

The launcher can later be extended from this config surface without changing the entry command shape.

## Runtime Architecture

### Launcher

Add a dedicated launcher module at `live_dashboard/run.py`.

It is responsible for:

- loading the default launch config
- building the frontend bundle
- resolving reusable runs
- executing stale or missing runs through `BacktestRunner`
- starting the FastAPI app with the resolved default run ids

### Backend

The FastAPI app becomes the single runtime surface.

It serves:

- `/api/*` JSON endpoints
- static frontend assets from `live_dashboard/frontend/dist`
- the SPA entry point for non-API routes

The backend also exposes the launcher-resolved default run ids so the frontend can hydrate without immediately guessing its own initial selection.

### Frontend

The frontend should behave like a production SPA, not a Vite-only development shell.

It must:

- read bootstrap state from the backend on first load
- use launcher-provided default run ids when available
- keep the existing manual selection behavior after hydration

The Vite dev workflow can remain for local frontend work, but it is no longer the normal user path.

## Data Flow

1. `live_dashboard/run.py` constructs the desired launch targets from the default config.
2. A run-resolution service scans `results/backtests/` and computes a normalized signature for each saved run.
3. Matching runs are selected per strategy using newest-first ordering.
4. Missing or stale strategies are executed through `BacktestRunner`.
5. The resolved run ids are injected into the FastAPI app factory.
6. The frontend requests bootstrap state, receives the default selected run ids, and then fetches the dashboard payload.

## Config Signature Shape

The signature must be stable and serializable so both saved runs and desired launch targets use the same normalization path.

The normalized shape should include:

- `start`
- `end`
- `capital`
- `schedule`
- `fill_mode`
- `fee`
- `sell_tax`
- `slippage`
- `use_k200`
- `allow_fractional`
- `strategy`
- strategy params such as `top_n` and `lookback`

Display labels and run ids must not affect matching.

## Failure Handling

- If the frontend build fails, launch must stop with a clear error.
- If a configured strategy name is not registered, launch must fail before starting any run.
- If a saved run is malformed or missing required files, it should be ignored for reuse rather than crashing run discovery.
- If auto-execution fails for a missing strategy, launch should stop and surface the failing strategy name.

## Testing Strategy

Tests must cover:

- config signature normalization
- newest-match selection
- partial reuse with only missing strategies executed
- full invalidation when global config changes
- strategy-level invalidation when strategy params change
- single-command launcher injecting default selected run ids into the backend
- backend SPA/static serving and bootstrap payload exposure

## Non-Goals

This change does not add:

- background refresh
- scheduling
- user-editable launch config UI
- dev-server orchestration inside the production launcher
