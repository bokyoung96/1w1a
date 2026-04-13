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
