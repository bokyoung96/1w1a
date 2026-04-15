import json
import sys
import types
from pathlib import Path

from analysts.cli import main
from analysts.config import build_config
from analysts.pipeline import ArasPipeline
from analysts.storage import SqliteArasStore


class FakeTelegramClient:
    def __init__(self, updates: list[dict], file_payloads: dict[str, bytes]) -> None:
        self._updates = updates
        self._file_payloads = file_payloads

    def get_updates(self, *, offset: int | None, limit: int) -> list[dict]:
        return [update for update in self._updates if offset is None or update['update_id'] >= offset][:limit]

    @staticmethod
    def get_file(file_id: str) -> dict[str, str]:
        return {'file_path': f'docs/{file_id}.pdf'}

    def download_file(self, file_path: str) -> bytes:
        return self._file_payloads[Path(file_path).stem]


class FakeTelethonClient:
    def __init__(self, messages: list[dict]) -> None:
        self._messages = messages

    def get_latest_message_id(self, *, channel: str) -> int | None:
        message_ids = [message['message_id'] for message in self._messages if message['chat']['title'] == channel]
        return max(message_ids) if message_ids else None

    def iter_channel_messages(self, *, channel: str, after_message_id: int | None, limit: int) -> list[dict]:
        return [
            message
            for message in self._messages
            if message['chat']['title'] == channel and (after_message_id is None or message['message_id'] > after_message_id)
        ][:limit]

    def download_document(self, message: dict) -> bytes:
        return message['payload']



def test_runs_fetch_parse_route_analyze_wiki_and_signal_end_to_end(tmp_path: Path) -> None:
    updates = [
        {
            'update_id': 100,
            'channel_post': {
                'message_id': 501,
                'date': 1713081000,
                'chat': {'id': -1001234567890, 'title': 'DOC_POOL'},
                'caption': 'AI Capacity Update',
                'document': {
                    'file_id': 'file-001',
                    'file_unique_id': 'uniq-001',
                    'file_name': 'ai-capacity-update.pdf',
                    'mime_type': 'application/pdf',
                },
            },
        }
    ]
    file_payloads = {
        'file-001': (
            b'Executive Summary:\nNVIDIA (NVDA) and TSMC are expanding advanced packaging.\n\n'
            b'Risks:\nSupply concentration remains a risk for AI accelerators.'
        )
    }
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    pipeline = ArasPipeline(
        client=FakeTelegramClient(updates, file_payloads),
        store=store,
        config=config,
    )

    first_run = pipeline.run_once(channel='DOC_POOL')
    second_run = pipeline.run_once(channel='DOC_POOL')

    assert first_run.summary.downloaded == 1
    assert first_run.summary.duplicates == 0
    assert first_run.summary.ignored == 0
    assert first_run.summary.next_offset == 101
    assert len(first_run.wiki_pages) == 1
    assert len(first_run.signal_files) == 1

    assert second_run.summary.downloaded == 0
    assert second_run.summary.duplicates == 0
    assert second_run.summary.next_offset == 101
    assert second_run.wiki_pages == []
    assert second_run.signal_files == []

    wiki_page = tmp_path / 'data' / 'wiki' / 'sector' / 'semiconductors' / 'source-1.md'
    signal_snapshot = tmp_path / 'data' / 'signals' / 'semiconductors.json'
    assert wiki_page.exists()
    assert signal_snapshot.exists()
    assert 'Semiconductors: NVIDIA (NVDA) and TSMC are expanding advanced packaging.' in wiki_page.read_text()
    assert '"topic": "semiconductors"' in signal_snapshot.read_text()



def test_show_config_prints_serialized_paths(tmp_path: Path, capsys) -> None:
    assert main(['show-config', '--base-dir', str(tmp_path)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload['paths']['base_dir'] == str(tmp_path)
    assert payload['paths']['state_db'].endswith('data/state/aras.sqlite3')



def test_run_once_with_fixtures_builds_default_pipeline(tmp_path: Path, capsys) -> None:
    fixture_path = Path(__file__).parent / 'fixtures' / 'sample_updates.json'

    assert (
        main(
            [
                'run-once',
                '--channel',
                'DOC_POOL',
                '--base-dir',
                str(tmp_path),
                '--fixtures',
                str(fixture_path),
            ]
        )
        == 0
    )

    output = capsys.readouterr().out.strip()
    assert 'downloaded=1' in output
    assert 'duplicates=1' in output
    assert 'ignored=1' in output
    assert 'wiki_pages=1' in output
    assert 'signal_files=1' in output



def test_auth_login_dispatches_to_telethon_adapter(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[Path, object]] = []
    module = types.ModuleType('analysts.telethon_client')

    def auth_login(*, base_dir: Path, config) -> None:
        calls.append((base_dir, config))

    module.auth_login = auth_login
    monkeypatch.setitem(sys.modules, 'analysts.telethon_client', module)

    assert main(['auth-login', '--base-dir', str(tmp_path)]) == 0
    assert calls and calls[0][0] == tmp_path



def test_telethon_pipeline_seeds_history_then_processes_only_new_posts(tmp_path: Path) -> None:
    messages = [
        {
            'message_id': 100,
            'date': 1713081000,
            'chat': {'title': 'DOC_POOL'},
            'caption': 'Historical AI Capacity Update',
            'document': {
                'file_id': 'telethon-file-100',
                'file_unique_id': 'telethon-100',
                'file_name': 'historical.pdf',
                'mime_type': 'application/pdf',
            },
            'payload': b'Historical content',
        }
    ]
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    client = FakeTelethonClient(messages)
    pipeline = ArasPipeline(client=client, store=store, config=config)

    first_run = pipeline.run_once(channel='DOC_POOL')

    assert first_run.summary.downloaded == 0
    assert first_run.summary.next_offset == 100

    client._messages.append(
        {
            'message_id': 101,
            'date': 1713081060,
            'chat': {'title': 'DOC_POOL'},
            'caption': 'AI Capacity Update',
            'document': {
                'file_id': 'telethon-file-101',
                'file_unique_id': 'telethon-101',
                'file_name': 'ai-capacity-update.pdf',
                'mime_type': 'application/pdf',
            },
            'payload': (
                b'Executive Summary:\nNVIDIA (NVDA) and TSMC are expanding advanced packaging.\n\n'
                b'Risks:\nSupply concentration remains a risk for AI accelerators.'
            ),
        }
    )

    second_run = pipeline.run_once(channel='DOC_POOL')

    assert second_run.summary.downloaded == 1
    assert second_run.summary.next_offset == 101

    wiki_page = tmp_path / 'data' / 'wiki' / 'sector' / 'semiconductors' / 'source-1.md'
    assert wiki_page.exists()
