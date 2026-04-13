# KOSDAQ150 Universe Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first-class `kosdaq150` universe to 1w1a by registering the `qw_ksdq_*` dataset family, resolving universe-specific datasets in the backtest runner, and propagating `universe_id` through CLI, saved runs, and dashboard launch logic without breaking legacy `K200` behavior.

**Architecture:** Keep `DataCatalog` as the low-level dataset registry and add a separate `UniverseRegistry` layer that maps semantic dataset aliases like `close` and `market_cap` to concrete dataset ids such as `qw_ksdq_adj_c` and `qw_ksdq_mkcap`. `BacktestRunner` becomes the single place that resolves `universe_id` into datasets, membership masks, and default benchmark metadata, while dashboard presets and saved-run signatures carry `universe_id` as configuration only.

**Tech Stack:** Python 3.11, pandas, pytest, dataclasses, argparse, FastAPI dashboard services

---

## File Structure

- Modify: `backtesting/catalog/enums.py`
  Register `qw_ksdq_*` dataset ids.
- Modify: `backtesting/catalog/catalog.py`
  Add `DatasetSpec` entries for the KOSDAQ150 dataset family.
- Modify: `backtesting/data/loader.py`
  Add KOSDAQ semantic frame keys and extend `LoadRequest` with `universe_id`.
- Modify: `backtesting/ingest/io.py`
  Teach raw lookup to find nested files such as `raw/ksdq/qw_ksdq_adj_c.csv`.
- Create: `backtesting/universe.py`
  Define `UniverseSpec`, alias remapping, and `UniverseRegistry.default()`.
- Modify: `backtesting/__init__.py`
  Export the universe API.
- Modify: `backtesting/run.py`
  Add `RunConfig.universe_id`, optional benchmark defaults, universe-aware dataset resolution, and CLI parsing.
- Modify: `dashboard/strategies.py`
  Add `universe_id` to strategy presets.
- Modify: `dashboard/run.py`
  Pass preset `universe_id` through to `RunConfig`.
- Modify: `dashboard/backend/services/launch_resolution.py`
  Include `universe_id` in launch signatures and compat defaults.
- Modify: `dashboard/backend/services/run_index.py`
  Include `universe_id` in saved-run dedupe signatures.
- Modify: `README.md`
  Document `--universe kosdaq150`.
- Test: `tests/catalog/test_groups.py`
- Test: `tests/data/test_loader.py`
- Test: `tests/ingest/test_pipeline.py`
- Create test: `tests/data/test_universe.py`
- Test: `tests/test_run.py`
- Test: `tests/dashboard/test_run.py`
- Test: `tests/dashboard/backend/test_launch_resolution.py`
- Test: `tests/dashboard/backend/test_run_index_service.py`

### Task 1: Register KOSDAQ150 Datasets And Fix Nested Raw Ingest

**Files:**
- Modify: `backtesting/catalog/enums.py`
- Modify: `backtesting/catalog/catalog.py`
- Modify: `backtesting/data/loader.py`
- Modify: `backtesting/ingest/io.py`
- Test: `tests/catalog/test_groups.py`
- Test: `tests/data/test_loader.py`
- Test: `tests/ingest/test_pipeline.py`

- [ ] **Step 1: Write the failing catalog, loader, and ingest tests**

