# ARAS / analysts

Alpha Research Agent System (ARAS) MVP scaffold built only inside `analysts/`.

## Scope
- Fetch new PDF research reports from a Telegram channel via Telethon user-session crawling
- Persist raw artifacts and metadata with duplicate protection
- Parse PDF-like content into structured sections/entities/tickers
- Route reports to sector or macro analyst lanes
- Build deterministic insights, wiki pages, and alpha-signal summaries
- Ship a test-first, modular foundation for later LLM-powered analyst upgrades

## Architecture
- `src/analysts/config.py` — runtime paths + local Telethon settings
- `src/analysts/telethon_client.py` — Telethon auth/session adapter + fixture client
- `src/analysts/fetcher.py` — Bot API fixture polling and Telethon channel crawl pipeline
- `src/analysts/parser.py` — best-effort PDF text extraction + document structuring
- `src/analysts/router.py` — sector/macro routing rules
- `src/analysts/agents.py` — deterministic analyst + coordinator agents
- `src/analysts/wiki.py` — deterministic markdown wiki emission + idempotent index updates
- `src/analysts/signal.py` — repeated-keyword/conflict signal snapshots with idempotent JSON writes
- `src/analysts/storage.py` — SQLite-backed run state and dedupe ledger
- `src/analysts/pipeline.py` — end-to-end orchestration with new-post-only Telethon seeding
- `src/analysts/cli.py` — CLI entrypoint for config inspection, auth login, and run-once execution

## Local secret setup
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
  }
}
```

Telethon session files are stored under `analysts/data/state/` and ignored by git.

## CLI
All paths below are relative to `analysts/` after `cd analysts`.

```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli show-config
PYTHONPATH=src ../.venv/bin/python -m analysts.cli auth-login
PYTHONPATH=src ../.venv/bin/python -m analysts.cli run-once --channel DOC_POOL
```

### First login
- `auth-login` sends a Telegram code to the configured phone number.
- If the account uses Telegram 2FA, the CLI prompts for the password.
- After that, the saved local session is reused for future runs.

### Crawl semantics
- First Telethon run in `new posts only` mode seeds `last_seen_message_id` to the current latest channel message without backfilling history.
- Later runs download only messages newer than that stored id.
- State advances only after a message is ignored, skipped as a duplicate, or downloaded/persisted successfully.

## Fixture smoke path
For deterministic fixture verification without real Telegram auth:

```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli run-once --channel DOC_POOL --fixtures tests/fixtures/sample_updates.json
```

## Verification
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/pytest tests -q
```
