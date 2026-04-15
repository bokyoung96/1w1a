# ARAS / analysts

Alpha Research Agent System (ARAS) workspace built only inside `analysts/`.

## What works now
- Telethon-based Telegram crawling for `DOC_POOL`
- Raw PDF persistence under `data/raw/`
- Token-cheap LLM analyst summaries via local `codex exec`
- Processed artifacts under `data/processed/`
- Saved local Telethon session under `data/state/`

## Current workflow
### 1) Authenticate once
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli auth-login
```

### 2) Crawl new posts going forward
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli run-once --channel DOC_POOL
```

### 3) Summarize the latest downloaded report again
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli summarize-latest --channel DOC_POOL
```

## Local config
Create `analysts/config.local.json` (gitignored):

```json
{
  "telegram": {
    "mode": "telethon",
    "api_id": 123456,
    "api_hash": "replace-me",
    "phone_number": "+821012345678",
    "channel": "DOC_POOL",
    "session_name": "doc-pool",
    "pdf_only": true
  },
  "summary": {
    "provider": "codex_cli",
    "model": "gpt-5.4-mini",
    "reasoning_effort": "low",
    "max_input_chars": 3200,
    "max_key_points": 4,
    "cli_command": "codex"
  }
}
```

## Token-cheap summary design
- raw PDF remains the source of truth
- local extraction builds a compact summary packet first
- two concise analyst lanes run per report:
  - sector analyst
  - macro analyst
- no expensive coordinator by default
- processed outputs are easy to inspect:
  - `data/processed/*-raw-text.txt`
  - `data/processed/*-summary-input.json`
  - `data/processed/*-summary.json`
  - `data/processed/*-summary.md`

## Notes
- Generated data is gitignored but still available for inspection locally.
- Telethon session files stay under `data/state/` and are gitignored.
- The local `pyaes` shim exists only to satisfy Telethon import behavior in this environment while `cryptg` handles the actual crypto path.

## Verification
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/pytest tests -q
```
