import json
from pathlib import Path

import pytest

from analysts.config import build_config
from analysts.fetcher import TelegramFetcher
from analysts.storage import SqliteArasStore


def _load_fixture(name: str) -> list[dict]:
    fixture_path = Path(__file__).parent / "fixtures" / name
    return json.loads(fixture_path.read_text())


class FakeTelegramClient:
    def __init__(self, updates: list[dict], *, fail_file_ids: set[str] | None = None) -> None:
        self._updates = updates
        self._fail_file_ids = fail_file_ids or set()
        self.requested_offsets: list[int | None] = []
        self.file_requests: list[str] = []
        self.downloaded_paths: list[str] = []

    def get_updates(self, *, offset: int | None, limit: int) -> list[dict]:
        self.requested_offsets.append(offset)
        return [update for update in self._updates if offset is None or update["update_id"] >= offset][:limit]

    def get_file(self, file_id: str) -> dict[str, str]:
        self.file_requests.append(file_id)
        return {"file_path": f"docs/{file_id}.pdf"}

    def download_file(self, file_path: str) -> bytes:
        self.downloaded_paths.append(file_path)
        file_id = Path(file_path).stem
        if file_id in self._fail_file_ids:
            raise RuntimeError(f"download failed for {file_id}")
        return f"PDF bytes for {file_id}".encode()


def test_downloads_only_unseen_pdf_messages_and_advances_next_offset(tmp_path: Path) -> None:
    client = FakeTelegramClient(_load_fixture("sample_updates.json"))
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    result = fetcher.poll_once(channel="DOC_POOL")

    assert client.requested_offsets == [None]
    assert [report.metadata["file_unique_id"] for report in result.downloaded] == ["uniq-001"]
    assert [item["update_id"] for item in result.skipped_duplicates] == [102]
    assert result.ignored_updates == [101]
    assert result.next_offset == 103
    assert store.get_next_update_offset() == 103

    saved_path = result.downloaded[0].pdf_path
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"PDF bytes for file-001"


def test_keeps_stored_offset_when_a_download_fails(tmp_path: Path) -> None:
    client = FakeTelegramClient(_load_fixture("sample_updates.json"), fail_file_ids={"file-001"})
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    store.set_next_update_offset(77)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    with pytest.raises(RuntimeError, match="download failed for file-001"):
        fetcher.poll_once(channel="DOC_POOL")

    assert client.requested_offsets == [77]
    assert store.get_next_update_offset() == 77
    assert store.list_reports() == []
