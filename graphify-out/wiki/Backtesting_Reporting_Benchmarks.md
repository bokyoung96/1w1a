# Backtesting Reporting Benchmarks

> 32 nodes · cohesion 0.11

## Key Concepts

- **SectorRepository** (17 connections) — `backtesting/reporting/benchmarks.py`
- **benchmarks.py** (15 connections) — `backtesting/reporting/benchmarks.py`
- **BenchmarkRepository** (9 connections) — `backtesting/reporting/benchmarks.py`
- **default_repositories_for_universe()** (7 connections) — `backtesting/reporting/benchmarks.py`
- **KOSDAQ GICS Sector History** (6 connections) — `raw/snp_ksdq_gics_sector_big.xlsx`
- **KOSDAQ GICS Sector Mapping** (5 connections) — `raw/snp_ksdq_gics_sector_latest.md`
- **BenchmarkSeries** (4 connections) — `backtesting/reporting/benchmarks.py`
- **default()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **_load_default_frame()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **_load_display_name_maps()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **_normalize_symbol_key()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **.from_historical_excel()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **._group_row_by_sector()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **._latest_aligned_weights()** (4 connections) — `backtesting/reporting/benchmarks.py`
- **.load_series()** (3 connections) — `backtesting/reporting/benchmarks.py`
- **.latest_sector_row()** (3 connections) — `backtesting/reporting/benchmarks.py`
- **.load_returns()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **from_frame()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **_read_historical_sector_frame()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **_read_quantwise_benchmark_frame()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **.display_symbol()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **.__init__()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **.latest_sector_counts()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **.latest_sector_weights()** (2 connections) — `backtesting/reporting/benchmarks.py`
- **.sector_contribution_timeseries()** (2 connections) — `backtesting/reporting/benchmarks.py`
- *... and 7 more nodes in this community*

## Relationships

- [[Backtesting Reporting Snapshots]] (5 shared connections)
- [[Backtesting Reporting Builder]] (4 shared connections)
- [[Dashboard Backend Services]] (3 shared connections)
- [[Backtesting Strategy Catalog]] (3 shared connections)

## Source Files

- `backtesting/reporting/benchmarks.py`
- `raw/snp_ksdq_gics_sector_big.xlsx`
- `raw/snp_ksdq_gics_sector_big_pivot.csv`
- `raw/snp_ksdq_gics_sector_latest.md`
- `raw/snp_ksdq_gics_sector_membership.md`

## Audit Trail

- EXTRACTED: 105 (83%)
- INFERRED: 22 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*