```python
# tests/catalog/test_groups.py
EXPECTED_RAW_STEMS = {
    # existing stems...
    "qw_ksdq150_yn",
    "qw_ksdq_adj_c",
    "qw_ksdq_adj_h",
    "qw_ksdq_adj_l",
    "qw_ksdq_adj_o",
    "qw_ksdq_mkcap",
    "qw_ksdq_mktcap_flt",
    "qw_ksdq_v",
    "qw_ksdq_wics_sec_big",
}

def test_catalog_groups_cover_known_datasets() -> None:
    catalog = DataCatalog.default()

    assert DatasetId.QW_KSDQ_ADJ_C in catalog.ids(DatasetGroup.PRICE)
    assert DatasetId.QW_KSDQ150_YN in catalog.ids(DatasetGroup.FLAG)
    assert DatasetId.QW_KSDQ_WICS_SEC_BIG in catalog.ids(DatasetGroup.META)


# tests/data/test_loader.py
def test_loader_uses_semantic_key_for_kosdaq_close_data(tmp_path: Path) -> None:
    parquet_dir = tmp_path / "parquet"
    parquet_dir.mkdir()
    store = ParquetStore(parquet_dir)
    store.write(
        "qw_ksdq_adj_c",
        pd.DataFrame({"A035720": [10.0, 11.0]}, index=pd.to_datetime(["2024-01-02", "2024-01-03"])),
    )

    loader = DataLoader(DataCatalog.default(), store)
    data = loader.load(
        LoadRequest(
            datasets=[DatasetId.QW_KSDQ_ADJ_C],
            start="2024-01-02",
            end="2024-01-03",
        )
    )

    assert "close" in data.frames
    assert "qw_ksdq_adj_c" not in data.frames
    assert list(data.frames["close"].columns) == ["A035720"]


# tests/ingest/test_pipeline.py
def test_ingest_finds_nested_raw_dataset(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    parquet_dir = tmp_path / "parquet"
    nested = raw_dir / "ksdq"
    nested.mkdir(parents=True)
    parquet_dir.mkdir()

    pd.DataFrame(
        {
            "Unnamed: 0": ["2024-01-02", "2024-01-03"],
            "A035720": [100.0, 101.0],
        }
    ).to_csv(nested / "qw_ksdq_adj_c.csv", index=False)

    job = IngestJob(DataCatalog.default(), raw_dir=raw_dir, parquet_dir=parquet_dir)

    result = job.run(DatasetId.QW_KSDQ_ADJ_C)

    assert result.rows == 2
    assert (parquet_dir / "qw_ksdq_adj_c.parquet").exists()
```

- [ ] **Step 2: Run the focused tests and confirm they fail for the expected reasons**

Run: `pytest tests/catalog/test_groups.py::test_catalog_groups_cover_known_datasets tests/catalog/test_groups.py::test_catalog_covers_all_stock_raw_stems tests/data/test_loader.py::test_loader_uses_semantic_key_for_kosdaq_close_data tests/ingest/test_pipeline.py::test_ingest_finds_nested_raw_dataset -v`

Expected: FAIL with errors like `AttributeError: QW_KSDQ_ADJ_C`, `KeyError` from missing catalog entries, and `FileNotFoundError: missing raw dataset: qw_ksdq_adj_c`

- [ ] **Step 3: Add the KOSDAQ150 dataset ids, specs, frame keys, and nested raw lookup**

```python
# backtesting/catalog/enums.py
class DatasetId(str, Enum):
    # existing ids...
    QW_KSDQ150_YN = "qw_ksdq150_yn"
    QW_KSDQ_ADJ_C = "qw_ksdq_adj_c"
    QW_KSDQ_ADJ_H = "qw_ksdq_adj_h"
    QW_KSDQ_ADJ_L = "qw_ksdq_adj_l"
    QW_KSDQ_ADJ_O = "qw_ksdq_adj_o"
    QW_KSDQ_MKCAP = "qw_ksdq_mkcap"
    QW_KSDQ_MKTCAP_FLT = "qw_ksdq_mktcap_flt"
    QW_KSDQ_V = "qw_ksdq_v"
    QW_KSDQ_WICS_SEC_BIG = "qw_ksdq_wics_sec_big"


# backtesting/catalog/catalog.py
specs = {
    # existing specs...
    DatasetId.QW_KSDQ_ADJ_C: _spec(DatasetId.QW_KSDQ_ADJ_C, group=DatasetGroup.PRICE, freq="D", kind="price"),
    DatasetId.QW_KSDQ_ADJ_O: _spec(DatasetId.QW_KSDQ_ADJ_O, group=DatasetGroup.PRICE, freq="D", kind="price"),
    DatasetId.QW_KSDQ_ADJ_H: _spec(DatasetId.QW_KSDQ_ADJ_H, group=DatasetGroup.PRICE, freq="D", kind="price"),
    DatasetId.QW_KSDQ_ADJ_L: _spec(DatasetId.QW_KSDQ_ADJ_L, group=DatasetGroup.PRICE, freq="D", kind="price"),
    DatasetId.QW_KSDQ_V: _spec(DatasetId.QW_KSDQ_V, group=DatasetGroup.PRICE, freq="D", kind="volume", fill="zero"),
    DatasetId.QW_KSDQ_MKCAP: _spec(DatasetId.QW_KSDQ_MKCAP, group=DatasetGroup.PRICE, freq="D", kind="market_cap"),
    DatasetId.QW_KSDQ_MKTCAP_FLT: _spec(
        DatasetId.QW_KSDQ_MKTCAP_FLT,
        group=DatasetGroup.PRICE,
        freq="D",
        kind="float_market_cap",
    ),
    DatasetId.QW_KSDQ150_YN: _spec(
        DatasetId.QW_KSDQ150_YN,
        group=DatasetGroup.FLAG,
        freq="D",
        kind="flag",
        fill="zero",
        dtype="int64",
    ),
    DatasetId.QW_KSDQ_WICS_SEC_BIG: _spec(
        DatasetId.QW_KSDQ_WICS_SEC_BIG,
        group=DatasetGroup.META,
        freq="M",
        kind="sector",
        dtype="string",
    ),
}


# backtesting/data/loader.py
class LoadRequest:
    datasets: list[DatasetId]
    start: str
    end: str
    universe: pd.DataFrame | None = None
    benchmark: pd.Series | None = None
    universe_id: str | None = None
    price_mode: str = "adj"


FRAME_KEYS = {
    # existing keys...
    DatasetId.QW_KSDQ_ADJ_C: "close",
    DatasetId.QW_KSDQ_ADJ_O: "open",
    DatasetId.QW_KSDQ_ADJ_H: "high",
    DatasetId.QW_KSDQ_ADJ_L: "low",
    DatasetId.QW_KSDQ_V: "volume",
    DatasetId.QW_KSDQ_MKCAP: "market_cap",
    DatasetId.QW_KSDQ_MKTCAP_FLT: "float_market_cap",
    DatasetId.QW_KSDQ150_YN: "universe_membership",
    DatasetId.QW_KSDQ_WICS_SEC_BIG: "sector_big",
}


# backtesting/ingest/io.py
def find_raw_path(raw_dir: Path, stem: str) -> Path:
    for suffix in (".csv", ".xlsx"):
        direct = raw_dir / f"{stem}{suffix}"
        if direct.exists():
            return direct

    matches: list[Path] = []
    for suffix in (".csv", ".xlsx"):
        matches.extend(sorted(raw_dir.rglob(f"{stem}{suffix}")))
    if matches:
        return matches[0]

    raise FileNotFoundError(f"missing raw dataset: {stem}")
```

