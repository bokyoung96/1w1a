# Tests Dashboard Backend

> 113 nodes · cohesion 0.05

## Key Concepts

- **DataCatalog.get()** (76 connections) — `backtesting/catalog/catalog.py`
- **LaunchResolutionService.resolve()** (45 connections) — `dashboard/backend/services/launch_resolution.py`
- **test_dashboard_api.py** (44 connections) — `tests/dashboard/backend/test_dashboard_api.py`
- **LaunchResolutionService** (36 connections) — `dashboard/backend/services/launch_resolution.py`
- **test_launch_resolution.py** (29 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **_write_saved_run()** (29 connections) — `tests/dashboard/backend/test_dashboard_api.py`
- **RunIndexService** (24 connections) — `dashboard/backend/services/run_index.py`
- **_build_payload_service()** (23 connections) — `tests/dashboard/backend/test_dashboard_api.py`
- **test_run_index_service.py** (17 connections) — `tests/dashboard/backend/test_run_index_service.py`
- **list_runs()** (16 connections) — `dashboard/backend/api.py`
- **_write_matching_run()** (12 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **create_app()** (11 connections) — `dashboard/backend/main.py`
- **_write_run()** (11 connections) — `tests/dashboard/backend/test_run_index_service.py`
- **KISAuth** (9 connections) — `kis/config.py`
- **api.py** (9 connections) — `dashboard/backend/api.py`
- **_write_matching_default_runs()** (9 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **main.py** (8 connections) — `dashboard/backend/main.py`
- **_saved_config()** (8 connections) — `tests/dashboard/backend/test_launch_resolution.py`
- **TRClient** (7 connections) — `kis/tr_id/register.py`
- **LaunchResolutionService._archive_duplicate_runs()** (7 connections) — `dashboard/backend/services/launch_resolution.py`
- **LaunchResolutionService._build_saved_signature()** (7 connections) — `dashboard/backend/services/launch_resolution.py`
- **LaunchResolutionService._normalize_value()** (7 connections) — `dashboard/backend/services/launch_resolution.py`
- **RunIndexService._config_signature()** (7 connections) — `dashboard/backend/services/run_index.py`
- **KISAuth.get_access_token()** (7 connections) — `kis/config.py`
- **LaunchResolutionService._build_signature()** (6 connections) — `dashboard/backend/services/launch_resolution.py`
- *... and 88 more nodes in this community*

## Relationships

- [[Docs Superpowers Plans]] (66 shared connections)
- [[Raw Ksdq Csv]] (47 shared connections)
- [[Backtesting Reporting Tests]] (19 shared connections)
- [[Tests Test Run.Py Engine]] (16 shared connections)
- [[Dashboard Backend Schemas]] (10 shared connections)
- [[Backtesting Reporting Composers]] (9 shared connections)
- [[Tests Dashboard Test_Run]] (6 shared connections)
- [[Docs Superpowers Policy]] (3 shared connections)
- [[Docs Superpowers Reporting]] (2 shared connections)
- [[Backtesting Reporting Tables_Single]] (2 shared connections)
- [[Kis Tools.Py Tr_Id]] (2 shared connections)
- [[Docs Superpowers Live]] (2 shared connections)

## Source Files

- `backtesting/catalog/catalog.py`
- `dashboard/backend/__init__.py`
- `dashboard/backend/api.py`
- `dashboard/backend/main.py`
- `dashboard/backend/services/launch_resolution.py`
- `dashboard/backend/services/run_index.py`
- `dashboard/frontend/src/lib/api.ts`
- `kis/config.py`
- `kis/tr_id/protocol.py`
- `kis/tr_id/register.py`
- `root.py`
- `tests/dashboard/backend/test_dashboard_api.py`
- `tests/dashboard/backend/test_launch_resolution.py`
- `tests/dashboard/backend/test_run_index_service.py`
- `tests/kis/test_root.py`

## Audit Trail

- EXTRACTED: 227 (29%)
- INFERRED: 556 (71%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*