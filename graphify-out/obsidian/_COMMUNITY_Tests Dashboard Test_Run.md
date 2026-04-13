---
type: community
cohesion: 0.10
members: 35
---

# Tests Dashboard Test_Run

**Cohesion:** 0.10 - loosely connected
**Members:** 35 nodes

## Members
- [[FakeRunner]] - code - tests/dashboard/test_run.py
- [[FakeRunner.run()]] - code - tests/dashboard/test_run.py
- [[ReportArgumentParser]] - code - backtesting/reporting/cli.py
- [[ReportArgumentParser.parse_args()]] - code - backtesting/reporting/cli.py
- [[ReportCli]] - code - backtesting/reporting/cli.py
- [[ReportCli.parser()]] - code - backtesting/reporting/cli.py
- [[ReportCli.run()]] - code - backtesting/reporting/cli.py
- [[ReportKind]] - code - backtesting/reporting/models.py
- [[ReportSpec.__post_init__()]] - code - backtesting/reporting/models.py
- [[_build_run_config()]] - code - dashboard/run.py
- [[_install_frontend_dependencies()]] - code - dashboard/run.py
- [[_needs_npm_install()]] - code - dashboard/run.py
- [[_resolve_npm_command()]] - code - dashboard/run.py
- [[_validate_report_args()]] - code - backtesting/reporting/cli.py
- [[build_frontend()]] - code - dashboard/run.py
- [[build_parser()]] - code - dashboard/run.py
- [[cli.py]] - code - backtesting/reporting/cli.py
- [[fake_rmtree()]] - code - tests/dashboard/test_run.py
- [[fake_run()]] - code - tests/dashboard/test_run.py
- [[launch_dashboard()]] - code - dashboard/run.py
- [[main()_2]] - code - dashboard/run.py
- [[run.py_1]] - code - dashboard/run.py
- [[test_build_frontend_installs_dependencies_when_node_modules_are_missing()]] - code - tests/dashboard/test_run.py
- [[test_build_frontend_reinstalls_when_lockfile_is_newer_than_install_marker()]] - code - tests/dashboard/test_run.py
- [[test_build_frontend_retries_after_clearing_corrupt_node_modules()]] - code - tests/dashboard/test_run.py
- [[test_build_frontend_runs_npm_build_without_install_when_lockfile_matches()]] - code - tests/dashboard/test_run.py
- [[test_build_parser_prints_dashboard_help()]] - code - tests/dashboard/test_run.py
- [[test_cli_builds_report_spec_with_auto_kind_and_benchmark()]] - code - tests/reporting/test_cli.py
- [[test_cli_parser_supports_kind_and_benchmark_options()]] - code - tests/reporting/test_cli.py
- [[test_cli_rejects_invalid_kind_and_run_count_combination()]] - code - tests/reporting/test_cli.py
- [[test_launch_dashboard_passes_universe_id_to_backtest_runner()]] - code - tests/dashboard/test_run.py
- [[test_launch_dashboard_reuses_matching_runs_and_executes_missing_presets()]] - code - tests/dashboard/test_run.py
- [[test_report_cli_parses_run_ids()]] - code - tests/test_report_cli.py
- [[test_run.py]] - code - tests/dashboard/test_run.py
- [[test_run_script_help_works_from_repo_root()]] - code - tests/dashboard/test_run.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tests_Dashboard_Test_Run
SORT file.name ASC
```

## Connections to other communities
- 18 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 8 edges to [[_COMMUNITY_Tests Test Run.Py Engine]]
- 7 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 6 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 6 edges to [[_COMMUNITY_Tests Dashboard Backend]]
- 5 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 4 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Kosdaq150]]
- 2 edges to [[_COMMUNITY_Backtesting Reporting Composers]]
- 1 edge to [[_COMMUNITY_Backtesting Reporting Tests]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Breakout]]

## Top bridge nodes
- [[ReportCli.run()]] - degree 10, connects to 5 communities
- [[launch_dashboard()]] - degree 13, connects to 4 communities
- [[ReportCli]] - degree 12, connects to 4 communities
- [[ReportArgumentParser.parse_args()]] - degree 11, connects to 4 communities
- [[ReportCli.parser()]] - degree 10, connects to 4 communities