- [ ] **Step 4: Run the focused tests again and confirm they pass**

Run: `pytest tests/catalog/test_groups.py tests/data/test_loader.py tests/ingest/test_pipeline.py -v`

Expected: PASS for the new KOSDAQ dataset coverage, semantic loader key, and nested raw ingest test

- [ ] **Step 5: Commit the dataset-layer changes**

```bash
git add backtesting/catalog/enums.py backtesting/catalog/catalog.py backtesting/data/loader.py backtesting/ingest/io.py tests/catalog/test_groups.py tests/data/test_loader.py tests/ingest/test_pipeline.py
git commit -m "feat: register kosdaq150 dataset family"
```

### Task 2: Create UniverseSpec And UniverseRegistry

**Files:**
- Create: `backtesting/universe.py`
- Modify: `backtesting/__init__.py`
- Test: `tests/data/test_universe.py`

- [ ] **Step 1: Write the failing universe registry tests**

```python
# tests/data/test_universe.py
import pytest

from backtesting.catalog import DatasetId
from backtesting.universe import UniverseRegistry


def test_registry_returns_kosdaq150_defaults() -> None:
    registry = UniverseRegistry.default()
    spec = registry.get("kosdaq150")

    assert spec.id == "kosdaq150"
    assert spec.membership_dataset is DatasetId.QW_KSDQ150_YN
    assert spec.default_benchmark_dataset == "qw_BM"
    assert spec.dataset_aliases["close"] is DatasetId.QW_KSDQ_ADJ_C
    assert spec.dataset_aliases["market_cap"] is DatasetId.QW_KSDQ_MKCAP


def test_registry_remaps_generic_dataset_ids_to_universe_specific_ids() -> None:
    registry = UniverseRegistry.default()
    spec = registry.get("kosdaq150")

    assert spec.resolve_dataset(DatasetId.QW_ADJ_C) is DatasetId.QW_KSDQ_ADJ_C
    assert spec.resolve_dataset(DatasetId.QW_MKTCAP) is DatasetId.QW_KSDQ_MKCAP
    assert spec.resolve_dataset(DatasetId.QW_OP_NFY1) is DatasetId.QW_OP_NFY1


def test_registry_rejects_unknown_universe() -> None:
    registry = UniverseRegistry.default()

    with pytest.raises(KeyError, match="unknown universe"):
        registry.get("not-real")
```

