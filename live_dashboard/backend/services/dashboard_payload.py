from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from backtesting.reporting.benchmarks import BenchmarkRepository, SectorRepository
from backtesting.reporting.models import BenchmarkConfig, SavedRun
from backtesting.reporting.reader import RunReader
from backtesting.reporting.snapshots import PerformanceSnapshot, PerformanceSnapshotFactory
from live_dashboard.backend.schemas import (
    BenchmarkModel,
    DashboardContextModel,
    DashboardExposureModel,
    DashboardMetricModel,
    DashboardPayloadModel,
    DashboardPerformanceModel,
    DashboardRollingModel,
)
from live_dashboard.backend.serializers import (
    serialize_latest_holdings,
    serialize_named_series,
    serialize_named_values,
    serialize_value_points,
)
from live_dashboard.backend.services.run_index import RunIndexService
from root import ROOT


class DashboardPayloadService:
    def __init__(
        self,
        runs_root: Path | None = None,
        *,
        run_index_service: RunIndexService | None = None,
        run_reader: RunReader | None = None,
        snapshot_factory: PerformanceSnapshotFactory | None = None,
    ) -> None:
        self.runs_root = runs_root or (ROOT.results_path / "backtests")
        self.run_index_service = run_index_service or RunIndexService(self.runs_root)
        self.run_reader = run_reader or RunReader()
        self.snapshot_factory = snapshot_factory or PerformanceSnapshotFactory(
            benchmark_repo=BenchmarkRepository.default(),
            sector_repo=SectorRepository.default(),
        )
        self.benchmark = BenchmarkConfig.default_kospi200()

    def build(self, run_ids: list[str]) -> DashboardPayloadModel:
        selected_runs = [self._read_run(run_id) for run_id in run_ids]
        snapshots = [self.snapshot_factory.build(run, self.benchmark) for run in selected_runs]

        return DashboardPayloadModel(
            mode="single" if len(run_ids) == 1 else "multi",
            selected_run_ids=run_ids,
            available_runs=self.run_index_service.list_runs(),
            metrics={snapshot.run_id: self._serialize_metrics(snapshot) for snapshot in snapshots},
            context={snapshot.run_id: self._serialize_context(snapshot) for snapshot in snapshots},
            performance=DashboardPerformanceModel(
                series=[self._serialize_series(snapshot, snapshot.strategy_equity) for snapshot in snapshots],
                benchmark=serialize_value_points(snapshots[0].benchmark_equity) if len(snapshots) == 1 else None,
                drawdowns=[self._serialize_series(snapshot, snapshot.drawdowns.underwater) for snapshot in snapshots],
            ),
            rolling=DashboardRollingModel(
                rolling_sharpe=self._serialize_rolling_series(snapshots, "rolling_sharpe"),
                rolling_beta=self._serialize_rolling_series(snapshots, "rolling_beta"),
            ),
            exposure=DashboardExposureModel(
                holdings_count=[self._serialize_series(snapshot, snapshot.exposure.holdings_count) for snapshot in snapshots],
                latest_holdings={
                    snapshot.run_id: serialize_latest_holdings(snapshot.exposure.latest_holdings) for snapshot in snapshots
                },
                sector_weights={
                    snapshot.run_id: serialize_named_values(snapshot.sectors.latest_weighted) for snapshot in snapshots
                },
            ),
        )

    def _read_run(self, run_id: str) -> SavedRun:
        run_dir = self.runs_root / run_id
        if not run_dir.exists():
            raise HTTPException(status_code=404, detail=f"unknown run_id: {run_id}")
        return self.run_reader.read(run_dir)

    def _serialize_context(self, snapshot: PerformanceSnapshot) -> DashboardContextModel:
        run = self._read_run(snapshot.run_id)
        return DashboardContextModel(
            label=snapshot.display_name,
            strategy=str(run.config.get("strategy") or "unknown"),
            benchmark=BenchmarkModel(code=self.benchmark.code, name=self.benchmark.name),
            start_date=snapshot.strategy_equity.index.min().date().isoformat(),
            end_date=snapshot.strategy_equity.index.max().date().isoformat(),
            as_of_date=snapshot.strategy_equity.index.max().date().isoformat(),
        )

    @staticmethod
    def _serialize_metrics(snapshot: PerformanceSnapshot) -> DashboardMetricModel:
        metrics = snapshot.metrics
        return DashboardMetricModel(
            label=snapshot.display_name,
            cumulative_return=metrics.cumulative_return,
            cagr=metrics.cagr,
            annual_volatility=metrics.annual_volatility,
            sharpe=metrics.sharpe,
            sortino=metrics.sortino,
            calmar=metrics.calmar,
            max_drawdown=metrics.max_drawdown,
            final_equity=metrics.final_equity,
            avg_turnover=metrics.avg_turnover,
            alpha=metrics.alpha,
            beta=metrics.beta,
            tracking_error=metrics.tracking_error,
            information_ratio=metrics.information_ratio,
        )

    @staticmethod
    def _serialize_series(snapshot: PerformanceSnapshot, series: object) -> object:
        return serialize_named_series(
            series,
            run_id=snapshot.run_id,
            label=snapshot.display_name,
        )

    @staticmethod
    def _serialize_rolling_series(snapshots: list[PerformanceSnapshot], name: str) -> list[object]:
        return [
            serialize_named_series(
                snapshot.rolling.series[name],
                run_id=snapshot.run_id,
                label=snapshot.display_name,
            )
            for snapshot in snapshots
            if not snapshot.rolling.series[name].dropna().empty
        ]
