from root import ROOT


def test_root_exposes_repo_paths():
    assert ROOT.root.name == "1w1a"
    assert ROOT.config_path == ROOT.root / "config" / "config.json"
    assert ROOT.kis_path == ROOT.root / "kis"
    assert ROOT.raw_path == ROOT.root / "raw"
    assert ROOT.parquet_path == ROOT.root / "parquet"
