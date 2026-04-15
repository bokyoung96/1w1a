import json
from pathlib import Path

from analysts.config import build_config



def _write_local_config(base_dir: Path) -> None:
    (base_dir / 'config.local.json').write_text(
        json.dumps(
            {
                'telegram': {
                    'mode': 'telethon',
                    'api_id': 123456,
                    'api_hash': 'super-secret-hash',
                    'phone_number': '+821012345678',
                    'channel': 'DOC_POOL',
                    'session_name': 'doc-pool',
                    'pdf_only': True,
                }
            }
        )
    )



def test_build_config_loads_gitignored_local_telethon_settings(tmp_path: Path) -> None:
    _write_local_config(tmp_path)

    config = build_config(tmp_path)

    assert config.telethon is not None
    assert config.telethon.channel == 'DOC_POOL'
    assert config.telethon.session_name == 'doc-pool'
    assert config.telethon.pdf_only is True
    assert config.paths.local_config_path == tmp_path / 'config.local.json'
    assert config.paths.telethon_session_path == tmp_path / 'data' / 'state' / 'doc-pool.session'



def test_display_payload_redacts_telethon_secrets(tmp_path: Path) -> None:
    _write_local_config(tmp_path)

    config = build_config(tmp_path)
    payload = config.to_display_dict()

    assert payload['telethon']['api_id'] == '<redacted>'
    assert payload['telethon']['api_hash'] == '<redacted>'
    assert payload['telethon']['phone_number'] == '<redacted>'
    assert payload['telethon']['channel'] == 'DOC_POOL'
