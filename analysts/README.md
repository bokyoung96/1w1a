# ARAS / analysts

Alpha Research Agent System (ARAS) MVP scaffold built only inside `analysts/`.

## Scope
- Fetch new PDF research reports from a Telegram channel via Bot API-compatible polling
- Persist raw artifacts and metadata with duplicate protection
- Parse PDF-like content into structured sections/entities/tickers
- Route reports to sector or macro analyst lanes
- Build deterministic insights, wiki pages, and alpha-signal summaries
- Ship a test-first, modular foundation for later LLM-powered analyst upgrades

## Architecture
- `src/analysts/fetcher.py` — Telegram polling + PDF download pipeline
- `src/analysts/parser.py` — best-effort PDF text extraction + document structuring
- `src/analysts/router.py` — sector/macro routing rules
- `src/analysts/agents.py` — deterministic analyst + coordinator agents
- `src/analysts/wiki.py` — markdown wiki emission
- `src/analysts/signal.py` — repeated-keyword/conflict signal detection
- `src/analysts/storage.py` — SQLite-backed run state and dedupe ledger
- `src/analysts/pipeline.py` — end-to-end orchestration
- `src/analysts/cli.py` — CLI entrypoint

## Quick start

```bash
cd analysts
../.venv/bin/pytest -q
PYTHONPATH=src ../.venv/bin/python -m analysts.cli run-once --channel DOC_POOL --fixtures tests/fixtures/sample_updates.json
```

## Notes
- The Telegram integration uses a small Bot API adapter so the MVP stays dependency-light.
- PDF extraction is intentionally best-effort and deterministic; swap the extractor behind the same interface when a stronger parser is approved.
- All generated runtime artifacts stay inside `analysts/data/`.
