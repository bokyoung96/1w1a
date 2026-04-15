import json
from pathlib import Path

from analysts.cli import main



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
