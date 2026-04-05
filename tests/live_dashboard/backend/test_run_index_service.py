from __future__ import annotations

import json
from pathlib import Path

from live_dashboard.backend.services.run_index import RunIndexService


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
    _write_run(tmp_path, "momentum_20260405_090000", name="Momentum", strategy="momentum", final_equity=130_000_000.0)
    _write_run(tmp_path, "value_20260405_100000", name="OP Fwd Yield", strategy="op_fwd_yield", final_equity=125_000_000.0)

    service = RunIndexService(tmp_path)

    runs = service.list_runs()

    assert [run.run_id for run in runs] == ["value_20260405_100000", "momentum_20260405_090000"]
    assert runs[0].label == "OP Fwd Yield"
    assert runs[0].strategy == "op_fwd_yield"
    assert runs[0].summary.final_equity == 125_000_000.0


def test_list_runs_skips_directories_missing_config_or_summary(tmp_path: Path) -> None:
    valid_dir = tmp_path / "valid_run"
    valid_dir.mkdir()
    (valid_dir / "config.json").write_text(json.dumps({"name": "Momentum", "strategy": "momentum"}), encoding="utf-8")
    (valid_dir / "summary.json").write_text(json.dumps({"final_equity": 111.0, "avg_turnover": 0.2}), encoding="utf-8")

    incomplete_dir = tmp_path / "broken_run"
    incomplete_dir.mkdir()
    (incomplete_dir / "config.json").write_text(json.dumps({"name": "Broken"}), encoding="utf-8")

    service = RunIndexService(tmp_path)

    runs = service.list_runs()

    assert [run.run_id for run in runs] == ["valid_run"]
