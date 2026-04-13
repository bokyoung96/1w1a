---
source_file: "dashboard/backend/services/launch_resolution.py"
type: "code"
community: "Tests Dashboard Backend"
location: "L33"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Tests_Dashboard_Backend
---

# LaunchResolutionService

## Connections
- [[2026-04-05-live-dashboard-single-command-launch]] - `rationale_for` [INFERRED]
- [[2026-04-05-research-dashboard-refresh]] - `rationale_for` [INFERRED]
- [[2026-04-13-kosdaq150-universe-integration]] - `rationale_for` [INFERRED]
- [[LaunchResolutionService.__init__()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._archive_duplicate_runs()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._archive_run_dir()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._build_saved_signature()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._build_signature()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._find_matching_run()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._is_usable_saved_run()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._load_saved_config()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._normalize_universe_id()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._normalize_use_k200()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._normalize_value()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._parse_run_timestamp()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._run_sort_key()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService._saved_signature_key()]] - `contains` [EXTRACTED]
- [[LaunchResolutionService.resolve()]] - `contains` [EXTRACTED]
- [[launch_dashboard()]] - `calls` [INFERRED]
- [[launch_resolution.py]] - `contains` [EXTRACTED]
- [[test_resolution_archives_legacy_and_new_schema_duplicates_together()]] - `calls` [INFERRED]
- [[test_resolution_archives_older_duplicate_run()]] - `calls` [INFERRED]
- [[test_resolution_does_not_match_archived_runs()]] - `calls` [INFERRED]
- [[test_resolution_executes_only_missing_strategy_when_partial_matches_exist()]] - `calls` [INFERRED]
- [[test_resolution_ignores_malformed_saved_config()]] - `calls` [INFERRED]
- [[test_resolution_ignores_non_dict_saved_config()]] - `calls` [INFERRED]
- [[test_resolution_keeps_older_valid_run_when_newer_duplicate_is_incomplete()]] - `calls` [INFERRED]
- [[test_resolution_marks_all_presets_missing_when_global_config_changes()]] - `calls` [INFERRED]
- [[test_resolution_marks_single_strategy_missing_when_strategy_params_change()]] - `calls` [INFERRED]
- [[test_resolution_marks_strategy_missing_when_benchmark_metadata_changes()]] - `calls` [INFERRED]
- [[test_resolution_marks_strategy_missing_when_universe_changes()]] - `calls` [INFERRED]
- [[test_resolution_marks_strategy_missing_when_warmup_changes()]] - `calls` [INFERRED]
- [[test_resolution_reuses_legacy_saved_run_when_only_compat_fields_are_missing()]] - `calls` [INFERRED]
- [[test_resolution_reuses_legacy_saved_run_when_universe_id_is_legacy_k200()]] - `calls` [INFERRED]
- [[test_resolution_reuses_newest_matching_run()]] - `calls` [INFERRED]
- [[test_resolution_reuses_saved_kosdaq150_run_when_use_k200_is_normalized()]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Tests_Dashboard_Backend