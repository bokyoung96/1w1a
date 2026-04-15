# ARAS / analysts

Alpha Research Agent System (ARAS) workspace built only inside `analysts/`.

## What works now
- Telethon-based Telegram crawling for `DOC_POOL`
- Raw PDF persistence under `data/raw/`
- Token-cheap LLM analyst summaries via local `codex exec`
- Processed artifacts under `data/processed/`
- Saved local Telethon session under `data/state/`

## In-flight PDF ingestion contract
The current runtime still uses the lightweight summary extractor, but the active PDF-ingestion lane is targeting a richer artifact contract inside `analysts/` only:

- raw PDFs stay in `data/raw/` as the source of truth
- processed artifacts become inspectable per report under `data/processed/`
- summaries should read chunked PDF content when full extraction succeeds
- future command surface:
  - `ingest-pdf --path ...`
  - `summarize-latest --channel DOC_POOL`
  - `summarize-recent --channel DOC_POOL --limit 10`

Planned processed artifact set:
- `data/processed/*-fulltext.txt`
- `data/processed/*-extraction.json`
- `data/processed/*-images.json`
- `data/processed/*-chunks.json`
- `data/processed/*-summary-input.json`
- `data/processed/*-summary.json`
- `data/processed/*-summary.md`

Until that work lands, the current summarized path still emits `*-raw-text.txt` plus summary input/output artifacts.

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

### 4) Watch for new reports until a deadline
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli watch-until \
  --channel DOC_POOL \
  --until 2026-04-15T17:30:00+09:00
```

### 4a) Easier launcher from repo root
```bash
cd /Users/bkchoi/Desktop/GitHub/1w1a
.venv/bin/python analysts/run_watcher.py --until 2026-04-15T17:30:00+09:00
```

- deadline must be timezone-aware ISO-8601
- new unique PDF reports are downloaded once and summarized immediately
- summarize failures retry immediately without stopping the watch loop
- no new messages are accepted after the deadline; any report already accepted before cutoff is allowed to finish processing
- progress logs stream to stdout and `analysts/data/state/watch-runner.log`
- heartbeat logs show liveness while the watcher is idle

## Active pipeline map
The live analysts path is intentionally narrow:

1. `cli.py` — command entrypoints and wiring
2. `telethon_client.py` + `fetcher.py` — Telegram auth/crawl/download
3. `pipeline.py` — top-level orchestration
4. `parser.py` + `router.py` — route hints for a report
5. `pdf_ingest.py` — PDF extraction, chunks, page selection, preview artifacts
6. `summarizer.py` — Codex-backed sector/macro summaries
7. `summary_outputs.py` — persisted summary JSON/Markdown artifacts
8. `graphify.py` — optional graphify corpus refresh from processed summaries

Legacy wiki/signal/coordinator modules were removed from the active package surface because they were no longer part of the current production pipeline.

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

## PDF ingestion design references
- `docs/2026-04-15-pdf-ingestion-review.md` — current gap analysis, integration risks, and merge checklist for the ingestion upgrade
- `docs/openclaw-integration.md` — stable command-oriented interface that future OpenClaw automation should call

## Notes
- Generated data is gitignored but still available for inspection locally.
- Telethon session files stay under `data/state/` and are gitignored.
- The local `pyaes` shim exists only to satisfy Telethon import behavior in this environment while `cryptg` handles the actual crypto path.

## Verification
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/pytest tests -q
```

## Graphify wiki/update
```bash
cd analysts
PYTHONPATH=src ../.venv/bin/python -m analysts.cli graphify-update
```

This builds a graphify-ready corpus from processed summary artifacts so a future graphify/OpenClaw layer can update incrementally as new reports are processed.
