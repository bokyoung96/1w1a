---
type: community
cohesion: 0.04
members: 131
---

# Tests Dashboard Backend

**Cohesion:** 0.04 - loosely connected
**Members:** 131 nodes

## Members
- [[DataCatalog.get()]] - code - backtesting/catalog/catalog.py
- [[FakeRunner]] - code - tests/dashboard/test_run.py
- [[FakeRunner.run()]] - code - tests/dashboard/test_run.py
- [[KISAuth]] - code - kis/config.py
- [[KISAuth.__init__()]] - code - kis/config.py
- [[KISAuth._clear_token()]] - code - kis/config.py
- [[KISAuth._load_token()]] - code - kis/config.py
- [[KISAuth._save_token()]] - code - kis/config.py
- [[KISAuth._should_refresh_token()]] - code - kis/config.py
- [[KISAuth.get_access_token()]] - code - kis/config.py
- [[LaunchPlan]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService.__init__()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._archive_duplicate_runs()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._archive_run_dir()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._build_saved_signature()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._build_signature()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._find_matching_run()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._is_usable_saved_run()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._load_saved_config()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._normalize_universe_id()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._normalize_use_k200()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._normalize_value()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._parse_run_timestamp()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._run_sort_key()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService._saved_signature_key()]] - code - dashboard/backend/services/launch_resolution.py
- [[LaunchResolutionService.resolve()]] - code - dashboard/backend/services/launch_resolution.py
- [[ResolvedRun]] - code - dashboard/backend/services/launch_resolution.py
- [[RunIndexService]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService.__init__()]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService._config_signature()]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService._normalize_universe_id()]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService._normalize_value()]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService._parse_run_timestamp()]] - code - dashboard/backend/services/run_index.py
- [[RunIndexService._sort_key()]] - code - dashboard/backend/services/run_index.py
- [[UniverseSpec.resolve_dataset()]] - code - backtesting/universe.py
- [[__init__.py_15]] - code - dashboard/backend/__init__.py
- [[_build_payload_service()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[_build_run_config()]] - code - dashboard/run.py
- [[_install_frontend_dependencies()]] - code - dashboard/run.py
- [[_needs_npm_install()]] - code - dashboard/run.py
- [[_resolve_npm_command()]] - code - dashboard/run.py
- [[_saved_config()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[_write_incomplete_run()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[_write_matching_default_runs()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[_write_matching_run()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[_write_run()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[_write_run_artifacts()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[_write_saved_run()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[_write_saved_run()_1]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[api.py]] - code - dashboard/backend/api.py
- [[build_frontend()]] - code - dashboard/run.py
- [[build_parser()]] - code - dashboard/run.py
- [[create_app()]] - code - dashboard/backend/main.py
- [[fake_rmtree()]] - code - tests/dashboard/test_run.py
- [[fake_run()]] - code - tests/dashboard/test_run.py
- [[get_dashboard()]] - code - dashboard/backend/api.py
- [[get_dashboard_payload_service()]] - code - dashboard/backend/api.py
- [[get_frontend_dist_dir()]] - code - dashboard/backend/main.py
- [[get_run_index_service()]] - code - dashboard/backend/api.py
- [[get_session()]] - code - dashboard/backend/api.py
- [[launch_dashboard()]] - code - dashboard/run.py
- [[launch_resolution.py]] - code - dashboard/backend/services/launch_resolution.py
- [[list_runs()]] - code - dashboard/backend/api.py
- [[main()_2]] - code - dashboard/run.py
- [[main.py]] - code - dashboard/backend/main.py
- [[query()]] - code - dashboard/frontend/src/lib/api.ts
- [[run.py_1]] - code - dashboard/run.py
- [[serve_frontend()]] - code - dashboard/backend/main.py
- [[test_build_frontend_installs_dependencies_when_node_modules_are_missing()]] - code - tests/dashboard/test_run.py
- [[test_build_frontend_reinstalls_when_lockfile_is_newer_than_install_marker()]] - code - tests/dashboard/test_run.py
- [[test_build_frontend_retries_after_clearing_corrupt_node_modules()]] - code - tests/dashboard/test_run.py
- [[test_build_frontend_runs_npm_build_without_install_when_lockfile_matches()]] - code - tests/dashboard/test_run.py
- [[test_build_parser_prints_dashboard_help()]] - code - tests/dashboard/test_run.py
- [[test_create_app_does_not_route_unknown_api_paths_to_spa()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_create_app_fails_fast_when_index_html_is_missing()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_create_app_rejects_requests_outside_frontend_dist()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_api.py]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_app_serves_frontend_index_when_dist_exists()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_endpoint_includes_exposure_payload()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_latest_holdings_returns_tolerate_small_float_residue_in_final_weights()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_latest_holdings_returns_use_latest_rebalance_weights_not_just_symbol_cohort()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_includes_latest_holdings_winners_and_losers()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_includes_launch_metadata()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_includes_monthly_return_distribution()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_includes_rolling_correlation()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_launch_benchmark_uses_shared_dashboard_default()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_preserves_korean_sector_and_stock_names()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_payload_uses_kosdaq150_defaults_when_run_is_kosdaq150()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_returns_controlled_error_for_non_directory_run_entry()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_returns_controlled_error_for_unreadable_run_directory()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_returns_multi_mode_payload_for_repeated_run_ids()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_returns_per_run_benchmark_series_for_multi_run_selection()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_returns_single_mode_payload()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_skips_non_finite_latest_holdings_values()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_dashboard_skips_non_finite_sector_weights_values()]] - code - tests/dashboard/backend/test_dashboard_api.py
- [[test_launch_dashboard_passes_universe_id_to_backtest_runner()]] - code - tests/dashboard/test_run.py
- [[test_launch_dashboard_reuses_matching_runs_and_executes_missing_presets()]] - code - tests/dashboard/test_run.py
- [[test_launch_resolution.py]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_list_runs_dedupes_legacy_and_new_schema_copies_of_same_config()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_list_runs_ignores_archived_and_duplicate_config_runs()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_list_runs_keeps_older_valid_run_when_newer_duplicate_is_incomplete()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_list_runs_returns_newest_first()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_list_runs_skips_malformed_json_and_invalid_numeric_values()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_list_runs_treats_legacy_k200_and_missing_universe_id_as_equivalent()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_list_runs_treats_universe_id_as_part_of_signature()]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_registry_default_benchmark_codes_exist_in_qw_bm_parquet()]] - code - tests/data/test_universe.py
- [[test_registry_rejects_unknown_universe()]] - code - tests/data/test_universe.py
- [[test_registry_remaps_generic_dataset_ids_to_universe_specific_ids()]] - code - tests/data/test_universe.py
- [[test_registry_returns_kosdaq150_defaults()]] - code - tests/data/test_universe.py
- [[test_registry_returns_legacy_k200_defaults()]] - code - tests/data/test_universe.py
- [[test_resolution_archives_legacy_and_new_schema_duplicates_together()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_archives_older_duplicate_run()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_does_not_match_archived_runs()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_executes_only_missing_strategy_when_partial_matches_exist()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_ignores_malformed_saved_config()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_ignores_non_dict_saved_config()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_keeps_older_valid_run_when_newer_duplicate_is_incomplete()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_marks_all_presets_missing_when_global_config_changes()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_marks_single_strategy_missing_when_strategy_params_change()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_marks_strategy_missing_when_benchmark_metadata_changes()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_marks_strategy_missing_when_universe_changes()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_marks_strategy_missing_when_warmup_changes()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_reuses_legacy_saved_run_when_only_compat_fields_are_missing()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_reuses_legacy_saved_run_when_universe_id_is_legacy_k200()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_reuses_newest_matching_run()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_resolution_reuses_saved_kosdaq150_run_when_use_k200_is_normalized()]] - code - tests/dashboard/backend/test_launch_resolution.py
- [[test_run.py]] - code - tests/dashboard/test_run.py
- [[test_run_index_service.py]] - code - tests/dashboard/backend/test_run_index_service.py
- [[test_run_script_help_works_from_repo_root()]] - code - tests/dashboard/test_run.py
- [[test_session_endpoint_returns_default_selected_run_ids()]] - code - tests/dashboard/backend/test_dashboard_api.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Tests_Dashboard_Backend
SORT file.name ASC
```

## Connections to other communities
- 40 edges to [[_COMMUNITY_Docs Superpowers Kosdaq150]]
- 35 edges to [[_COMMUNITY_Backtesting Reporting Frontend]]
- 33 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 27 edges to [[_COMMUNITY_Raw Ksdq Csv]]
- 21 edges to [[_COMMUNITY_Tests Test Run.Py Engine]]
- 13 edges to [[_COMMUNITY_Backtesting Reporting Composers]]
- 11 edges to [[_COMMUNITY_Dashboard Backend Schemas]]
- 8 edges to [[_COMMUNITY_Tests Reporting Analytics]]
- 7 edges to [[_COMMUNITY_Backtesting Reporting Tests]]
- 7 edges to [[_COMMUNITY_Docs Superpowers Plans]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Policy]]
- 2 edges to [[_COMMUNITY_Docs Superpowers Reporting]]
- 1 edge to [[_COMMUNITY_Kis Tr Id Protocol]]
- 1 edge to [[_COMMUNITY_Dashboard Frontend App]]
- 1 edge to [[_COMMUNITY_Backtesting Universe.Py]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Reporting]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Performance]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Live]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Live]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Research]]
- 1 edge to [[_COMMUNITY_Docs Superpowers Analytics]]
- 1 edge to [[_COMMUNITY_Dashboard Frontend Src]]

## Top bridge nodes
- [[LaunchResolutionService.resolve()]] - degree 46, connects to 13 communities
- [[DataCatalog.get()]] - degree 77, connects to 11 communities
- [[RunIndexService]] - degree 24, connects to 5 communities
- [[_write_saved_run()]] - degree 29, connects to 4 communities
- [[_build_payload_service()]] - degree 23, connects to 4 communities