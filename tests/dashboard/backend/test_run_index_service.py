from __future__ import annotations

import json
from pathlib import Path

from dashboard.backend.services.run_index import RunIndexService


def _write_run(root: Path, run_id: str, *, name: str, strategy: str, final_equity: float) -> None:
    run_dir = root / run_id
    (run_dir / "series").mkdir(parents=True)
    (run_dir / "positions").mkdir()
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "name": name,
                "strategy": strategy,
                "start": "2020-01-01",
                "end": "2020-12-31",
                "schedule": "monthly",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(
            {
                "final_equity": final_equity,
                "avg_turnover": 0.12,
            }
        ),
        encoding="utf-8",
    )


def test_list_runs_returns_newest_first(tmp_path: Path) -> None:
    _write_run(tmp_path, "zeta_20240405_090000", name="Momentum", strategy="momentum", final_equity=130_000_000.0)
    _write_run(tmp_path, "alpha_20260405_100000", name="OP Fwd Yield", strategy="op_fwd_yield", final_equity=125_000_000.0)

    service = RunIndexService(tmp_path)

    runs = service.list_runs()

    assert [run.run_id for run in runs] == ["alpha_20260405_100000", "zeta_20240405_090000"]
    assert runs[0].label == "OP Fwd Yield"
    assert runs[0].strategy == "op_fwd_yield"
    assert runs[0].summary.final_equity == 125_000_000.0


def test_list_runs_skips_malformed_json_and_invalid_numeric_values(tmp_path: Path) -> None:
    valid_dir = tmp_path / "valid_run_20260405_120000"
    valid_dir.mkdir()
    (valid_dir / "config.json").write_text(json.dumps({"name": "Momentum", "strategy": "momentum"}), encoding="utf-8")
    (valid_dir / "summary.json").write_text(json.dumps({"final_equity": 111.0, "avg_turnover": 0.2}), encoding="utf-8")

    malformed_config_dir = tmp_path / "bad_config_20260405_110000"
    malformed_config_dir.mkdir()
    (malformed_config_dir / "config.json").write_text("{", encoding="utf-8")
    (malformed_config_dir / "summary.json").write_text(json.dumps({"final_equity": 100.0, "avg_turnover": 0.1}), encoding="utf-8")

    malformed_summary_dir = tmp_path / "bad_summary_20260405_100000"
    malformed_summary_dir.mkdir()
    (malformed_summary_dir / "config.json").write_text(json.dumps({"name": "Broken", "strategy": "broken"}), encoding="utf-8")
    (malformed_summary_dir / "summary.json").write_text("{", encoding="utf-8")

    invalid_numeric_dir = tmp_path / "bad_numbers_20260405_090000"
    invalid_numeric_dir.mkdir()
    (invalid_numeric_dir / "config.json").write_text(json.dumps({"name": "Bad Numbers", "strategy": "broken"}), encoding="utf-8")
    (invalid_numeric_dir / "summary.json").write_text(
        json.dumps({"final_equity": "not-a-number", "avg_turnover": 0.3}),
        encoding="utf-8",
    )

    service = RunIndexService(tmp_path)

    runs = service.list_runs()

    assert [run.run_id for run in runs] == ["valid_run_20260405_120000"]
