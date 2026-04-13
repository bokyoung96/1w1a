---
source_file: "dashboard/backend/services/run_index.py"
type: "code"
community: "Tests Dashboard Backend"
location: "L14"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Tests_Dashboard_Backend
---

# RunIndexService

## Connections
- [[2026-04-05-live-dashboard-single-command-launch]] - `rationale_for` [INFERRED]
- [[2026-04-05-research-dashboard-refresh]] - `rationale_for` [INFERRED]
- [[2026-04-13-kosdaq150-universe-integration]] - `rationale_for` [INFERRED]
- [[DashboardPayloadService.__init__()]] - `calls` [INFERRED]
- [[LaunchResolutionService.resolve()]] - `calls` [INFERRED]
- [[RunIndexService.__init__()]] - `contains` [EXTRACTED]
- [[RunIndexService._config_signature()]] - `contains` [EXTRACTED]
- [[RunIndexService._is_usable_run_dir()]] - `contains` [EXTRACTED]
- [[RunIndexService._load_run_option()]] - `contains` [EXTRACTED]
- [[RunIndexService._normalize_universe_id()]] - `contains` [EXTRACTED]
- [[RunIndexService._normalize_value()]] - `contains` [EXTRACTED]
- [[RunIndexService._parse_run_timestamp()]] - `contains` [EXTRACTED]
- [[RunIndexService._sort_key()]] - `contains` [EXTRACTED]
- [[RunIndexService.list_runs()]] - `contains` [EXTRACTED]
- [[_build_payload_service()]] - `calls` [INFERRED]
- [[get_run_index_service()]] - `calls` [INFERRED]
- [[run_index.py]] - `contains` [EXTRACTED]
- [[test_list_runs_dedupes_legacy_and_new_schema_copies_of_same_config()]] - `calls` [INFERRED]
- [[test_list_runs_ignores_archived_and_duplicate_config_runs()]] - `calls` [INFERRED]
- [[test_list_runs_keeps_older_valid_run_when_newer_duplicate_is_incomplete()]] - `calls` [INFERRED]
- [[test_list_runs_returns_newest_first()]] - `calls` [INFERRED]
- [[test_list_runs_skips_malformed_json_and_invalid_numeric_values()]] - `calls` [INFERRED]
- [[test_list_runs_treats_legacy_k200_and_missing_universe_id_as_equivalent()]] - `calls` [INFERRED]
- [[test_list_runs_treats_universe_id_as_part_of_signature()]] - `calls` [INFERRED]

#graphify/code #graphify/INFERRED #community/Tests_Dashboard_Backend