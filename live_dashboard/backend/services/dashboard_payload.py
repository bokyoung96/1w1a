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
from live_dashboard.backend.serializers import serialize_latest_holdings, serialize_named_values, serialize_series
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
            metrics=[self._serialize_metrics(snapshot) for snapshot in snapshots],
            context=self._serialize_context(snapshots),
            performance=DashboardPerformanceModel(
                strategy_equity=self._flatten_series(snapshots, "strategy_equity"),
                benchmark_equity=self._flatten_series(snapshots, "benchmark_equity"),
                strategy_returns=self._flatten_series(snapshots, "strategy_returns"),
            ),
            rolling=DashboardRollingModel(
                rolling_sharpe=self._flatten_rolling_series(snapshots, "rolling_sharpe"),
                rolling_beta=self._flatten_rolling_series(snapshots, "rolling_beta"),
            ),
            exposure=DashboardExposureModel(
                holdings_count=self._flatten_holdings_count(snapshots),
                latest_holdings={
                    snapshot.run_id: serialize_latest_holdings(snapshot.exposure.latest_holdings) for snapshot in snapshots
                },
                sector_weights={
                    snapshot.run_id: serialize_named_values(snapshot.sectors.latest_weighted) for snapshot in snapshots
                },
                sector_counts={
                    snapshot.run_id: serialize_named_values(snapshot.sectors.latest_count) for snapshot in snapshots
                },
            ),
        )

    def _read_run(self, run_id: str) -> SavedRun:
        run_dir = self.runs_root / run_id
        if not run_dir.exists():
            raise HTTPException(status_code=404, detail=f"unknown run_id: {run_id}")
        return self.run_reader.read(run_dir)

    def _serialize_context(self, snapshots: list[PerformanceSnapshot]) -> DashboardContextModel:
        start_date = min(snapshot.strategy_equity.index.min() for snapshot in snapshots)
        end_date = max(snapshot.strategy_equity.index.max() for snapshot in snapshots)
        return DashboardContextModel(
            benchmark=BenchmarkModel(code=self.benchmark.code, name=self.benchmark.name),
            start_date=start_date.date().isoformat(),
            end_date=end_date.date().isoformat(),
            as_of_date=end_date.date().isoformat(),
        )

    @staticmethod
    def _serialize_metrics(snapshot: PerformanceSnapshot) -> DashboardMetricModel:
        metrics = snapshot.metrics
        return DashboardMetricModel(
            run_id=snapshot.run_id,
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
    def _flatten_series(snapshots: list[PerformanceSnapshot], attribute: str) -> list[object]:
        points: list[object] = []
        for snapshot in snapshots:
            points.extend(
                serialize_series(
                    getattr(snapshot, attribute),
                    run_id=snapshot.run_id,
                    label=snapshot.display_name,
                )
            )
        return points

    @staticmethod
    def _flatten_rolling_series(snapshots: list[PerformanceSnapshot], name: str) -> list[object]:
        points: list[object] = []
        for snapshot in snapshots:
            points.extend(serialize_series(snapshot.rolling.series[name], run_id=snapshot.run_id, label=snapshot.display_name))
        return points

    @staticmethod
    def _flatten_holdings_count(snapshots: list[PerformanceSnapshot]) -> list[object]:
        points: list[object] = []
        for snapshot in snapshots:
            points.extend(
                serialize_series(
                    snapshot.exposure.holdings_count,
                    run_id=snapshot.run_id,
                    label=snapshot.display_name,
                )
            )
        return points
