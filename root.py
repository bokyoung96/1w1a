from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RootPaths:
    root: Path

    @property
    def config_path(self) -> Path:
        return self.root / "config" / "config.json"

    @property
    def config_path_str(self) -> str:
        return str(self.config_path)


ROOT = RootPaths(Path(__file__).resolve().parent)