- [ ] **Step 2: Run the new universe tests and verify they fail because the module does not exist yet**

Run: `pytest tests/data/test_universe.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'backtesting.universe'`

- [ ] **Step 3: Implement UniverseSpec, alias remapping, and registry defaults**

```python
# backtesting/universe.py
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from backtesting.catalog import DatasetId


_DATASET_ALIAS_BY_ID: dict[DatasetId, str] = {
    DatasetId.QW_ADJ_C: "close",
    DatasetId.QW_ADJ_O: "open",
    DatasetId.QW_ADJ_H: "high",
    DatasetId.QW_ADJ_L: "low",
    DatasetId.QW_V: "volume",
    DatasetId.QW_MKTCAP: "market_cap",
    DatasetId.QW_MKTCAP_FLT: "float_market_cap",
    DatasetId.QW_WICS_SEC_BIG: "sector_big",
    DatasetId.QW_K200_YN: "membership",
}


@dataclass(frozen=True, slots=True)
class UniverseSpec:
    id: str
    display_name: str
    description: str
    membership_dataset: DatasetId | None
    default_benchmark_code: str
    default_benchmark_name: str
    default_benchmark_dataset: str
    dataset_aliases: Mapping[str, DatasetId]

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset_aliases", MappingProxyType(dict(self.dataset_aliases)))

    def resolve_dataset(self, dataset_id: DatasetId) -> DatasetId:
        alias = _DATASET_ALIAS_BY_ID.get(dataset_id)
        if alias is None:
            return dataset_id
        return self.dataset_aliases.get(alias, dataset_id)


@dataclass(frozen=True, slots=True)
class UniverseRegistry:
    specs: Mapping[str, UniverseSpec]

    @classmethod
    def default(cls) -> "UniverseRegistry":
        return cls(
            specs={
                "legacy_k200": UniverseSpec(
                    id="legacy_k200",
                    display_name="Legacy KOSPI200",
                    description="Existing K200 membership path for backward compatibility.",
                    membership_dataset=DatasetId.QW_K200_YN,
                    default_benchmark_code="IKS200",
                    default_benchmark_name="KOSPI200",
                    default_benchmark_dataset="qw_BM",
                    dataset_aliases={},
                ),
                "kosdaq150": UniverseSpec(
                    id="kosdaq150",
                    display_name="KOSDAQ150",
                    description="KOSDAQ150 price and membership dataset family.",
                    membership_dataset=DatasetId.QW_KSDQ150_YN,
                    default_benchmark_code="KQ150",
                    default_benchmark_name="KOSDAQ150",
                    default_benchmark_dataset="qw_BM",
                    dataset_aliases={
                        "close": DatasetId.QW_KSDQ_ADJ_C,
                        "open": DatasetId.QW_KSDQ_ADJ_O,
                        "high": DatasetId.QW_KSDQ_ADJ_H,
                        "low": DatasetId.QW_KSDQ_ADJ_L,
                        "volume": DatasetId.QW_KSDQ_V,
                        "market_cap": DatasetId.QW_KSDQ_MKCAP,
                        "float_market_cap": DatasetId.QW_KSDQ_MKTCAP_FLT,
                        "sector_big": DatasetId.QW_KSDQ_WICS_SEC_BIG,
                        "membership": DatasetId.QW_KSDQ150_YN,
                    },
                ),
            }
        )

    def get(self, universe_id: str) -> UniverseSpec:
        try:
            return self.specs[universe_id]
        except KeyError as exc:
            available = ", ".join(sorted(self.specs))
            raise KeyError(f"unknown universe '{universe_id}'. Available: {available}") from exc
```

- [ ] **Step 4: Export the new universe types from the top-level package**

```python
# backtesting/__init__.py
from .universe import UniverseRegistry, UniverseSpec

__all__ = (
    # existing exports...
    "UniverseRegistry",
    "UniverseSpec",
)
```

- [ ] **Step 5: Run the universe tests and confirm they pass**

Run: `pytest tests/data/test_universe.py -v`

Expected: PASS with `kosdaq150` defaults and generic-to-universe dataset remapping verified

- [ ] **Step 6: Commit the universe registry layer**

```bash
git add backtesting/universe.py backtesting/__init__.py tests/data/test_universe.py
git commit -m "feat: add universe registry"
```

### Task 3: Make BacktestRunner And CLI Universe-Aware

**Files:**
- Modify: `backtesting/run.py`
- Test: `tests/test_run.py`

