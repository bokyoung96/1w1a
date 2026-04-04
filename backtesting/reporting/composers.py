from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .models import ComparisonBundle, TearsheetBundle

__all__ = (
    "ComparisonComposer",
    "ComparisonRenderContext",
    "PageContext",
    "TableContext",
    "TearsheetComposer",
    "TearsheetRenderContext",
)

_TABLE_TITLES = {
    "performance_summary": "Performance Summary",
    "drawdown_episodes": "Worst Drawdowns",
    "top_holdings": "Top Holdings",
    "sector_weights": "Sector Weights",
    "validation_appendix": "Validation Appendix",
    "ranked_summary": "Ranked Summary",
    "benchmark_relative": "Benchmark Relative Metrics",
    "exposure_summary": "Holdings And Turnover",
    "sector_summary": "Sector Comparison",
}
_PAGE_TITLES = {
    "executive": "Executive Overview",
    "rolling": "Rolling Diagnostics",
    "calendar": "Return Shape",
    "exposure": "Holdings And Sectors",
    "performance": "Performance Comparison",
}
_PERCENT_COLUMNS = {
    "cagr",
    "cumulative_return",
    "annual_volatility",
    "max_drawdown",
    "avg_turnover",
    "alpha",
    "tracking_error",
    "weight",
    "top_sector_weight",
    "drawdown",
    "target_weight",
    "abs_weight",
}
_NUMBER_COLUMNS = {"beta", "sharpe", "sortino", "calmar", "information_ratio"}
_INTEGER_COLUMNS = {"count", "holdings_count", "duration_days", "recovery_days"}
_MONEY_COLUMNS = {"final_equity"}
_PERCENT_METRICS = {
    "Cumulative Return",
    "CAGR",
    "Volatility",
    "Max Drawdown",
    "Avg Turnover",
    "Alpha",
    "Tracking Error",
}
_NUMBER_METRICS = {"Sharpe", "Sortino", "Calmar", "Beta", "Information Ratio"}
_MONEY_METRICS = {"Final Equity"}


@dataclass(frozen=True, slots=True)
class PageContext:
    key: str
    title: str
    path: str


@dataclass(frozen=True, slots=True)
class TableContext:
    key: str
    title: str
    columns: tuple[str, ...]
    rows: tuple[dict[str, str], ...]


@dataclass(frozen=True, slots=True)
class TearsheetRenderContext:
    title: str
    report_name: str
    display_name: str
    benchmark_name: str
    metric_cards: tuple[dict[str, str], ...]
    pages: tuple[PageContext, ...]
    tables: tuple[TableContext, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ComparisonRenderContext:
    title: str
    report_name: str
    benchmark_name: str
    participants: tuple[str, ...]
    metric_cards: tuple[dict[str, str], ...]
    pages: tuple[PageContext, ...]
    tables: tuple[TableContext, ...]
    notes: tuple[str, ...]


class TearsheetComposer:
    def compose(self, bundle: TearsheetBundle) -> TearsheetRenderContext:
        summary = bundle.tables.get("performance_summary", pd.DataFrame())
        return TearsheetRenderContext(
            title=bundle.spec.title or bundle.display_name,
            report_name=bundle.spec.name,
            display_name=bundle.display_name,
            benchmark_name=bundle.spec.benchmark.name,
            metric_cards=_metric_cards(summary),
            pages=_page_contexts(bundle.pages, bundle.out_dir),
            tables=_table_contexts(bundle.tables),
            notes=bundle.notes,
        )


class ComparisonComposer:
    def compose(self, bundle: ComparisonBundle) -> ComparisonRenderContext:
        ranked = bundle.tables.get("ranked_summary", pd.DataFrame())
        return ComparisonRenderContext(
            title=bundle.spec.title or bundle.spec.name,
            report_name=bundle.spec.name,
            benchmark_name=bundle.spec.benchmark.name,
            participants=bundle.display_names,
            metric_cards=_comparison_metric_cards(ranked),
            pages=_page_contexts(bundle.pages, bundle.out_dir),
            tables=_table_contexts(bundle.tables),
            notes=bundle.notes,
        )


def _comparison_metric_cards(frame: pd.DataFrame) -> tuple[dict[str, str], ...]:
    if frame.empty:
        return ()
    leader = frame.iloc[0]
    cards = [
        {"label": "Top CAGR", "value": f'{leader["display_name"]} · {_format_value("cagr", leader.get("cagr"))}'}
    ]
    if "sharpe" in leader.index:
        cards.append(
            {"label": "Top Sharpe", "value": f'{leader["display_name"]} · {_format_value("sharpe", leader.get("sharpe"))}'}
        )
    return tuple(cards)


def _metric_cards(frame: pd.DataFrame) -> tuple[dict[str, str], ...]:
    if frame.empty:
        return ()
    cards: list[dict[str, str]] = []
    for row in frame.head(8).to_dict(orient="records"):
        label = str(row.get("metric", ""))
        cards.append({"label": label, "value": _format_metric_value(label, row.get("value"))})
    return tuple(cards)


def _page_contexts(pages: dict[str, Path], out_dir: Path) -> tuple[PageContext, ...]:
    items: list[PageContext] = []
    for key, path in pages.items():
        items.append(
            PageContext(
                key=key,
                title=_PAGE_TITLES.get(key, key.replace("_", " ").title()),
                path=os.path.relpath(path, out_dir).replace(os.sep, "/"),
            )
        )
    return tuple(items)


def _table_contexts(tables: dict[str, pd.DataFrame]) -> tuple[TableContext, ...]:
    items: list[TableContext] = []
    for key, frame in tables.items():
        rows = tuple(
            {
                str(column): _format_table_cell(key, row, str(column), value)
                for column, value in row.items()
            }
            for row in frame.to_dict(orient="records")
        )
        items.append(
            TableContext(
                key=key,
                title=_TABLE_TITLES.get(key, key.replace("_", " ").title()),
                columns=tuple(str(column) for column in frame.columns),
                rows=rows,
            )
        )
    return tuple(items)


def _format_table_cell(table_key: str, row: dict[str, object], column: str, value: object) -> str:
    if table_key == "performance_summary" and column == "value":
        return _format_metric_value(str(row.get("metric", "")), value)
    return _format_value(column, value)


def _format_metric_value(metric: str, value: object) -> str:
    label = metric.strip()
    if label in _PERCENT_METRICS:
        return _format_value("cagr", value)
    if label in _NUMBER_METRICS:
        return _format_value("sharpe", value)
    if label in _MONEY_METRICS:
        return _format_value("final_equity", value)
    return _format_value("value", value)


def _format_value(column: str, value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "isoformat") and not isinstance(value, (str, bytes, int, float)):
        try:
            return value.isoformat()
        except TypeError:
            pass
    if isinstance(value, str):
        return value

    numeric = float(value)
    name = column.strip().lower()
    if name in _PERCENT_COLUMNS:
        return f"{numeric:.1%}"
    if name in _NUMBER_COLUMNS:
        return f"{numeric:.2f}"
    if name in _INTEGER_COLUMNS:
        return f"{int(round(numeric)):,}"
    if name in _MONEY_COLUMNS:
        return f"{numeric:,.0f}"
    return f"{numeric:,.2f}"
