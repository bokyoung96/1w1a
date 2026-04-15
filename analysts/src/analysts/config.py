from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REDACTED = "<redacted>"


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
    local_config_path: Path
    telethon_session_path: Path


@dataclass(frozen=True)
class TelethonConfig:
    api_id: int
    api_hash: str
    phone_number: str
    channel: str
    session_name: str
    mode: str = "telethon"
    pdf_only: bool = True

    def to_display_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "api_id": REDACTED,
            "api_hash": REDACTED,
            "phone_number": REDACTED,
            "channel": self.channel,
            "session_name": self.session_name,
            "pdf_only": self.pdf_only,
        }


@dataclass(frozen=True)
class ArasConfig:
    paths: ArasPaths
    polling_limit: int = 100
    telethon: TelethonConfig | None = None

    def to_display_dict(self) -> dict[str, Any]:
        return {
            "paths": {
                "base_dir": str(self.paths.base_dir),
                "data_dir": str(self.paths.data_dir),
                "raw_dir": str(self.paths.raw_dir),
                "processed_dir": str(self.paths.processed_dir),
                "wiki_dir": str(self.paths.wiki_dir),
                "signals_dir": str(self.paths.signals_dir),
                "state_dir": str(self.paths.state_dir),
                "state_db": str(self.paths.state_db),
                "local_config_path": str(self.paths.local_config_path),
                "telethon_session_path": str(self.paths.telethon_session_path),
            },
            "polling_limit": self.polling_limit,
            "telethon": None if self.telethon is None else self.telethon.to_display_dict(),
        }


@dataclass(frozen=True)
class LocalRuntimeConfig:
    telethon: TelethonConfig | None


def build_config(base_dir: Path) -> ArasConfig:
    base_dir = Path(base_dir)
    data_dir = base_dir / "data"
    local_config_path = base_dir / "config.local.json"
    runtime = _load_local_runtime_config(local_config_path)
    session_name = runtime.telethon.session_name if runtime.telethon is not None else "telethon"
    paths = ArasPaths(
        base_dir=base_dir,
        data_dir=data_dir,
        raw_dir=data_dir / "raw",
        processed_dir=data_dir / "processed",
        wiki_dir=data_dir / "wiki",
        signals_dir=data_dir / "signals",
        state_dir=data_dir / "state",
        state_db=data_dir / "state" / "aras.sqlite3",
        local_config_path=local_config_path,
        telethon_session_path=data_dir / "state" / f"{session_name}.session",
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
    return ArasConfig(paths=paths, telethon=runtime.telethon)


def require_telethon_config(config: ArasConfig) -> TelethonConfig:
    if config.telethon is None:
        raise RuntimeError(
            "Missing Telethon config. Create analysts/config.local.json with telegram.api_id, "
            "telegram.api_hash, telegram.phone_number, telegram.channel, and telegram.session_name."
        )
    return config.telethon


def _load_local_runtime_config(local_config_path: Path) -> LocalRuntimeConfig:
    if not local_config_path.exists():
        return LocalRuntimeConfig(telethon=None)

    payload = json.loads(local_config_path.read_text())
    telegram_payload = payload.get("telegram") or {}
    if not telegram_payload:
        return LocalRuntimeConfig(telethon=None)

    mode = str(telegram_payload.get("mode", "telethon"))
    if mode != "telethon":
        return LocalRuntimeConfig(telethon=None)

    return LocalRuntimeConfig(
        telethon=TelethonConfig(
            api_id=int(telegram_payload["api_id"]),
            api_hash=str(telegram_payload["api_hash"]),
            phone_number=str(telegram_payload["phone_number"]),
            channel=str(telegram_payload["channel"]),
            session_name=str(telegram_payload.get("session_name", "telethon")),
            mode=mode,
            pdf_only=bool(telegram_payload.get("pdf_only", True)),
        )
    )
