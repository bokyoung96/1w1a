# Run Artifacts

> 42 nodes · cohesion 0.09

## Key Concepts

- **results/backtests Run Store** (10 connections) — `results/backtests`
- **Backtest Runner** (7 connections) — `backtesting/run.py`
- **BenchmarkConfig** (7 connections) — `backtesting/reporting/models.py`
- **Performance Snapshot Factory** (7 connections) — `backtesting/reporting/snapshots.py`
- **Saved Run Artifact** (7 connections) — `backtesting/reporting/models.py`
- **Dashboard Payload Service** (6 connections) — `dashboard/backend/services/dashboard_payload.py`
- **Dashboard Launch Config** (5 connections) — `dashboard/strategies.py`
- **Dashboard Launcher** (5 connections) — `dashboard/run.py`
- **Launch Resolution Service** (5 connections) — `dashboard/backend/services/launch_resolution.py`
- **Report Builder** (5 connections) — `backtesting/reporting/builder.py`
- **Report CLI** (5 connections) — `backtesting/reporting/cli.py`
- **Run Index Service** (5 connections) — `dashboard/backend/services/run_index.py`
- **Run Reader** (5 connections) — `backtesting/reporting/reader.py`
- **Dashboard Backend App** (4 connections) — `dashboard/backend/main.py`
- **Momentum Strategy** (4 connections) — `backtesting/strategies/momentum.py`
- **OP Forward Yield Strategy** (4 connections) — `backtesting/strategies/op_fwd.py`
- **Strategy Preset** (4 connections) — `dashboard/strategies.py`
- **52W Breakout Strategy, Simple** (3 connections) — `backtesting/strategies/breakout_simple.py`
- **52W Breakout Strategy, Staged** (3 connections) — `backtesting/strategies/breakout_staged.py`
- **Breakout 52W Simple Run (daily, close; CAGR -1.47%, MDD -51.66%)** (3 connections) — `results/backtests/breakout_52w_simple_2020-01-01_2025-12-31_20260412_224119`
- **Breakout 52W Simple Run (daily, close; CAGR -1.47%, MDD -51.66%)** (3 connections) — `results/backtests/breakout_52w_simple_2020-01-01_2025-12-31_20260412_224539`
- **Breakout 52W Staged Run (daily, close; CAGR +1.01%, MDD -38.12%)** (3 connections) — `results/backtests/breakout_52w_staged_2020-01-01_2025-12-31_20260412_224143`
- **Breakout 52W Staged Run (daily, close; CAGR +0.87%, MDD -38.32%)** (3 connections) — `results/backtests/breakout_52w_staged_2020-01-01_2025-12-31_20260412_224603`
- **Dashboard API Router** (3 connections) — `dashboard/backend/api.py`
- **Dashboard Backend Requirements** (3 connections) — `dashboard/backend/requirements.txt`
- *... and 17 more nodes in this community*

## Relationships

- No strong cross-community connections detected

## Source Files

- `backtesting/reporting/builder.py`
- `backtesting/reporting/cli.py`
- `backtesting/reporting/models.py`
- `backtesting/reporting/reader.py`
- `backtesting/reporting/snapshots.py`
- `backtesting/reporting/writer.py`
- `backtesting/run.py`
- `backtesting/strategies/breakout_simple.py`
- `backtesting/strategies/breakout_staged.py`
- `backtesting/strategies/momentum.py`
- `backtesting/strategies/op_fwd.py`
- `dashboard/backend/api.py`
- `dashboard/backend/main.py`
- `dashboard/backend/requirements.txt`
- `dashboard/backend/services/dashboard_payload.py`
- `dashboard/backend/services/launch_resolution.py`
- `dashboard/backend/services/run_index.py`
- `dashboard/run.py`
- `dashboard/strategies.py`
- `parquet`

## Audit Trail

- EXTRACTED: 108 (72%)
- INFERRED: 42 (28%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*