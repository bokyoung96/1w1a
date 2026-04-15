import json
from pathlib import Path

import pytest

from analysts.config import build_config
from analysts.fetcher import TelegramFetcher
from analysts.storage import SqliteArasStore



def _load_fixture(name: str) -> list[dict]:
    fixture_path = Path(__file__).parent / 'fixtures' / name
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
        return [update for update in self._updates if offset is None or update['update_id'] >= offset][:limit]

    def get_file(self, file_id: str) -> dict[str, str]:
        self.file_requests.append(file_id)
        return {'file_path': f'docs/{file_id}.pdf'}

    def download_file(self, file_path: str) -> bytes:
        self.downloaded_paths.append(file_path)
        file_id = Path(file_path).stem
        if file_id in self._fail_file_ids:
            raise RuntimeError(f'download failed for {file_id}')
        return f'PDF bytes for {file_id}'.encode()


class FakeTelethonClient:
    def __init__(self, messages: list[dict], *, fail_file_ids: set[str] | None = None) -> None:
        self._messages = messages
        self._fail_file_ids = fail_file_ids or set()
        self.latest_channel_requests: list[str] = []
        self.channel_requests: list[tuple[str, int | None, int]] = []
        self.downloaded_file_ids: list[str] = []

    def get_latest_message_id(self, *, channel: str) -> int | None:
        self.latest_channel_requests.append(channel)
        matching = [message['message_id'] for message in self._messages if message['chat']['title'] == channel]
        return max(matching) if matching else None

    def iter_channel_messages(self, *, channel: str, after_message_id: int | None, limit: int) -> list[dict]:
        self.channel_requests.append((channel, after_message_id, limit))
        return [
            message
            for message in self._messages
            if message['chat']['title'] == channel and (after_message_id is None or message['message_id'] > after_message_id)
        ][:limit]

    def download_document(self, message: dict) -> bytes:
        file_id = message['document']['file_id']
        self.downloaded_file_ids.append(file_id)
        if file_id in self._fail_file_ids:
            raise RuntimeError(f'download failed for {file_id}')
        return f'PDF bytes for {file_id}'.encode()



def test_downloads_only_unseen_pdf_messages_and_advances_next_offset(tmp_path: Path) -> None:
    client = FakeTelegramClient(_load_fixture('sample_updates.json'))
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    result = fetcher.poll_once(channel='DOC_POOL')

    assert client.requested_offsets == [None]
    assert [report.metadata['file_unique_id'] for report in result.downloaded] == ['uniq-001']
    assert [item['update_id'] for item in result.skipped_duplicates] == [102]
    assert result.ignored_updates == [101]
    assert result.next_offset == 103
    assert store.get_next_update_offset() == 103

    saved_path = result.downloaded[0].pdf_path
    assert saved_path.exists()
    assert saved_path.read_bytes() == b'PDF bytes for file-001'



def test_keeps_stored_offset_when_a_download_fails(tmp_path: Path) -> None:
    client = FakeTelegramClient(_load_fixture('sample_updates.json'), fail_file_ids={'file-001'})
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    store.set_next_update_offset(77)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    with pytest.raises(RuntimeError, match='download failed for file-001'):
        fetcher.poll_once(channel='DOC_POOL')

    assert client.requested_offsets == [77]
    assert store.get_next_update_offset() == 77
    assert store.list_reports() == []



def test_seeds_last_seen_message_id_on_first_run_without_downloading_history(tmp_path: Path) -> None:
    client = FakeTelethonClient(
        [
            {
                'message_id': 500,
                'date': 1713081000,
                'chat': {'title': 'DOC_POOL'},
                'caption': 'Old report',
                'document': {
                    'file_id': 'file-500',
                    'file_unique_id': 'uniq-500',
                    'file_name': 'old.pdf',
                    'mime_type': 'application/pdf',
                },
            },
            {
                'message_id': 501,
                'date': 1713081060,
                'chat': {'title': 'DOC_POOL'},
                'caption': 'Latest report',
                'document': {
                    'file_id': 'file-501',
                    'file_unique_id': 'uniq-501',
                    'file_name': 'latest.pdf',
                    'mime_type': 'application/pdf',
                },
            },
        ]
    )
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    result = fetcher.poll_once(channel='DOC_POOL')

    assert client.latest_channel_requests == ['DOC_POOL']
    assert client.channel_requests == []
    assert client.downloaded_file_ids == []
    assert result.downloaded == []
    assert result.next_offset == 501
    assert store.get_last_seen_message_id('DOC_POOL') == 501



def test_downloads_only_new_pdf_messages_after_last_seen_seed(tmp_path: Path) -> None:
    client = FakeTelethonClient(
        [
            {
                'message_id': 502,
                'date': 1713081120,
                'chat': {'title': 'DOC_POOL'},
                'caption': 'Text-only update',
            },
            {
                'message_id': 503,
                'date': 1713081180,
                'chat': {'title': 'DOC_POOL'},
                'caption': 'Fresh PDF',
                'document': {
                    'file_id': 'file-503',
                    'file_unique_id': 'uniq-503',
                    'file_name': 'fresh.pdf',
                    'mime_type': 'application/pdf',
                },
            },
        ]
    )
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    store.set_last_seen_message_id('DOC_POOL', 501)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    result = fetcher.poll_once(channel='DOC_POOL')

    assert client.channel_requests == [('DOC_POOL', 501, config.polling_limit)]
    assert result.ignored_updates == [502]
    assert [report.message_id for report in result.downloaded] == [503]
    assert result.next_offset == 503
    assert store.get_last_seen_message_id('DOC_POOL') == 503
    assert client.downloaded_file_ids == ['file-503']



def test_does_not_advance_last_seen_message_id_when_telethon_download_fails(tmp_path: Path) -> None:
    client = FakeTelethonClient(
        [
            {
                'message_id': 503,
                'date': 1713081180,
                'chat': {'title': 'DOC_POOL'},
                'caption': 'Fresh PDF',
                'document': {
                    'file_id': 'file-503',
                    'file_unique_id': 'uniq-503',
                    'file_name': 'fresh.pdf',
                    'mime_type': 'application/pdf',
                },
            }
        ],
        fail_file_ids={'file-503'},
    )
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    store.set_last_seen_message_id('DOC_POOL', 501)
    fetcher = TelegramFetcher(client=client, store=store, config=config)

    with pytest.raises(RuntimeError, match='download failed for file-503'):
        fetcher.poll_once(channel='DOC_POOL')

    assert store.get_last_seen_message_id('DOC_POOL') == 501
    assert store.list_reports() == []
