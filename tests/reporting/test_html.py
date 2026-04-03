from pathlib import Path

import pandas as pd

from backtesting.reporting.html import HtmlRenderer
from backtesting.reporting.models import ReportBundle, ReportSpec, SavedRun


def test_html_renderer_writes_report_html(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run_dir = tmp_path / "sample"
    plot_dir = run_dir / "plots"
    plot_dir.mkdir(parents=True)
    (plot_dir / "equity.png").write_bytes(b"png")
    (plot_dir / "drawdown.png").write_bytes(b"png")
    (plot_dir / "turnover.png").write_bytes(b"png")
    (plot_dir / "monthly_heatmap.png").write_bytes(b"png")
    (plot_dir / "top_weights.png").write_bytes(b"png")

    run = SavedRun(
        run_id="sample",
        path=run_dir,
        config={"strategy": "momentum"},
        summary={"cagr": 0.1},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
        latest_weights=pd.DataFrame({"symbol": ["A"], "target_weight": [1.0]}),
        latest_qty=pd.DataFrame({"symbol": ["A"], "qty": [10.0]}),
    )
    bundle = ReportBundle(
        spec=ReportSpec(name="sample-report", run_ids=("sample",)),
        out_dir=tmp_path / "sample-report",
        runs=(run,),
        summary=pd.DataFrame([{"run_id": "sample", "cagr": 0.1}]),
        appendix=pd.DataFrame([{"run_id": "sample"}]),
        plots={"equity": plot_dir / "equity.png"},
        notes=("missing_split:sample",),
    )

    path = HtmlRenderer().render(bundle)

    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert path.parent.joinpath("styles.css").exists()
    assert "<html" in content.lower()
    assert "sample-report" in content
    assert "Executive Summary Table" in content
    assert "Performance Section" in content
    assert "Positions Section - sample" in content
    assert "Appendix Section" in content


def test_html_renderer_supports_html_plot_fallback_and_table_fallbacks(tmp_path: Path) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run_dir = tmp_path / "legacy-run"
    plot_dir = run_dir / "plots"
    plot_dir.mkdir(parents=True)
    (plot_dir / "equity.html").write_text("<html><body>plot</body></html>", encoding="utf-8")

    run = SavedRun(
        run_id="legacy-run",
        path=run_dir,
        config={"strategy": "momentum"},
        summary={"cagr": 0.1},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"B": [0.0, -0.3], "A": [0.2, 0.1]}, index=index),
        qty=pd.DataFrame({"B": [0.0, -30.0], "A": [10.0, 5.0]}, index=index),
    )
    bundle = ReportBundle(
        spec=ReportSpec(name="legacy-report", run_ids=("legacy-run",)),
        out_dir=tmp_path / "legacy-report",
        runs=(run,),
        summary=pd.DataFrame([{"run_id": "legacy-run", "cagr": 0.1}]),
        appendix=pd.DataFrame([{"run_id": "legacy-run"}]),
        plots={"equity": plot_dir / "equity.html"},
        notes=(),
    )

    path = HtmlRenderer().render(bundle)

    content = path.read_text(encoding="utf-8")
    assert '<iframe class="plot-frame"' in content
    assert "plots/equity.html" in content
    assert "abs_weight" in content
    assert "abs_qty" in content
    assert content.index(">B<") < content.index(">A<")
