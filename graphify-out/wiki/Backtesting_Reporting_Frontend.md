# Backtesting Reporting Frontend

> 180 nodes · cohesion 0.02

## Key Concepts

- **Shares Outstanding Outstanding** (75 connections) — `raw/qw_sha_out.csv`
- **Equity Latest Quarter** (66 connections) — `raw/qw_equity_lfq0.csv`
- **Wics Sector Sector Large Cap Sector** (61 connections) — `raw/qw_wics_sec_big.csv`
- **Foreign Ownership Ratio** (52 connections) — `raw/qw_foreign_ratio.csv`
- **Map** (44 connections) — `raw/map.xlsx`
- **Options Div** (44 connections) — `raw/options/qw_div.csv`
- **Kospi200 1M** (31 connections) — `raw/KOSPI200_1M.csv`
- **Assets Latest Quarter** (31 connections) — `raw/qw_asset_lfq0.csv`
- **PerformanceSnapshotFactory** (28 connections) — `backtesting/reporting/snapshots.py`
- **PerformanceStrip.tsx** (28 connections) — `dashboard/frontend/src/components/PerformanceStrip.tsx`
- **models.py** (27 connections) — `backtesting/reporting/models.py`
- **ResearchDetailPanel.tsx** (27 connections) — `dashboard/frontend/src/components/ResearchDetailPanel.tsx`
- **snapshots.py** (26 connections) — `backtesting/reporting/snapshots.py`
- **analytics.py** (25 connections) — `backtesting/reporting/analytics.py`
- **Options Implied Vol** (23 connections) — `raw/options/qw_implied_vol.csv`
- **test_builder.py** (22 connections) — `tests/reporting/test_builder.py`
- **tables_single.py** (19 connections) — `backtesting/reporting/tables_single.py`
- **dashboard_payload.py** (19 connections) — `dashboard/backend/services/dashboard_payload.py`
- **test_figures.py** (17 connections) — `tests/reporting/test_figures.py`
- **test_reader.py** (16 connections) — `tests/reporting/test_reader.py`
- **ExposureBand.tsx** (15 connections) — `dashboard/frontend/src/components/ExposureBand.tsx`
- **tables_comparison.py** (14 connections) — `backtesting/reporting/tables_comparison.py`
- **strategies.py** (14 connections) — `dashboard/strategies.py`
- **test_tables.py** (14 connections) — `tests/reporting/test_tables.py`
- **RunSelector.test.tsx** (13 connections) — `dashboard/frontend/src/components/RunSelector.test.tsx`
- *... and 155 more nodes in this community*

## Relationships

- [[Raw Ksdq Csv]] (144 shared connections)
- [[Backtesting Reporting Tests]] (42 shared connections)
- [[Docs Superpowers Reporting]] (39 shared connections)
- [[Tests Reporting Analytics]] (37 shared connections)
- [[Docs Superpowers Plans]] (35 shared connections)
- [[Tests Dashboard Backend]] (35 shared connections)
- [[Docs Superpowers Kosdaq150]] (28 shared connections)
- [[Dashboard Frontend App]] (24 shared connections)
- [[Backtesting Reporting Composers]] (23 shared connections)
- [[Dashboard Backend Schemas]] (16 shared connections)
- [[Docs Superpowers Performance]] (14 shared connections)
- [[Dashboard Frontend Src]] (14 shared connections)

## Source Files

- `backtesting/construction/__init__.py`
- `backtesting/reporting/__init__.py`
- `backtesting/reporting/analytics.py`
- `backtesting/reporting/builder.py`
- `backtesting/reporting/comparison_figures.py`
- `backtesting/reporting/figures.py`
- `backtesting/reporting/models.py`
- `backtesting/reporting/plots.py`
- `backtesting/reporting/reader.py`
- `backtesting/reporting/snapshots.py`
- `backtesting/reporting/tables_comparison.py`
- `backtesting/reporting/tables_single.py`
- `backtesting/reporting/writer.py`
- `backtesting/types.py`
- `backtesting/validation/session.py`
- `dashboard/backend/services/dashboard_payload.py`
- `dashboard/backend/services/run_index.py`
- `dashboard/frontend/src/components/DiagnosticStrip.tsx`
- `dashboard/frontend/src/components/EmptyState.tsx`
- `dashboard/frontend/src/components/ExposureBand.tsx`

## Audit Trail

- EXTRACTED: 416 (33%)
- INFERRED: 829 (67%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*