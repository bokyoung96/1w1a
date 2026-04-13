# Dashboard Backend Schemas

> 60 nodes · cohesion 0.07

## Key Concepts

- **schemas.py** (38 connections) — `dashboard/backend/schemas.py`
- **DashboardPayloadService.build()** (22 connections) — `dashboard/backend/services/dashboard_payload.py`
- **DashboardPayloadService** (18 connections) — `dashboard/backend/services/dashboard_payload.py`
- **serializers.py** (16 connections) — `dashboard/backend/serializers.py`
- **sanitize_finite_number()** (9 connections) — `dashboard/backend/serializers.py`
- **DashboardPayloadService._serialize_research()** (9 connections) — `dashboard/backend/services/dashboard_payload.py`
- **serialize_named_series()** (8 connections) — `dashboard/backend/serializers.py`
- **serialize_value_points()** (8 connections) — `dashboard/backend/serializers.py`
- **DashboardPayloadService._serialize_launch_benchmark_context()** (7 connections) — `dashboard/backend/services/dashboard_payload.py`
- **test_strategies.py** (6 connections) — `tests/dashboard/test_strategies.py`
- **serialize_category_series()** (6 connections) — `dashboard/backend/serializers.py`
- **serialize_drawdown_episodes()** (6 connections) — `dashboard/backend/serializers.py`
- **serialize_heatmap()** (6 connections) — `dashboard/backend/serializers.py`
- **DashboardPayloadService._resolve_benchmark()** (6 connections) — `dashboard/backend/services/dashboard_payload.py`
- **RunIndexService._load_run_option()** (6 connections) — `dashboard/backend/services/run_index.py`
- **serialize_distribution()** (5 connections) — `dashboard/backend/serializers.py`
- **serialize_latest_holdings()** (5 connections) — `dashboard/backend/serializers.py`
- **serialize_named_values()** (5 connections) — `dashboard/backend/serializers.py`
- **DashboardPayloadService._serialize_context()** (5 connections) — `dashboard/backend/services/dashboard_payload.py`
- **DashboardPayloadService._serialize_rolling_correlation()** (5 connections) — `dashboard/backend/services/dashboard_payload.py`
- **DashboardPayloadService._snapshot_factory_for_run()** (5 connections) — `dashboard/backend/services/dashboard_payload.py`
- **enabled_strategy_presets()** (5 connections) — `dashboard/strategies.py`
- **BenchmarkModel** (4 connections) — `dashboard/backend/schemas.py`
- **DashboardResearchModel** (4 connections) — `dashboard/backend/schemas.py`
- **ResearchFocusModel** (4 connections) — `dashboard/backend/schemas.py`
- *... and 35 more nodes in this community*

## Relationships

- [[Docs Superpowers Plans]] (29 shared connections)
- [[Backtesting Reporting Frontend]] (16 shared connections)
- [[Docs Superpowers Kosdaq150]] (11 shared connections)
- [[Tests Dashboard Backend]] (11 shared connections)
- [[Raw Ksdq Csv]] (3 shared connections)
- [[Docs Superpowers Reporting]] (2 shared connections)
- [[Backtesting Reporting Composers]] (2 shared connections)
- [[Tests Test Run.Py Engine]] (2 shared connections)
- [[Docs Superpowers Analytics]] (1 shared connections)
- [[Backtesting Reporting Tests]] (1 shared connections)
- [[Docs Superpowers Policy]] (1 shared connections)

## Source Files

- `dashboard/backend/schemas.py`
- `dashboard/backend/serializers.py`
- `dashboard/backend/services/dashboard_payload.py`
- `dashboard/backend/services/run_index.py`
- `dashboard/strategies.py`
- `tests/dashboard/test_strategies.py`

## Audit Trail

- EXTRACTED: 119 (38%)
- INFERRED: 196 (62%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*