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
- `src/analysts/config.py` — runtime paths + polling settings
- `src/analysts/domain.py` — shared contracts for reports, parsed docs, insights, and signals
- `src/analysts/fetcher.py` — Telegram polling + PDF download pipeline
- `src/analysts/parser.py` — best-effort PDF text extraction + document structuring
- `src/analysts/router.py` — sector/macro routing rules
- `src/analysts/agents.py` — deterministic analyst + coordinator agents
- `src/analysts/wiki.py` — deterministic markdown wiki emission + idempotent index updates
- `src/analysts/signal.py` — repeated-keyword/conflict signal snapshots with idempotent JSON writes
- `src/analysts/storage.py` — SQLite-backed run state and dedupe ledger
- `src/analysts/pipeline.py` — end-to-end orchestration with degraded-output fallback handling
- `src/analysts/cli.py` — CLI entrypoint for config inspection and merged runtime orchestration

## Quick start

```bash
cd analysts
../.venv/bin/pytest -q
PYTHONPATH=src ../.venv/bin/python -m analysts.cli show-config
PYTHONPATH=src ../.venv/bin/python -m analysts.cli run-once --channel DOC_POOL --fixtures tests/fixtures/sample_updates.json
```

## Verification
All paths below are relative to `analysts/` after `cd analysts`.

```bash
PYTHONPATH=src ../.venv/bin/pytest tests/test_fetcher.py tests/test_storage.py -q
PYTHONPATH=src ../.venv/bin/pytest tests/test_wiki.py tests/test_signal.py tests/test_pipeline.py -q
PYTHONPATH=src ../.venv/bin/pytest tests -q
```

## Notes
- The Telegram integration uses a small Bot API adapter so the MVP stays dependency-light.
- PDF extraction is intentionally best-effort and deterministic; swap the extractor behind the same interface when a stronger parser is approved.
- The parser contract is explicit: text-heavy reports return `parse_quality="high"`, while undecodable payloads return `parse_quality="degraded"`, empty structures, and a `degraded_reason` instead of failing the run.
- Routing stays deterministic and token-based so sector keywords do not trigger on incidental substrings (for example `"ai"` inside `"daily"`).
- All generated runtime artifacts stay inside `analysts/data/`.

## Focused verification commands

```bash
cd analysts
PYTHONPATH=src ../.venv/bin/pytest tests/test_parser.py -q
PYTHONPATH=src ../.venv/bin/pytest tests/test_router.py -q
PYTHONPATH=src ../.venv/bin/pytest tests/test_agents.py -q
PYTHONPATH=src ../.venv/bin/pytest tests -q
```
