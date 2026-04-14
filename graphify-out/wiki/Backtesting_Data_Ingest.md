# Backtesting Data Ingest

> 29 nodes · cohesion 0.09

## Key Concepts

- **ParquetStore** (8 connections) — `backtesting/data/store.py`
- **DataLoader** (6 connections) — `backtesting/data/loader.py`
- **pipeline.py** (5 connections) — `backtesting/ingest/pipeline.py`
- **IngestJob** (5 connections) — `backtesting/ingest/pipeline.py`
- **loader.py** (4 connections) — `backtesting/data/loader.py`
- **report.py** (4 connections) — `backtesting/ingest/report.py`
- **MarketData** (4 connections) — `backtesting/data/loader.py`
- **IngestResult** (4 connections) — `backtesting/ingest/report.py`
- **__init__.py** (3 connections) — `backtesting/data/__init__.py`
- **io.py** (3 connections) — `backtesting/ingest/io.py`
- **.load()** (3 connections) — `backtesting/data/loader.py`
- **LoadRequest** (3 connections) — `backtesting/data/loader.py`
- **policy.py** (2 connections) — `backtesting/data/policy.py`
- **store.py** (2 connections) — `backtesting/data/store.py`
- **__init__.py** (2 connections) — `backtesting/ingest/__init__.py`
- **normalize.py** (2 connections) — `backtesting/ingest/normalize.py`
- **._load_frame()** (2 connections) — `backtesting/data/loader.py`
- **.to_dict()** (2 connections) — `backtesting/ingest/report.py`
- **.write_json()** (2 connections) — `backtesting/ingest/report.py`
- **find_raw_path()** (1 connections) — `backtesting/ingest/io.py`
- **read_raw_frame()** (1 connections) — `backtesting/ingest/io.py`
- **.__init__()** (1 connections) — `backtesting/data/loader.py`
- **normalize_frame()** (1 connections) — `backtesting/ingest/normalize.py`
- **.run()** (1 connections) — `backtesting/ingest/pipeline.py`
- **expand_monthly_frame()** (1 connections) — `backtesting/data/policy.py`
- *... and 4 more nodes in this community*

## Relationships

- [[Backtesting Strategy Catalog]] (4 shared connections)

## Source Files

- `backtesting/data/__init__.py`
- `backtesting/data/loader.py`
- `backtesting/data/policy.py`
- `backtesting/data/store.py`
- `backtesting/ingest/__init__.py`
- `backtesting/ingest/io.py`
- `backtesting/ingest/normalize.py`
- `backtesting/ingest/pipeline.py`
- `backtesting/ingest/report.py`

## Audit Trail

- EXTRACTED: 62 (82%)
- INFERRED: 14 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*