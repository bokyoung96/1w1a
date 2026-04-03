import backtesting as bt
from kis import KISConfig


def test_public_package_exports_import_cleanly() -> None:
    export_names = bt.__all__

    assert isinstance(export_names, tuple)
    assert export_names == tuple(dict.fromkeys(export_names))
    assert {"DataCatalog", "BacktestEngine", "ValidationSession"}.issubset(export_names)
    assert KISConfig is not None

    namespace: dict[str, object] = {}
    exec("from backtesting import *", namespace)

    for name in export_names:
        assert name in namespace
