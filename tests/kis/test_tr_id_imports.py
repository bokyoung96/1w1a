import importlib


def test_tr_id_modules_import_after_kis_migration():
    for module_name in (
        "tr_id.register",
        "tr_id.call",
        "tr_id.deriv_minute",
    ):
        importlib.import_module(module_name)
