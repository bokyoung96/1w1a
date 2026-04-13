import importlib.util
from pathlib import Path


def _load_generate_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "graphify-out" / "generate_graphify.py"
    spec = importlib.util.spec_from_file_location("graphify_generate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_prepare_output_paths_cleans_stale_generated_files(tmp_path) -> None:
    module = _load_generate_module()

    out = tmp_path / "graphify-out"
    obsidian = out / "obsidian"
    wiki = out / "wiki"
    obsidian.mkdir(parents=True)
    wiki.mkdir(parents=True)
    (obsidian / "qw__ksdq_v.csv.md").write_text("stale", encoding="utf-8")
    (wiki / "old.md").write_text("stale", encoding="utf-8")
    (out / "graph.svg").write_text("stale", encoding="utf-8")
    (out / "graph 2.html").write_text("stale", encoding="utf-8")
    (out / "summary 2.json").write_text("stale", encoding="utf-8")

    module.prepare_output_paths(out)

    assert not (obsidian / "qw__ksdq_v.csv.md").exists()
    assert not (wiki / "old.md").exists()
    assert not (out / "graph.svg").exists()
    assert not (out / "graph 2.html").exists()
    assert not (out / "summary 2.json").exists()
    assert obsidian.exists()
    assert wiki.exists()