- [ ] **Step 1: Write the failing runner and CLI tests**

```python
# tests/test_run.py
def test_runner_uses_kosdaq_universe_specific_datasets(tmp_path: Path) -> None:
    parquet_dir = tmp_path / "parquet"
    raw_dir = tmp_path / "raw"
    result_dir = tmp_path / "results"
    parquet_dir.mkdir()
    raw_dir.mkdir()
    store = ParquetStore(parquet_dir)
    index = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])

    store.write("qw_adj_c", pd.DataFrame({"A": [1.0, 1.0, 1.0]}, index=index))
    store.write("qw_ksdq_adj_c", pd.DataFrame({"A": [10.0, 11.0, 12.0]}, index=index))
    store.write("qw_ksdq150_yn", pd.DataFrame({"A": [1, 1, 1], "B": [0, 0, 0]}, index=index))

    runner = BacktestRunner(catalog=DataCatalog.default(), raw_dir=raw_dir, parquet_dir=parquet_dir, result_dir=result_dir)
    report = runner.run(
        RunConfig(
            strategy="momentum",
            start="2024-01-02",
            end="2024-01-04",
            lookback=1,
            schedule="daily",
            fill_mode="close",
            universe_id="kosdaq150",
        )
    )

    assert report.config.universe_id == "kosdaq150"
    assert report.config.benchmark_name == "KOSDAQ150"
    assert report.result.equity.index[-1].isoformat() == "2024-01-04T00:00:00"


def test_run_parser_accepts_universe_argument(monkeypatch: pytest.MonkeyPatch) -> None:
    observed = {}

    class StubRunner:
        def __init__(self, result_dir=None):
            pass

        def run(self, config):
            observed["config"] = config
            index = pd.to_datetime(["2024-01-02"])
            result = BacktestResult(
                equity=pd.Series([1.0], index=index),
                returns=pd.Series([0.0], index=index),
                weights=pd.DataFrame({"A": [1.0]}, index=index),
                qty=pd.DataFrame({"A": [1.0]}, index=index),
                turnover=pd.Series([0.0], index=index),
            )
            return RunReport(config=config, summary={"final_equity": 1.0, "avg_turnover": 0.0}, result=result)

    monkeypatch.setattr("backtesting.run.BacktestRunner", StubRunner)
    monkeypatch.setattr("sys.argv", ["run.py", "--strategy", "momentum", "--start", "2024-01-02", "--end", "2024-01-02", "--universe", "kosdaq150"])

    backtesting_main()

    assert observed["config"].universe_id == "kosdaq150"
```

- [ ] **Step 2: Run the focused runner tests and verify they fail**

Run: `pytest tests/test_run.py::test_runner_uses_kosdaq_universe_specific_datasets tests/test_run.py::test_run_parser_accepts_universe_argument -v`

Expected: FAIL because `RunConfig` has no `universe_id`, parser does not know `--universe`, and benchmark defaults still point to KOSPI200

- [ ] **Step 3: Extend RunConfig to support optional benchmarks and universe_id**

```python
# backtesting/run.py
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
    universe_id: str | None = None
    benchmark_code: str | None = None
    benchmark_name: str | None = None
    benchmark_dataset: str | None = None
    warmup_days: int = 0
```

- [ ] **Step 4: Implement universe-aware dataset resolution, membership masks, and benchmark defaults**

