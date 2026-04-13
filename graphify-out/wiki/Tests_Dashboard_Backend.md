# Tests Dashboard Backend

> 131 nodes · cohesion 0.04

## Key Concepts

- **DataCatalog.get()** (77 connections) — `backtesting/catalog/catalog.py`
- **LaunchResolutionService.resolve()** (46 connections) — `dashboard/backend/services/launch_resolution.py`
- **test_dashboard_api.py** (44 connections) — `tests/dashboard/backend/test_dashboard_api.py`
- **LaunchResolutionService** (36 connections) — `dashboard/backend/services/launch_resolution.py`
- **test_launch_resolution.py** (29 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **_write_saved_run()** (29 connections) — `tests/dashboard/backend/test_dashboard_api.py`
- **RunIndexService** (24 connections) — `dashboard/backend/services/run_index.py`
- **_build_payload_service()** (23 connections) — `tests/dashboard/backend/test_dashboard_api.py`
- **test_run_index_service.py** (17 connections) — `tests/dashboard/backend/test_run_index_service.py`
- **test_run.py** (16 connections) — `tests/dashboard/test_run.py`
- **list_runs()** (16 connections) — `dashboard/backend/api.py`
- **run.py** (15 connections) — `dashboard/run.py`
- **launch_dashboard()** (13 connections) — `dashboard/run.py`
- **_write_matching_run()** (12 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **launch_resolution.py** (11 connections) — `dashboard/backend/services/launch_resolution.py`
- **create_app()** (11 connections) — `dashboard/backend/main.py`
- **build_frontend()** (11 connections) — `dashboard/run.py`
- **_write_run()** (11 connections) — `tests/dashboard/backend/test_run_index_service.py`
- **KISAuth** (9 connections) — `kis/config.py`
- **api.py** (9 connections) — `dashboard/backend/api.py`
- **_write_matching_default_runs()** (9 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **main.py** (8 connections) — `dashboard/backend/main.py`
- **_saved_config()** (8 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **LaunchResolutionService._archive_duplicate_runs()** (7 connections) — `dashboard/backend/services/launch_resolution.py`
- **LaunchResolutionService._build_saved_signature()** (7 connections) — `dashboard/backend/services/launch_resolution.py`
- *... and 106 more nodes in this community*

## Relationships

- [[Docs Superpowers Plans]] (40 shared connections)
- [[Docs Superpowers Kosdaq150]] (40 shared connections)
- [[Backtesting Reporting Frontend]] (35 shared connections)
- [[Raw Ksdq Csv]] (27 shared connections)
- [[Tests Test Run.Py Engine]] (21 shared connections)
- [[Backtesting Reporting Composers]] (13 shared connections)
- [[Dashboard Backend Schemas]] (11 shared connections)
- [[Tests Reporting Analytics]] (8 shared connections)
- [[Backtesting Reporting Tests]] (7 shared connections)
- [[Docs Superpowers Reporting]] (3 shared connections)
- [[Docs Superpowers Policy]] (2 shared connections)
- [[Docs Superpowers Live]] (2 shared connections)

## Source Files

- `backtesting/catalog/catalog.py`
- `backtesting/universe.py`
- `dashboard/backend/__init__.py`
- `dashboard/backend/api.py`
- `dashboard/backend/main.py`
- `dashboard/backend/services/launch_resolution.py`
- `dashboard/backend/services/run_index.py`
- `dashboard/frontend/src/lib/api.ts`
- `dashboard/run.py`
- `kis/config.py`
- `tests/dashboard/backend/test_dashboard_api.py`
- `tests/dashboard/backend/test_launch_resolution.py`
- `tests/dashboard/backend/test_run_index_service.py`
- `tests/dashboard/test_run.py`
- `tests/data/test_universe.py`

## Audit Trail

- EXTRACTED: 266 (30%)
- INFERRED: 628 (70%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*