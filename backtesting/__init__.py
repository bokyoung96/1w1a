from __future__ import annotations

from importlib import import_module

__all__ = (
    "BacktestEngine",
    "BacktestResult",
    "BaseStrategy",
    "MomentumTopN",
    "OpFwdYieldTopN",
    "CostModel",
    "CrossSectionalStrategy",
    "CustomSchedule",
    "DataCatalog",
    "DataLoader",
    "DailySchedule",
    "DatasetGroup",
    "DatasetGroups",
    "DatasetId",
    "DatasetSpec",
    "LoadRequest",
    "MarketData",
    "MonthlySchedule",
    "ParquetStore",
    "RankLongOnly",
    "RankLongShort",
    "RebalanceSchedule",
    "RegisteredStrategy",
    "ReportBuilder",
    "ReportBundle",
    "ReportSpec",
    "RunReader",
    "RunWriter",
    "SplitConfig",
    "SplitResult",
    "ThresholdTrend",
    "TimeSeriesStrategy",
    "TradeCost",
    "ValidationSession",
    "WeeklySchedule",
    "build_strategy",
    "expand_monthly_frame",
    "fill_prices",
    "list_strategies",
    "quantile_returns",
    "rank_ic",
    "register_strategy",
    "split_frame",
    "summarize_perf",
)

_EXPORTS: dict[str, tuple[str, str]] = {
    "quantile_returns": (".analytics", "quantile_returns"),
    "rank_ic": (".analytics", "rank_ic"),
    "summarize_perf": (".analytics", "summarize_perf"),
    "DataCatalog": (".catalog", "DataCatalog"),
    "DatasetGroup": (".catalog", "DatasetGroup"),
    "DatasetGroups": (".catalog", "DatasetGroups"),
    "DatasetId": (".catalog", "DatasetId"),
    "DatasetSpec": (".catalog", "DatasetSpec"),
    "DataLoader": (".data", "DataLoader"),
    "LoadRequest": (".data", "LoadRequest"),
    "MarketData": (".data", "MarketData"),
    "ParquetStore": (".data", "ParquetStore"),
    "expand_monthly_frame": (".data", "expand_monthly_frame"),
    "BacktestEngine": (".engine", "BacktestEngine"),
    "BacktestResult": (".engine", "BacktestResult"),
    "CostModel": (".execution", "CostModel"),
    "CustomSchedule": (".execution", "CustomSchedule"),
    "DailySchedule": (".execution", "DailySchedule"),
    "MonthlySchedule": (".execution", "MonthlySchedule"),
    "RebalanceSchedule": (".execution", "RebalanceSchedule"),
    "TradeCost": (".execution", "TradeCost"),
    "WeeklySchedule": (".execution", "WeeklySchedule"),
    "fill_prices": (".execution", "fill_prices"),
    "ReportBuilder": (".reporting", "ReportBuilder"),
    "ReportBundle": (".reporting", "ReportBundle"),
    "ReportSpec": (".reporting", "ReportSpec"),
    "RunReader": (".reporting", "RunReader"),
    "RunWriter": (".reporting", "RunWriter"),
    "BaseStrategy": (".strategy", "BaseStrategy"),
    "CrossSectionalStrategy": (".strategy", "CrossSectionalStrategy"),
    "RankLongOnly": (".strategy", "RankLongOnly"),
    "RankLongShort": (".strategy", "RankLongShort"),
    "ThresholdTrend": (".strategy", "ThresholdTrend"),
    "TimeSeriesStrategy": (".strategy", "TimeSeriesStrategy"),
    "MomentumTopN": (".strategies", "MomentumTopN"),
    "OpFwdYieldTopN": (".strategies", "OpFwdYieldTopN"),
    "RegisteredStrategy": (".strategies", "RegisteredStrategy"),
    "build_strategy": (".strategies", "build_strategy"),
    "list_strategies": (".strategies", "list_strategies"),
    "register_strategy": (".strategies", "register_strategy"),
    "SplitConfig": (".validation", "SplitConfig"),
    "SplitResult": (".validation", "SplitResult"),
    "ValidationSession": (".validation", "ValidationSession"),
    "split_frame": (".validation", "split_frame"),
}


def __getattr__(name: str):
    try:
        module_name, attr_name = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
