from pathlib import Path

import pandas as pd

from backtesting.reporting.html import HtmlRenderer
from backtesting.reporting.models import BenchmarkConfig, ComparisonBundle, ReportBundle, ReportSpec, SavedRun, TearsheetBundle


def _write_asset(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".html":
        path.write_text("<html><body>plot</body></html>", encoding="utf-8")
    else:
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
            "performance_summary": pd.DataFrame(
                [
                    {"metric_key": "cagr", "metric": "CAGR", "value": 0.172},
                    {"metric_key": "sharpe", "metric": "Sharpe", "value": 1.1},
                    {"metric_key": "beta", "metric": "Beta", "value": 1.01},
                    {"metric_key": "final_equity", "metric": "Final Equity", "value": 1234567.0},
                ]
            ),
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
    assert "17.2%" in html
    assert "1.10" in html
    assert "1.01" in html
    assert "1,234,567" in html
    assert "110.0%" not in html
    assert "101.0%" not in html


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
            "ranked_summary": pd.DataFrame(
                [
                    {"display_name": "Momentum", "cagr": 0.172, "sharpe": 1.10},
                    {"display_name": "OP Fwd Yield", "cagr": 0.150, "sharpe": 1.35},
                ]
            ),
            "benchmark_relative": pd.DataFrame([{"display_name": "Momentum", "alpha": "3.2%"}]),
            "exposure_summary": pd.DataFrame([{"display_name": "Momentum", "holdings_count": "20"}]),
            "sector_summary": pd.DataFrame([{"display_name": "Momentum", "top_sector": "Tech"}]),
        },
        notes=("missing_split:run-b",),
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
    assert "Top CAGR" in html
    assert "Momentum · 17.2%" in html
    assert "Top Sharpe" in html
    assert "OP Fwd Yield · 1.35" in html
    assert "missing_split:run-b" in html


def test_html_renderer_keeps_legacy_reportbundle_path_styled(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="legacy-run",
        path=tmp_path / "legacy-run",
        config={"strategy": "momentum"},
        summary={"cagr": 0.1},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
    )
    plot_path = _write_asset(tmp_path / "legacy-report" / "plots" / "equity.png")
    bundle = ReportBundle(
        spec=ReportSpec(name="legacy-report", run_ids=("legacy-run",)),
        out_dir=tmp_path / "legacy-report",
        runs=(run,),
        summary=pd.DataFrame([{"run_id": "legacy-run", "cagr": 0.1}]),
        appendix=pd.DataFrame([{"run_id": "legacy-run"}]),
        plots={"equity": plot_path},
        notes=(),
    )

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    css = path.parent.joinpath("styles.css").read_text(encoding="utf-8")
    assert '<div class="plot-grid">' in html
    assert ".plot-grid" in css


def test_html_renderer_supports_html_page_asset_fallback_for_new_templates(tmp_path: Path) -> None:
    bundle = TearsheetBundle(
        spec=ReportSpec(
            name="fallback-report",
            run_ids=("run-a",),
            title="Fallback Tearsheet",
            benchmark=BenchmarkConfig.default_kospi200(),
        ),
        out_dir=tmp_path / "fallback-report",
        run_id="run-a",
        display_name="Momentum",
        pages={
            "executive": _write_asset(tmp_path / "fallback-report" / "pages" / "executive.html"),
        },
        tables={
            "performance_summary": pd.DataFrame([{"metric_key": "cagr", "metric": "CAGR", "value": 0.172}]),
            "drawdown_episodes": pd.DataFrame(),
            "top_holdings": pd.DataFrame(),
            "sector_weights": pd.DataFrame(),
            "validation_appendix": pd.DataFrame(),
        },
        notes=(),
    )

    path = HtmlRenderer().render(bundle)

    html = path.read_text(encoding="utf-8")
    assert '<iframe class="plot-frame"' in html
    assert "pages/executive.html" in html
