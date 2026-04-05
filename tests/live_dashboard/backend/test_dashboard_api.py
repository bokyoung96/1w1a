from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository
from backtesting.reporting.snapshots import PerformanceSnapshotFactory
from live_dashboard.backend.api import get_dashboard_payload_service
from live_dashboard.backend.main import app
from live_dashboard.backend.services.dashboard_payload import DashboardPayloadService
from live_dashboard.backend.services.run_index import RunIndexService


def test_dashboard_endpoint_includes_exposure_payload(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=110.0,
        avg_turnover=0.03,
        weights=[[0.6, 0.4, 0.0], [0.55, 0.45, 0.0]],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["exposure"]["holdingsCount"] == [
        {
            "runId": "alpha_20260405_100000",
            "label": "Alpha Strategy",
            "points": [
                {"date": "2024-01-02", "value": 2.0},
                {"date": "2024-01-03", "value": 2.0},
            ],
        }
    ]
    assert payload["exposure"]["latestHoldings"] == {
        "alpha_20260405_100000": [
            {"symbol": "A", "targetWeight": 0.55, "absWeight": 0.55},
            {"symbol": "B", "targetWeight": 0.45, "absWeight": 0.45},
        ]
    }
    assert payload["exposure"]["latestHoldings"]["alpha_20260405_100000"][0]["symbol"] == "A"
    assert payload["exposure"]["sectorWeights"] == {
        "alpha_20260405_100000": [
            {"name": "Tech", "value": 0.55},
            {"name": "Utilities", "value": 0.45},
        ]
    }


def test_dashboard_returns_single_mode_payload(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=110.0,
        avg_turnover=0.03,
        weights=[[0.6, 0.4, 0.0], [0.55, 0.45, 0.0]],
    )
    _write_saved_run(
        tmp_path,
        "omega_20260405_110000",
        name="Omega Strategy",
        final_equity=120.0,
        avg_turnover=0.04,
        weights=[[0.3, 0.4, 0.3], [0.2, 0.5, 0.3]],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "single"
    assert payload["selectedRunIds"] == ["alpha_20260405_100000"]
    assert [run["runId"] for run in payload["availableRuns"]] == [
        "omega_20260405_110000",
        "alpha_20260405_100000",
    ]
    assert payload["metrics"] == {
        "alpha_20260405_100000": {
            "label": "Alpha Strategy",
            "cumulativeReturn": pytest.approx(0.1),
            "cagr": pytest.approx(164_238.77066398552),
            "annualVolatility": pytest.approx(0.7937253933193773),
            "sharpe": pytest.approx(15.874507866387544),
            "sortino": 0.0,
            "calmar": 0.0,
            "maxDrawdown": 0.0,
            "finalEquity": 110.0,
            "avgTurnover": pytest.approx(0.03),
            "alpha": pytest.approx(0.0),
            "beta": pytest.approx(20.0),
            "trackingError": pytest.approx(0.7540391236534092),
            "informationRatio": pytest.approx(15.874507866387544),
        }
    }
    assert payload["context"] == {
        "alpha_20260405_100000": {
            "label": "Alpha Strategy",
            "strategy": "momentum",
            "startDate": "2024-01-02",
            "endDate": "2024-01-03",
            "asOfDate": "2024-01-03",
            "benchmark": {"code": "IKS200", "name": "KOSPI200"},
        }
    }
    assert payload["performance"]["series"] == [
        {
            "runId": "alpha_20260405_100000",
            "label": "Alpha Strategy",
            "points": [
                {"date": "2024-01-02", "value": 100.0},
                {"date": "2024-01-03", "value": 110.0},
            ],
        }
    ]
    assert payload["performance"]["benchmark"] == [
        {"date": "2024-01-02", "value": 100.0},
        {"date": "2024-01-03", "value": 100.49999999999999},
    ]
    assert payload["performance"]["drawdowns"] == [
        {
            "runId": "alpha_20260405_100000",
            "label": "Alpha Strategy",
            "points": [
                {"date": "2024-01-02", "value": 0.0},
                {"date": "2024-01-03", "value": 0.0},
            ],
        }
    ]
    assert payload["rolling"] == {"rollingSharpe": [], "rollingBeta": []}
    assert payload["exposure"]["holdingsCount"] == [
        {
            "runId": "alpha_20260405_100000",
            "label": "Alpha Strategy",
            "points": [
                {"date": "2024-01-02", "value": 2.0},
                {"date": "2024-01-03", "value": 2.0},
            ],
        }
    ]
    assert payload["exposure"]["latestHoldings"] == {
        "alpha_20260405_100000": [
            {"symbol": "A", "targetWeight": 0.55, "absWeight": 0.55},
            {"symbol": "B", "targetWeight": 0.45, "absWeight": 0.45},
        ]
    }
    assert payload["exposure"]["sectorWeights"] == {
        "alpha_20260405_100000": [
            {"name": "Tech", "value": 0.55},
            {"name": "Utilities", "value": 0.45},
        ]
    }


def test_dashboard_returns_multi_mode_payload_for_repeated_run_ids(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=110.0,
        avg_turnover=0.03,
        weights=[[0.6, 0.4, 0.0], [0.55, 0.45, 0.0]],
    )
    _write_saved_run(
        tmp_path,
        "omega_20260405_110000",
        name="Omega Strategy",
        final_equity=120.0,
        avg_turnover=0.04,
        weights=[[0.3, 0.4, 0.3], [0.2, 0.5, 0.3]],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get(
        "/api/dashboard",
        params=[("run_ids", "omega_20260405_110000"), ("run_ids", "omega_20260405_110000")],
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "single"
    assert payload["selectedRunIds"] == ["omega_20260405_110000"]
    assert set(payload["metrics"]) == {"omega_20260405_110000"}
    assert set(payload["context"]) == {"omega_20260405_110000"}
    assert payload["performance"]["benchmark"] == [
        {"date": "2024-01-02", "value": 100.0},
        {"date": "2024-01-03", "value": 100.49999999999999},
    ]
    assert {entry["runId"] for entry in payload["performance"]["series"]} == {"omega_20260405_110000"}
    assert {entry["runId"] for entry in payload["performance"]["drawdowns"]} == {"omega_20260405_110000"}
    assert {entry["runId"] for entry in payload["rolling"]["rollingSharpe"]} == set()
    assert {entry["runId"] for entry in payload["exposure"]["holdingsCount"]} == {"omega_20260405_110000"}
    assert set(payload["exposure"]["latestHoldings"]) == {"omega_20260405_110000"}
    assert set(payload["exposure"]["sectorWeights"]) == {"omega_20260405_110000"}
    assert payload["exposure"]["latestHoldings"]["omega_20260405_110000"] == [
        {"symbol": "B", "targetWeight": 0.5, "absWeight": 0.5},
        {"symbol": "C", "targetWeight": 0.3, "absWeight": 0.3},
        {"symbol": "A", "targetWeight": 0.2, "absWeight": 0.2},
    ]


def test_dashboard_skips_non_finite_latest_holdings_values(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=110.0,
        avg_turnover=0.03,
        weights=[[0.6, 0.4, 0.0], [0.55, 0.45, 0.0]],
        latest_weights_rows=[
            {"symbol": "A", "target_weight": 0.55, "abs_weight": 0.55},
            {"symbol": "B", "target_weight": float("nan"), "abs_weight": float("nan")},
        ],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["exposure"]["latestHoldings"] == {
        "alpha_20260405_100000": [
            {"symbol": "A", "targetWeight": 0.55, "absWeight": 0.55},
        ]
    }


def test_dashboard_skips_non_finite_sector_weights_values(tmp_path: Path) -> None:
    _write_saved_run(
        tmp_path,
        "alpha_20260405_100000",
        name="Alpha Strategy",
        final_equity=110.0,
        avg_turnover=0.03,
        weights=[[0.6, 0.4, 0.0], [0.55, 0.45, 0.0]],
    )

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(
        tmp_path,
        sector_frame=pd.DataFrame(
            {"A": ["Tech"], "B": ["Utilities"], "C": [float("nan")]},
            index=pd.to_datetime(["2024-01-03"]),
        ),
    )

    response = client.get("/api/dashboard", params=[("run_ids", "alpha_20260405_100000")])

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["exposure"]["sectorWeights"] == {
        "alpha_20260405_100000": [
            {"name": "Tech", "value": 0.55},
            {"name": "Utilities", "value": 0.45},
        ]
    }


def test_dashboard_returns_controlled_error_for_non_directory_run_entry(tmp_path: Path) -> None:
    (tmp_path / "broken_20260405_120000").write_text("not a directory", encoding="utf-8")

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "broken_20260405_120000")])

    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json() == {"detail": "unknown run_id: broken_20260405_120000"}


def test_dashboard_returns_controlled_error_for_unreadable_run_directory(tmp_path: Path) -> None:
    _write_incomplete_run(tmp_path, "broken_20260405_130000")

    client = TestClient(app)
    app.dependency_overrides[get_dashboard_payload_service] = lambda: _build_payload_service(tmp_path)

    response = client.get("/api/dashboard", params=[("run_ids", "broken_20260405_130000")])

    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert response.json()["detail"].startswith("unable to read run_id: broken_20260405_130000")


def _build_payload_service(runs_root: Path, sector_frame: pd.DataFrame | None = None) -> DashboardPayloadService:
    if sector_frame is None:
        sector_frame = pd.DataFrame(
            {"A": ["Tech"], "B": ["Utilities"], "C": ["Health Care"]},
            index=pd.to_datetime(["2024-01-03"]),
        )
    return DashboardPayloadService(
        runs_root=runs_root,
        run_index_service=RunIndexService(runs_root),
        snapshot_factory=PerformanceSnapshotFactory(
            benchmark_repo=BenchmarkRepository.from_frame(
                pd.DataFrame(
                    {"IKS200": [200.0, 201.0]},
                    index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
                )
            ),
            sector_repo=SectorRepository.from_frame(sector_frame),
        ),
    )


def _write_saved_run(
    root: Path,
    run_id: str,
    *,
    name: str,
    final_equity: float,
    avg_turnover: float,
    weights: list[list[float]],
    latest_weights_rows: list[dict[str, object]] | None = None,
) -> None:
    run_dir = root / run_id
    series_dir = run_dir / "series"
    positions_dir = run_dir / "positions"
    series_dir.mkdir(parents=True)
    positions_dir.mkdir()

    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "name": name,
                "strategy": "momentum",
                "start": "2024-01-02",
                "end": "2024-01-03",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps({"final_equity": final_equity, "avg_turnover": avg_turnover}),
        encoding="utf-8",
    )

    dates = pd.to_datetime(["2024-01-02", "2024-01-03"])
    equity = pd.Series([100.0, final_equity], index=dates, name="equity")
    returns = equity.pct_change().fillna(0.0).rename("returns")
    turnover = pd.Series([0.02, avg_turnover * 2 - 0.02], index=dates, name="turnover")
    weights_frame = pd.DataFrame(weights, columns=["A", "B", "C"], index=dates)
    qty_frame = weights_frame.mul(10.0)

    equity.to_csv(series_dir / "equity.csv", index_label="date")
    returns.to_csv(series_dir / "returns.csv", index_label="date")
    turnover.to_csv(series_dir / "turnover.csv", index_label="date")
    weights_frame.to_parquet(positions_dir / "weights.parquet")
    qty_frame.to_parquet(positions_dir / "qty.parquet")
    if latest_weights_rows is not None:
        pd.DataFrame(latest_weights_rows).to_csv(positions_dir / "latest_weights.csv", index=False)


def _write_incomplete_run(root: Path, run_id: str) -> None:
    run_dir = root / run_id
    series_dir = run_dir / "series"
    positions_dir = run_dir / "positions"
    series_dir.mkdir(parents=True)
    positions_dir.mkdir()

    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "name": "Broken Strategy",
                "strategy": "momentum",
                "start": "2024-01-02",
                "end": "2024-01-03",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps({"final_equity": 100.0, "avg_turnover": 0.01}),
        encoding="utf-8",
    )
