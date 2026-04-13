# Tests Dashboard Test_Run

> 35 nodes · cohesion 0.10

## Key Concepts

- **test_run.py** (16 connections) — `tests/dashboard/test_run.py`
- **run.py** (15 connections) — `dashboard/run.py`
- **launch_dashboard()** (13 connections) — `dashboard/run.py`
- **ReportCli** (12 connections) — `backtesting/reporting/cli.py`
- **ReportArgumentParser.parse_args()** (11 connections) — `backtesting/reporting/cli.py`
- **build_frontend()** (11 connections) — `dashboard/run.py`
- **ReportCli.parser()** (10 connections) — `backtesting/reporting/cli.py`
- **ReportCli.run()** (10 connections) — `backtesting/reporting/cli.py`
- **cli.py** (8 connections) — `backtesting/reporting/cli.py`
- **FakeRunner** (6 connections) — `tests/dashboard/test_run.py`
- **build_parser()** (5 connections) — `dashboard/run.py`
- **_build_run_config()** (5 connections) — `dashboard/run.py`
- **test_report_cli_parses_run_ids()** (5 connections) — `tests/test_report_cli.py`
- **ReportKind** (4 connections) — `backtesting/reporting/models.py`
- **main()** (4 connections) — `dashboard/run.py`
- **test_launch_dashboard_passes_universe_id_to_backtest_runner()** (4 connections) — `tests/dashboard/test_run.py`
- **test_launch_dashboard_reuses_matching_runs_and_executes_missing_presets()** (4 connections) — `tests/dashboard/test_run.py`
- **test_cli_parser_supports_kind_and_benchmark_options()** (4 connections) — `tests/reporting/test_cli.py`
- **test_cli_rejects_invalid_kind_and_run_count_combination()** (4 connections) — `tests/reporting/test_cli.py`
- **ReportArgumentParser** (3 connections) — `backtesting/reporting/cli.py`
- **_install_frontend_dependencies()** (3 connections) — `dashboard/run.py`
- **test_run_script_help_works_from_repo_root()** (3 connections) — `tests/dashboard/test_run.py`
- **test_cli_builds_report_spec_with_auto_kind_and_benchmark()** (3 connections) — `tests/reporting/test_cli.py`
- **_validate_report_args()** (2 connections) — `backtesting/reporting/cli.py`
- **ReportSpec.__post_init__()** (2 connections) — `backtesting/reporting/models.py`
- *... and 10 more nodes in this community*

## Relationships

- [[Docs Superpowers Plans]] (20 shared connections)
- [[Raw Ksdq Csv]] (18 shared connections)
- [[Tests Test Run.Py Engine]] (8 shared connections)
- [[Docs Superpowers Reporting]] (6 shared connections)
- [[Tests Dashboard Backend]] (6 shared connections)
- [[Docs Superpowers Kosdaq150]] (2 shared connections)
- [[Backtesting Reporting Composers]] (2 shared connections)
- [[Docs Superpowers Breakout]] (1 shared connections)
- [[Backtesting Reporting Tests]] (1 shared connections)

## Source Files

- `backtesting/reporting/cli.py`
- `backtesting/reporting/models.py`
- `dashboard/run.py`
- `tests/dashboard/test_run.py`
- `tests/reporting/test_cli.py`
- `tests/test_report_cli.py`

## Audit Trail

- EXTRACTED: 68 (37%)
- INFERRED: 116 (63%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*