from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArasPaths:
    base_dir: Path
    data_dir: Path
    raw_dir: Path
    processed_dir: Path
    wiki_dir: Path
    signals_dir: Path
    state_dir: Path
    state_db: Path


@dataclass(frozen=True)
class ArasConfig:
    paths: ArasPaths
    polling_limit: int = 100


def build_config(base_dir: Path) -> ArasConfig:
    base_dir = Path(base_dir)
    data_dir = base_dir / "data"
    paths = ArasPaths(
        base_dir=base_dir,
        data_dir=data_dir,
        raw_dir=data_dir / "raw",
        processed_dir=data_dir / "processed",
        wiki_dir=data_dir / "wiki",
        signals_dir=data_dir / "signals",
        state_dir=data_dir / "state",
        state_db=data_dir / "state" / "aras.sqlite3",
    )
    for directory in (
        paths.data_dir,
        paths.raw_dir,
        paths.processed_dir,
        paths.wiki_dir,
        paths.signals_dir,
        paths.state_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return ArasConfig(paths=paths)
