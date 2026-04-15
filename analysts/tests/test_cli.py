import json
import subprocess
import sys
import types
from pathlib import Path

from analysts.cli import build_default_pipeline, main



def test_show_config_redacts_local_telethon_secrets(tmp_path: Path, capsys) -> None:
    (tmp_path / 'config.local.json').write_text(
        json.dumps(
            {
                'telegram': {
                    'mode': 'telethon',
                    'api_id': 123456,
                    'api_hash': 'super-secret-hash',
                    'phone_number': '+821012345678',
                    'channel': 'DOC_POOL',
                    'session_name': 'doc-pool',
                }
            }
        )
    )

    exit_code = main(['show-config', '--base-dir', str(tmp_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload['telethon']['api_hash'] == '<redacted>'
    assert payload['telethon']['channel'] == 'DOC_POOL'


def test_build_default_pipeline_prefers_fixture_client_when_fixture_path_is_set(
    tmp_path: Path,
    monkeypatch,
) -> None:
    fixture_calls: list[Path] = []
    live_calls: list[tuple[Path, object]] = []
    fixture_client = object()
    live_client = object()
    module = types.ModuleType('analysts.telethon_client')

    class FixtureTelegramClient:
        @classmethod
        def from_fixture_path(cls, fixture_path: Path):
            fixture_calls.append(fixture_path)
            return fixture_client

    class TelethonChannelClient:
        def __init__(self, *, base_dir: Path, config) -> None:
            live_calls.append((base_dir, config))

        def __new__(cls, *args, **kwargs):
            instance = super().__new__(cls)
            return live_client

    module.auth_login = lambda **kwargs: None
    module.FixtureTelegramClient = FixtureTelegramClient
    module.TelethonChannelClient = TelethonChannelClient
    monkeypatch.setitem(sys.modules, 'analysts.telethon_client', module)

    pipeline = build_default_pipeline(base_dir=tmp_path, fixtures_path='fixtures/sample.json')

    assert pipeline.client is fixture_client
    assert fixture_calls == [Path('fixtures/sample.json')]
    assert live_calls == []


def test_graphify_update_command_prints_manifest_summary(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    processed_dir = tmp_path / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    (processed_dir / 'report-1-summary.json').write_text(
        json.dumps(
            {
                'report_title': 'Report Title',
                'message_id': 123,
                'raw_pdf_path': 'data/raw/sample.pdf',
                'important_pages': [1],
                'summaries': [
                    {
                        'lane': 'sector',
                        'headline': 'Headline',
                        'confidence': 'high',
                        'cited_pages': [1],
                        'executive_summary': 'Summary body',
                        'key_points': ['A'],
                        'key_numbers': ['10%'],
                        'risks': ['Risk'],
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args=kwargs.get('args', args[0] if args else []), returncode=0)

    monkeypatch.setattr('analysts.graphify.subprocess.run', fake_run)

    assert main(['graphify-update', '--base-dir', str(tmp_path)]) == 0

    output = capsys.readouterr().out.strip()
    assert 'reports=1' in output
    assert 'graphify_invoked=true' in output
    assert 'manifest=' in output