```python
# backtesting/run.py
from dataclasses import asdict, dataclass, replace

from .universe import UniverseRegistry, UniverseSpec


class BacktestRunner:
    def __init__(self, *, catalog: DataCatalog | None = None, raw_dir: Path | None = None, parquet_dir: Path | None = None, result_dir: Path | None = None, universe_registry: UniverseRegistry | None = None) -> None:
        self.catalog = catalog or DataCatalog.default()
        self.universe_registry = universe_registry or UniverseRegistry.default()
        # existing init...

    def run(self, config: RunConfig) -> RunReport:
        strategy = build_strategy(config.strategy, top_n=config.top_n, lookback=config.lookback)
        universe_spec = self._resolve_universe_spec(config)
        effective_config = self._resolve_effective_config(config, universe_spec)

        dataset_ids = self._resolve_dataset_ids(strategy.datasets, effective_config, universe_spec)
        self._ensure_parquet(dataset_ids)

        market = self.loader.load(
            LoadRequest(
                datasets=dataset_ids,
                start=self._resolve_load_start(effective_config.start, effective_config.warmup_days),
                end=effective_config.end,
                universe_id=effective_config.universe_id,
            )
        )
        market.universe = self._universe(market, universe_spec, effective_config.use_k200)

        # existing plan/engine logic...
        report = RunReport(config=effective_config, summary=summary, result=result, position_plan=plan)
        report.output_dir = self.writer.write(report)
        return report

    def _resolve_universe_spec(self, config: RunConfig) -> UniverseSpec | None:
        if config.universe_id:
            return self.universe_registry.get(config.universe_id)
        if config.use_k200:
            return self.universe_registry.get("legacy_k200")
        return None

    def _resolve_effective_config(self, config: RunConfig, universe_spec: UniverseSpec | None) -> RunConfig:
        if universe_spec is None:
            benchmark_code = config.benchmark_code or "IKS200"
            benchmark_name = config.benchmark_name or "KOSPI200"
            benchmark_dataset = config.benchmark_dataset or "qw_BM"
            return replace(config, benchmark_code=benchmark_code, benchmark_name=benchmark_name, benchmark_dataset=benchmark_dataset)

        return replace(
            config,
            universe_id=config.universe_id or universe_spec.id,
            benchmark_code=config.benchmark_code or universe_spec.default_benchmark_code,
            benchmark_name=config.benchmark_name or universe_spec.default_benchmark_name,
            benchmark_dataset=config.benchmark_dataset or universe_spec.default_benchmark_dataset,
        )

    def _resolve_dataset_ids(self, strategy_datasets: tuple[DatasetId, ...], config: RunConfig, universe_spec: UniverseSpec | None) -> list[DatasetId]:
        dataset_ids = [DatasetId.QW_ADJ_C, *strategy_datasets]
        if config.fill_mode == "next_open":
            dataset_ids.append(DatasetId.QW_ADJ_O)
        if universe_spec is not None and universe_spec.membership_dataset is not None:
            dataset_ids.append(universe_spec.membership_dataset)

        if universe_spec is not None:
            dataset_ids = [universe_spec.resolve_dataset(dataset_id) for dataset_id in dataset_ids]

        return list(dict.fromkeys(dataset_ids))

    @staticmethod
    def _universe(market: MarketData, universe_spec: UniverseSpec | None, use_k200: bool) -> pd.DataFrame | None:
        if universe_spec is None:
            return None
        membership = market.frames.get("universe_membership")
        if membership is None:
            return None
        return membership.fillna(0).astype(bool)
```

- [ ] **Step 5: Add CLI parsing for `--universe` and keep legacy `--no-k200` behavior**

```python
# backtesting/run.py
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run registered backtests.")
    # existing args...
    parser.add_argument("--universe", choices=("kosdaq150",), dest="universe_id")
    parser.add_argument("--no-k200", action="store_true")
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
        universe_id=args.universe_id,
        use_k200=not args.no_k200,
        allow_fractional=not args.no_fractional,
    )
    # existing runner call...
```

- [ ] **Step 6: Run the runner tests and the existing run suite**

Run: `pytest tests/test_run.py -v`

Expected: PASS for the new `kosdaq150` path and existing legacy `use_k200` tests

- [ ] **Step 7: Commit the runner and CLI changes**

```bash
git add backtesting/run.py tests/test_run.py
git commit -m "feat: add universe-aware backtest runner"
```

### Task 4: Propagate `universe_id` Through Dashboard Presets And Saved-Run Signatures

**Files:**
- Modify: `dashboard/strategies.py`
- Modify: `dashboard/run.py`
- Modify: `dashboard/backend/services/launch_resolution.py`
- Modify: `dashboard/backend/services/run_index.py`
- Test: `tests/dashboard/test_run.py`
- Test: `tests/dashboard/backend/test_launch_resolution.py`
- Test: `tests/dashboard/backend/test_run_index_service.py`

- [ ] **Step 1: Write the failing dashboard tests**

