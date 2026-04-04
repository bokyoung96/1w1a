from pathlib import Path

import pandas as pd

from backtesting.reporting.html import HtmlRenderer
from backtesting.reporting.models import BenchmarkConfig, ComparisonBundle, ReportSpec, TearsheetBundle


def _write_asset(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"png")
    return path


def test_html_renderer_uses_tearsheet_template(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(
            name="single-report",
            run_ids=("run-a",),
            title="Momentum Tearsheet",
            benchmark=BenchmarkConfig.default_kospi200(),
        ),
        out_dir=tmp_path / "single-report",
        run_id="run-a",
        display_name="Momentum",
        pages={
            "executive": _write_asset(tmp_path / "single-report" / "pages" / "executive.png"),
            "rolling": _write_asset(tmp_path / "single-report" / "pages" / "rolling.png"),
        },
        tables={
            "performance_summary": pd.DataFrame([{"metric": "CAGR", "value": "17.2%"}]),
            "drawdown_episodes": pd.DataFrame([{"start": "2022-01-01", "drawdown": "-12.3%"}]),
            "top_holdings": pd.DataFrame([{"symbol": "AAA", "weight": "25.0%"}]),
            "sector_weights": pd.DataFrame([{"sector": "Tech", "weight": "40.0%"}]),
            "validation_appendix": pd.DataFrame([{"note": "missing_factor:run-a"}]),
        },
        notes=("missing_factor:run-a",),
    )

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    assert path.exists()
    assert path.parent.joinpath("styles.css").exists()
    assert "Momentum Tearsheet" in html
    assert "KOSPI200" in html
    assert "executive.png" in html
    assert "Metric Cards" in html
    assert "Top Holdings" in html


def test_html_renderer_uses_comparison_template(tmp_path: Path) -> None:
    bundle = ComparisonBundle(
        spec=ReportSpec(
            name="compare-report",
            run_ids=("run-a", "run-b"),
            title="Strategy Comparison",
            benchmark=BenchmarkConfig.default_kospi200(),
        ),
        out_dir=tmp_path / "compare-report",
        display_names=("Momentum", "OP Fwd Yield"),
        pages={
            "executive": _write_asset(tmp_path / "compare-report" / "pages" / "executive.png"),
            "performance": _write_asset(tmp_path / "compare-report" / "pages" / "performance.png"),
        },
        tables={
            "ranked_summary": pd.DataFrame([{"display_name": "Momentum", "cagr": "17.2%"}]),
            "benchmark_relative": pd.DataFrame([{"display_name": "Momentum", "alpha": "3.2%"}]),
            "exposure_summary": pd.DataFrame([{"display_name": "Momentum", "holdings_count": "20"}]),
            "sector_summary": pd.DataFrame([{"display_name": "Momentum", "top_sector": "Tech"}]),
        },
        notes=(),
    )

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    assert path.exists()
    assert "Strategy Comparison" in html
    assert "KOSPI200" in html
    assert "Momentum" in html
    assert "OP Fwd Yield" in html
    assert "performance.png" in html
    assert "Ranked Summary" in html
