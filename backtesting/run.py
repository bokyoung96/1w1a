from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from root import ROOT

from .analytics import summarize_perf
from .catalog import DataCatalog, DatasetId
from .data import DataLoader, LoadRequest, ParquetStore
from .engine import BacktestEngine, BacktestResult
from .execution import CostModel, DailySchedule, MonthlySchedule, WeeklySchedule
from .ingest import IngestJob
from .policy.base import PositionPlan
from .reporting import RunWriter
from .strategies import build_strategy, list_strategies
from .validation import validate_position_plan


@dataclass(frozen=True, slots=True)
class RunConfig:
    start: str
    end: str
    capital: float = 100_000_000.0
    strategy: str = "momentum"
    name: str | None = None
    top_n: int = 20
    lookback: int = 20
    schedule: str = "monthly"
    fill_mode: str = "next_open"
    fee: float = 0.0
    sell_tax: float = 0.0
    slippage: float = 0.0
    use_k200: bool = True
    allow_fractional: bool = True
    benchmark_code: str = "IKS200"
    benchmark_name: str = "KOSPI200"
    benchmark_dataset: str = "qw_BM"
    warmup_days: int = 0


@dataclass(slots=True)
class RunReport:
    config: RunConfig
    summary: dict[str, float]
    result: BacktestResult
    position_plan: PositionPlan | None = None
    output_dir: Path | None = None


class BacktestRunner:
    def __init__(
        self,
        *,
        catalog: DataCatalog | None = None,
        raw_dir: Path | None = None,
        parquet_dir: Path | None = None,
        result_dir: Path | None = None,
    ) -> None:
        self.catalog = catalog or DataCatalog.default()
        self.raw_dir = raw_dir or ROOT.raw_path
        self.parquet_dir = parquet_dir or ROOT.parquet_path
        self.result_dir = result_dir or (ROOT.results_path / "backtests")
        self.store = ParquetStore(self.parquet_dir)
        self.loader = DataLoader(self.catalog, self.store)
        self.ingest = IngestJob(self.catalog, self.raw_dir, self.parquet_dir)
        self.writer = RunWriter(self.result_dir)

    def run(self, config: RunConfig) -> RunReport:
        strategy = build_strategy(
            config.strategy,
            top_n=config.top_n,
            lookback=config.lookback,
        )

        dataset_ids = [DatasetId.QW_ADJ_C, *strategy.datasets]
        if config.fill_mode == "next_open":
            dataset_ids.append(DatasetId.QW_ADJ_O)
        if config.use_k200:
            dataset_ids.append(DatasetId.QW_K200_YN)
        dataset_ids = list(dict.fromkeys(dataset_ids))

        self._ensure_parquet(dataset_ids)

        market = self.loader.load(
            LoadRequest(
                datasets=dataset_ids,
                start=self._resolve_load_start(config.start, config.warmup_days),
                end=config.end,
            )
        )
        market.universe = self._universe(market, config.use_k200)

        plan = strategy.build_plan(market)
        validate_position_plan(plan)
        weights = plan.target_weights
        close = market.frames["close"]
        tradable = close.notna()
        if market.universe is not None:
            tradable = tradable & market.universe.reindex_like(close).fillna(False).astype(bool)

        engine = BacktestEngine(
            cost=CostModel(
                fee=config.fee,
                sell_tax=config.sell_tax,
                slippage=config.slippage,
            )
        )
        result = engine.run(
            close=close,
            open=market.frames.get("open"),
            weights=weights,
            capital=config.capital,
            tradable=tradable,
            schedule=self._schedule(config.schedule),
            fill_mode=config.fill_mode,
            allow_fractional=config.allow_fractional,
        )
        result = self._trim_result_to_display_range(result, start=config.start, end=config.end)
        if result.equity.empty:
            raise ValueError(
                f"no backtest rows remain after trimming to display range {config.start}..{config.end}"
            )

        summary = summarize_perf(result.returns)
        summary["final_equity"] = float(result.equity.iloc[-1])
        summary["avg_turnover"] = float(result.turnover.mean())
        report = RunReport(config=config, summary=summary, result=result, position_plan=plan)
        report.output_dir = self.writer.write(report)
        return report

    def _ensure_parquet(self, dataset_ids: list[DatasetId]) -> None:
        for dataset_id in dataset_ids:
            stem = self.catalog.get(dataset_id).stem
            path = self.parquet_dir / f"{stem}.parquet"
            if not path.exists():
                self.ingest.run(dataset_id)

    @staticmethod
    def _universe(market, use_k200: bool) -> pd.DataFrame | None:
        if not use_k200:
            return None
        if "k200_yn" not in market.frames:
            return None
        return market.frames["k200_yn"].fillna(0).astype(bool)

    @staticmethod
    def _schedule(name: str):
        if name == "daily":
            return DailySchedule()
        if name == "weekly":
            return WeeklySchedule()
        if name == "monthly":
            return MonthlySchedule()
        raise ValueError(f"unsupported schedule: {name}")

    @staticmethod
    def _resolve_load_start(start: str, warmup_days: int) -> str:
        if warmup_days <= 0:
            return start
        return (pd.Timestamp(start) - pd.Timedelta(days=warmup_days)).date().isoformat()

    @staticmethod
    def _trim_result_to_display_range(result: BacktestResult, *, start: str, end: str) -> BacktestResult:
        return BacktestResult(
            equity=result.equity.loc[start:end].copy(),
            returns=result.returns.loc[start:end].copy(),
            weights=result.weights.loc[start:end].copy(),
            qty=result.qty.loc[start:end].copy(),
            turnover=result.turnover.loc[start:end].copy(),
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run registered backtests.")
    parser.add_argument("--strategy", choices=list_strategies(), default="momentum")
    parser.add_argument("--name")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--capital", type=float, default=100_000_000.0)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--schedule", choices=("daily", "weekly", "monthly"), default="monthly")
    parser.add_argument("--fill-mode", choices=("close", "next_open"), default="next_open")
    parser.add_argument("--fee", type=float, default=0.0)
    parser.add_argument("--sell-tax", type=float, default=0.0)
    parser.add_argument("--slippage", type=float, default=0.0)
    parser.add_argument("--out-root")
    parser.add_argument("--no-k200", action="store_true")
    parser.add_argument("--no-fractional", action="store_true")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    config = RunConfig(
        start=args.start,
        end=args.end,
        capital=args.capital,
        strategy=args.strategy,
        name=args.name,
        top_n=args.top_n,
        lookback=args.lookback,
        schedule=args.schedule,
        fill_mode=args.fill_mode,
        fee=args.fee,
        sell_tax=args.sell_tax,
        slippage=args.slippage,
        use_k200=not args.no_k200,
        allow_fractional=not args.no_fractional,
    )
    runner = BacktestRunner(result_dir=Path(args.out_root) if args.out_root else None)
    report = runner.run(config)
    payload = {
        "config": asdict(report.config),
        "summary": report.summary,
        "output_dir": None if report.output_dir is None else str(report.output_dir),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(report.result.equity.tail())


if __name__ == "__main__":
    main()