```python
# tests/dashboard/test_run.py
def test_launch_dashboard_passes_universe_id_to_backtest_runner(tmp_path: Path, monkeypatch) -> None:
    observed_configs = []
    kosdaq_preset = replace(DEFAULT_LAUNCH_CONFIG.strategies[1], universe_id="kosdaq150")
    launch_config = replace(DEFAULT_LAUNCH_CONFIG, strategies=(DEFAULT_LAUNCH_CONFIG.strategies[0], kosdaq_preset))

    class FakeRunner:
        def run(self, config):
            observed_configs.append(config)
            return type("Report", (), {"output_dir": tmp_path / f"{config.strategy}_20260405_120000"})()

    monkeypatch.setattr("dashboard.run.DEFAULT_LAUNCH_CONFIG", launch_config)
    monkeypatch.setattr("dashboard.run.BacktestRunner", lambda result_dir=None: FakeRunner())
    # keep the rest of the test's existing stubs...

    launch_dashboard(runs_root=tmp_path, host="127.0.0.1", port=8000)

    assert observed_configs[0].universe_id == "kosdaq150"


# tests/dashboard/backend/test_launch_resolution.py
def test_resolution_marks_strategy_missing_when_universe_changes(tmp_path: Path) -> None:
    _write_matching_default_runs(tmp_path)
    altered = replace(
        DEFAULT_LAUNCH_CONFIG,
        strategies=(
            replace(DEFAULT_LAUNCH_CONFIG.strategies[0], universe_id="kosdaq150"),
            DEFAULT_LAUNCH_CONFIG.strategies[1],
        ),
    )

    plan = LaunchResolutionService(tmp_path).resolve(altered)

    assert plan.selected_run_ids == ["op_fwd_yield_20260405_110000"]
    assert [item.strategy_name for item in plan.missing_presets] == ["momentum"]


# tests/dashboard/backend/test_run_index_service.py
def test_list_runs_treats_universe_id_as_part_of_signature(tmp_path: Path) -> None:
    _write_run(tmp_path, "momentum_20260405_090000", name="Momentum", strategy="momentum", final_equity=121.0)
    _write_run(tmp_path, "momentum_20260405_100000", name="Momentum KOSDAQ", strategy="momentum", final_equity=122.0)

    first = tmp_path / "momentum_20260405_090000" / "config.json"
    second = tmp_path / "momentum_20260405_100000" / "config.json"
    first_payload = json.loads(first.read_text(encoding="utf-8"))
    second_payload = json.loads(second.read_text(encoding="utf-8"))
    second_payload["universe_id"] = "kosdaq150"
    first.write_text(json.dumps(first_payload), encoding="utf-8")
    second.write_text(json.dumps(second_payload), encoding="utf-8")

    runs = RunIndexService(tmp_path).list_runs()

    assert [run.run_id for run in runs] == ["momentum_20260405_100000", "momentum_20260405_090000"]
```

- [ ] **Step 2: Run the dashboard-focused tests and confirm they fail**

Run: `pytest tests/dashboard/test_run.py tests/dashboard/backend/test_launch_resolution.py tests/dashboard/backend/test_run_index_service.py -v`

Expected: FAIL because `StrategyPreset` has no `universe_id`, launch signatures ignore it, and run-index dedupe treats KOSPI and KOSDAQ runs as the same config

- [ ] **Step 3: Add `universe_id` to strategy presets and pass it to RunConfig**

```python
# dashboard/strategies.py
@dataclass(frozen=True, slots=True)
class StrategyPreset:
    enabled: bool
    strategy_name: str
    display_label: str
    params: Mapping[str, object] = field(default_factory=dict)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig.default_kospi200)
    warmup: WarmupConfig = field(default_factory=WarmupConfig)
    universe_id: str | None = None


# dashboard/run.py
def _build_run_config(preset: StrategyPreset) -> RunConfig:
    config = DEFAULT_LAUNCH_CONFIG.global_config
    return RunConfig(
        start=config.start,
        end=config.end,
        capital=config.capital,
        strategy=preset.strategy_name,
        name=preset.display_label,
        schedule=config.schedule,
        fill_mode=config.fill_mode,
        fee=config.fee,
        sell_tax=config.sell_tax,
        slippage=config.slippage,
        use_k200=config.use_k200,
        allow_fractional=config.allow_fractional,
        universe_id=preset.universe_id,
        benchmark_code=preset.benchmark.code,
        benchmark_name=preset.benchmark.name,
        benchmark_dataset=preset.benchmark.dataset,
        warmup_days=preset.warmup.extra_days,
        **dict(preset.params),
    )
```

- [ ] **Step 4: Include `universe_id` in launch resolution and run-index dedupe signatures**

