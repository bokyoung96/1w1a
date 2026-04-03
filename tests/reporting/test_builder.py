from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from backtesting.reporting.builder import ReportBuilder
from backtesting.reporting.models import ReportSpec, SavedRun
from backtesting.reporting.tables import build_appendix_table, build_summary_table


def test_report_builder_assembles_bundle_and_persists_tables(tmp_path: Path, monkeypatch) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    run = SavedRun(
        run_id="sample",
        path=tmp_path / "sample",
        config={"strategy": "momentum", "start": "2024-01-02", "end": "2024-01-03"},
        summary={"cagr": 0.1, "mdd": -0.2, "sharpe": 1.0, "final_equity": 110.0, "avg_turnover": 0.05},
        equity=pd.Series([100.0, 110.0], index=index),
        returns=pd.Series([0.0, 0.1], index=index),
        turnover=pd.Series([0.0, 0.05], index=index),
        weights=pd.DataFrame({"A": [1.0, 1.0]}, index=index),
        qty=pd.DataFrame({"A": [10.0, 10.0]}, index=index),
    )

    plot_dir = tmp_path / "sample-report" / "plots"
    plot_paths = {
        "equity": plot_dir / "equity.png",
        "drawdown": plot_dir / "drawdown.png",
        "turnover": plot_dir / "turnover.png",
        "top_weights": plot_dir / "top_weights.png",
        "monthly_heatmap": plot_dir / "monthly_heatmap.png",
    }

    def _make_plotter(method_name: str):
        def _plot(self, runs, *, require_png=False):  # type: ignore[no-untyped-def]
            path = plot_paths[method_name]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(method_name, encoding="utf-8")
            return path

        return _plot

    for method_name in plot_paths:
        monkeypatch.setattr(
            "backtesting.reporting.plots.PlotLibrary." + method_name,
            _make_plotter(method_name),
        )

    bundle = ReportBuilder(tmp_path).build(ReportSpec(name="sample-report", run_ids=("sample",)), [run])

    assert bundle.spec.name == "sample-report"
    assert bundle.out_dir == tmp_path / "sample-report"
    assert bundle.runs == (run,)
    assert_frame_equal(bundle.summary, build_summary_table([run]))
    assert_frame_equal(bundle.appendix, build_appendix_table([run]))
    assert bundle.plots == plot_paths
    assert bundle.notes == (
        "missing_validation:sample",
        "missing_split:sample",
        "missing_factor:sample",
    )

    tables_dir = bundle.out_dir / "tables"
    assert (tables_dir / "summary.csv").exists()
    assert (tables_dir / "appendix.csv").exists()
    assert (tables_dir / "sample_latest_weights.csv").exists()
    assert (tables_dir / "sample_latest_qty.csv").exists()