```python
# dashboard/backend/services/launch_resolution.py
@staticmethod
def _build_signature(config: DashboardLaunchConfig, preset: StrategyPreset) -> dict[str, Any]:
    signature = asdict(config.global_config)
    signature["strategy"] = preset.strategy_name
    signature["universe_id"] = preset.universe_id
    signature.update(dict(preset.params))
    signature["benchmark_code"] = preset.benchmark.code
    signature["benchmark_name"] = preset.benchmark.name
    signature["benchmark_dataset"] = preset.benchmark.dataset
    signature["warmup_days"] = preset.warmup.extra_days
    return LaunchResolutionService._normalize_value(signature)


@staticmethod
def _build_saved_signature(saved_config: dict[str, Any], desired_signature: dict[str, Any]) -> dict[str, Any]:
    compat_defaults = {
        "benchmark_code": "IKS200",
        "benchmark_name": "KOSPI200",
        "benchmark_dataset": "qw_BM",
        "warmup_days": 0,
        "universe_id": None,
    }
    return LaunchResolutionService._normalize_value(
        {key: saved_config.get(key, compat_defaults.get(key)) for key in desired_signature}
    )


# dashboard/backend/services/run_index.py
@staticmethod
def _config_signature(config: dict[str, Any]) -> str | None:
    relevant = {
        key: value
        for key, value in {
            **config,
            "benchmark_code": config.get("benchmark_code", "IKS200"),
            "benchmark_name": config.get("benchmark_name", "KOSPI200"),
            "benchmark_dataset": config.get("benchmark_dataset", "qw_BM"),
            "warmup_days": config.get("warmup_days", 0),
            "universe_id": config.get("universe_id"),
        }.items()
        if key != "name"
    }
    # existing normalization...
```

- [ ] **Step 5: Run the dashboard tests and confirm they pass**

Run: `pytest tests/dashboard/test_run.py tests/dashboard/backend/test_launch_resolution.py tests/dashboard/backend/test_run_index_service.py -v`

Expected: PASS with `universe_id` propagated to launch configs and treated as part of the saved-run signature

- [ ] **Step 6: Commit the dashboard propagation changes**

```bash
git add dashboard/strategies.py dashboard/run.py dashboard/backend/services/launch_resolution.py dashboard/backend/services/run_index.py tests/dashboard/test_run.py tests/dashboard/backend/test_launch_resolution.py tests/dashboard/backend/test_run_index_service.py
git commit -m "feat: propagate universe id through dashboard config"
```

### Task 5: Document The New Universe And Run Full Verification

**Files:**
- Modify: `README.md`
- Verification: repo test commands below

- [ ] **Step 1: Add README usage for the new KOSDAQ150 universe**

````md
# README.md
## Run Backtests

KOSDAQ150 universe example:

```powershell
python run.py --strategy momentum --universe kosdaq150 --start 2020-01-01 --end 2020-12-31 --top-n 20 --lookback 20 --schedule monthly --fill-mode next_open
```

When `--universe kosdaq150` is set, the runner uses the `qw_ksdq_*` dataset family and defaults the benchmark metadata to KOSDAQ150 from `qw_BM`. You can still override benchmark metadata explicitly if needed.
````

- [ ] **Step 2: Run the high-signal verification suite**

Run: `pytest tests/catalog/test_groups.py tests/data/test_loader.py tests/data/test_universe.py tests/ingest/test_pipeline.py tests/test_run.py tests/dashboard/test_run.py tests/dashboard/backend/test_launch_resolution.py tests/dashboard/backend/test_run_index_service.py -v`

Expected: PASS with 0 failures

- [ ] **Step 3: Run the broader regression suite for backtesting and reporting entrypoints**

Run: `pytest tests/reporting/test_cli.py tests/reporting/test_builder.py tests/reporting/test_snapshots.py tests/reporting/test_benchmarks.py -v`

Expected: PASS, proving the optional benchmark default change did not break report-side consumers

- [ ] **Step 4: Commit the documentation and verified integration**

```bash
git add README.md
git commit -m "docs: add kosdaq150 universe usage"
```

## Self-Review

- Spec coverage check:
  Dataset-family registration is covered by Task 1.
  `UniverseSpec` and alias remapping are covered by Task 2.
  CLI and Python backtest execution are covered by Task 3.
  Dashboard preset/signature propagation is covered by Task 4.
  README and full verification are covered by Task 5.

- Placeholder scan:
  No placeholder markers or unspecified verification commands remain.

- Type consistency:
  `universe_id` is introduced consistently on `LoadRequest`, `RunConfig`, `StrategyPreset`, and dashboard signatures.
  Benchmark defaults are handled by resolved `RunConfig` values instead of hard-coded dataclass defaults, so `kosdaq150` can supply its own benchmark.
