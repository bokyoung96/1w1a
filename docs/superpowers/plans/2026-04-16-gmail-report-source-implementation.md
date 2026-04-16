# Gmail Report Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Gmail source to `analysts/` that keeps Telegram and Gmail strongly separated at the ingestion/state layer, turns one Gmail message into one or more candidate documents, and routes canonical documents into the existing shared summarize path without breaking Telegram.

**Architecture:** Build a new `analysts.sources.gmail` package that owns Gmail OAuth, mailbox sync, candidate-document generation, and Gmail-specific persistence. Keep Telegram untouched except where shared CLI/config plumbing needs source selection; once Gmail candidates are normalized into canonical documents, reuse the existing analysis pipeline by extending it to accept both PDF-backed and text-backed canonical inputs.

**Tech Stack:** Python 3.11, Gmail API + OAuth, sqlite3, pytest, dataclasses, argparse, existing analysts PDF/text summarization pipeline

---

## File Structure

- Create: `analysts/src/analysts/sources/__init__.py`
  Namespace package for source-specific ingestion code.
- Create: `analysts/src/analysts/sources/gmail/__init__.py`
  Export Gmail source entry points.
- Create: `analysts/src/analysts/sources/gmail/models.py`
  Gmail message, attachment, candidate-document, and canonical-document dataclasses.
- Create: `analysts/src/analysts/sources/gmail/storage.py`
  Gmail-specific SQLite store for messages, attachments, candidates, and sync state.
- Create: `analysts/src/analysts/sources/gmail/client.py`
  OAuth token management and Gmail API wrapper.
- Create: `analysts/src/analysts/sources/gmail/sync.py`
  Polling sync runner that lists messages, fetches payloads, and persists raw Gmail message records.
- Create: `analysts/src/analysts/sources/gmail/normalize.py`
  Body-promotion rules, attachment classification, ZIP allowlist extraction, candidate generation, canonical-document conversion.
- Create: `analysts/src/analysts/sources/gmail/pipeline.py`
  Gmail source orchestration from sync to summarize-ready canonical documents.
- Modify: `analysts/src/analysts/config.py`
  Add `GmailConfig` and Gmail-specific paths/settings.
- Modify: `analysts/src/analysts/domain.py`
  Add canonical-document types or extend shared pipeline input contracts.
- Modify: `analysts/src/analysts/pipeline.py`
  Accept canonical Gmail documents and route text-backed inputs through a non-PDF summary path.
- Modify: `analysts/src/analysts/cli.py`
  Add `gmail-auth-login`, `gmail-sync-once`, `gmail-sync-recent`, `gmail-summarize-latest`, `gmail-summarize-recent` commands.
- Modify: `analysts/README.md`
  Document Gmail config, sync commands, and the source-separation model.
- Test: `analysts/tests/test_config.py`
  Add Gmail config loading coverage.
- Create: `analysts/tests/test_gmail_storage.py`
  Cover Gmail message/candidate schema and sync state persistence.
- Create: `analysts/tests/test_gmail_normalize.py`
  Cover body promotion, attachment handling, ZIP allowlist extraction, and candidate-level dedupe.
- Create: `analysts/tests/test_gmail_sync.py`
  Cover Gmail API polling flow with fixtures.
- Create: `analysts/tests/test_gmail_cli.py`
  Cover Gmail command surface.
- Modify: `analysts/tests/test_pipeline.py`
  Add canonical-document summarize coverage for Gmail-backed text and PDF candidates.

## Task 1: Add Gmail Config And Shared Canonical Document Types

**Files:**
- Modify: `analysts/src/analysts/config.py`
- Modify: `analysts/src/analysts/domain.py`
- Test: `analysts/tests/test_config.py`

- [ ] **Step 1: Write the failing config and canonical-type tests**

```python
# analysts/tests/test_config.py
from pathlib import Path

from analysts.config import build_config


def test_build_config_loads_gmail_settings(tmp_path: Path) -> None:
    (tmp_path / "config.local.json").write_text(
        """
        {
          "gmail": {
            "account_name": "reports-primary",
            "client_secret_path": "secrets/gmail-client.json",
            "token_path": "secrets/gmail-token.json",
            "query": "label:broker-reports newer_than:14d",
            "body_candidate_rules": {"min_chars": 800, "require_structure": true},
            "zip_allow_extensions": [".pdf", ".txt", ".html"],
            "poll_interval_seconds": 300
          }
        }
        """.strip()
    )

    config = build_config(tmp_path)

    assert config.gmail is not None
    assert config.gmail.account_name == "reports-primary"
    assert config.gmail.query == "label:broker-reports newer_than:14d"
    assert config.gmail.body_candidate_rules.min_chars == 800
    assert config.gmail.zip_allow_extensions == (".pdf", ".txt", ".html")


# analysts/tests/test_pipeline.py
from analysts.domain import CanonicalDocument


def test_canonical_document_supports_gmail_body_source(tmp_path: Path) -> None:
    document = CanonicalDocument(
        source="gmail",
        source_message_id="msg-1",
        source_thread_id="thread-1",
        source_feed="reports-primary",
        document_kind="email_body",
        title="Morning broker wrap",
        published_at="2026-04-16T06:00:00Z",
        sender_or_origin="broker@example.com",
        mime_type="text/plain",
        dedupe_key="body::msg-1::hash",
        raw_path=tmp_path / "raw.txt",
        normalized_text_path=tmp_path / "normalized.txt",
        metadata={"label_ids": ["Label_Reports"]},
    )

    assert document.source == "gmail"
    assert document.document_kind == "email_body"
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_config.py tests/test_pipeline.py -q`

Expected: FAIL because `GmailConfig`, `BodyCandidateRules`, and `CanonicalDocument` do not exist yet.

- [ ] **Step 3: Add Gmail config structures and canonical document dataclass**

```python
# analysts/src/analysts/config.py
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BodyCandidateRules:
    min_chars: int = 800
    require_structure: bool = True


@dataclass(frozen=True)
class GmailConfig:
    account_name: str
    client_secret_path: Path
    token_path: Path
    query: str
    label_filters: tuple[str, ...] = ()
    body_candidate_rules: BodyCandidateRules = BodyCandidateRules()
    zip_allow_extensions: tuple[str, ...] = (".pdf", ".txt", ".html")
    poll_interval_seconds: int = 300


@dataclass(frozen=True)
class ArasConfig:
    paths: ArasPaths
    polling_limit: int = 100
    telethon: TelethonConfig | None = None
    gmail: GmailConfig | None = None
    summary: SummaryConfig = SummaryConfig()
```

```python
# analysts/src/analysts/domain.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CanonicalDocument:
    source: str
    source_message_id: str
    source_thread_id: str | None
    source_feed: str
    document_kind: str
    title: str
    published_at: str | None
    sender_or_origin: str | None
    mime_type: str
    dedupe_key: str
    raw_path: Path
    normalized_text_path: Path | None
    metadata: dict[str, Any] = field(default_factory=dict)
```

- [ ] **Step 4: Run the focused tests again and verify they pass**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_config.py tests/test_pipeline.py -q`

Expected: PASS for Gmail config loading and canonical document construction.

- [ ] **Step 5: Commit the shared Gmail config/type changes**

```bash
git add analysts/src/analysts/config.py analysts/src/analysts/domain.py analysts/tests/test_config.py analysts/tests/test_pipeline.py
git commit -m "Add Gmail config and canonical document contracts"
```

## Task 2: Add Gmail Storage Schema And Sync State Persistence

**Files:**
- Create: `analysts/src/analysts/sources/__init__.py`
- Create: `analysts/src/analysts/sources/gmail/__init__.py`
- Create: `analysts/src/analysts/sources/gmail/models.py`
- Create: `analysts/src/analysts/sources/gmail/storage.py`
- Create: `analysts/tests/test_gmail_storage.py`

- [ ] **Step 1: Write the failing Gmail storage tests**

```python
# analysts/tests/test_gmail_storage.py
from pathlib import Path

from analysts.sources.gmail.models import GmailCandidateDocument, GmailMessageRecord
from analysts.sources.gmail.storage import GmailStore


def test_gmail_store_persists_message_candidate_and_history_state(tmp_path: Path) -> None:
    store = GmailStore(tmp_path / "gmail.sqlite3")
    message = GmailMessageRecord(
        gmail_message_id="msg-1",
        gmail_thread_id="thread-1",
        history_id="200",
        account_name="reports-primary",
        subject="Morning wrap",
        sender="broker@example.com",
        internal_date="2026-04-16T06:00:00Z",
        label_ids=("Label_Reports",),
        snippet="Top line",
        body_plain="Structured report body",
        body_html=None,
        raw_payload_json={"id": "msg-1"},
        sync_status="synced",
        query_fingerprint="qhash",
    )
    candidate = GmailCandidateDocument(
        candidate_id="cand-1",
        gmail_message_id="msg-1",
        gmail_thread_id="thread-1",
        candidate_kind="email_body",
        source_path="body://msg-1",
        title="Morning wrap",
        mime_type="text/plain",
        dedupe_key="body::msg-1::hash",
        sha256="hash",
        promotion_reason="body_rule:structured",
        raw_path=Path("raw/body.txt"),
        normalized_text_path=Path("processed/body.txt"),
        status="ready",
    )

    store.record_message(message)
    store.record_candidate(candidate)
    store.set_sync_state(account_name="reports-primary", last_history_id="200", full_sync_required=False)

    assert store.get_message("msg-1").subject == "Morning wrap"
    assert store.list_candidates_for_message("msg-1")[0].candidate_kind == "email_body"
    assert store.get_sync_state("reports-primary").last_history_id == "200"
```

- [ ] **Step 2: Run the storage test and confirm it fails**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_gmail_storage.py -q`

Expected: FAIL because the Gmail source package and store types are missing.

- [ ] **Step 3: Implement Gmail records and SQLite schema**

```python
# analysts/src/analysts/sources/gmail/models.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GmailMessageRecord:
    gmail_message_id: str
    gmail_thread_id: str
    history_id: str
    account_name: str
    subject: str
    sender: str | None
    internal_date: str | None
    label_ids: tuple[str, ...]
    snippet: str
    body_plain: str | None
    body_html: str | None
    raw_payload_json: dict[str, Any]
    sync_status: str
    query_fingerprint: str


@dataclass(frozen=True)
class GmailCandidateDocument:
    candidate_id: str
    gmail_message_id: str
    gmail_thread_id: str | None
    candidate_kind: str
    source_path: str
    title: str
    mime_type: str
    dedupe_key: str
    sha256: str
    promotion_reason: str | None
    raw_path: Path
    normalized_text_path: Path | None
    status: str
```

```python
# analysts/src/analysts/sources/gmail/storage.py
class GmailStore:
    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS gmail_messages (
                    gmail_message_id TEXT PRIMARY KEY,
                    gmail_thread_id TEXT NOT NULL,
                    history_id TEXT NOT NULL,
                    account_name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    sender TEXT,
                    internal_date TEXT,
                    label_ids_json TEXT NOT NULL,
                    snippet TEXT NOT NULL,
                    body_plain TEXT,
                    body_html TEXT,
                    raw_payload_json TEXT NOT NULL,
                    sync_status TEXT NOT NULL,
                    query_fingerprint TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS gmail_candidate_documents (
                    candidate_id TEXT PRIMARY KEY,
                    gmail_message_id TEXT NOT NULL,
                    gmail_thread_id TEXT,
                    candidate_kind TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    dedupe_key TEXT NOT NULL UNIQUE,
                    sha256 TEXT NOT NULL,
                    promotion_reason TEXT,
                    raw_path TEXT NOT NULL,
                    normalized_text_path TEXT,
                    status TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS gmail_sync_state (
                    account_name TEXT PRIMARY KEY,
                    last_history_id TEXT,
                    full_sync_required INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
```

- [ ] **Step 4: Run the storage test again and verify it passes**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_gmail_storage.py -q`

Expected: PASS with message, candidate, and sync-state round-trip coverage.

- [ ] **Step 5: Commit the Gmail storage layer**

```bash
git add analysts/src/analysts/sources/__init__.py analysts/src/analysts/sources/gmail/__init__.py analysts/src/analysts/sources/gmail/models.py analysts/src/analysts/sources/gmail/storage.py analysts/tests/test_gmail_storage.py
git commit -m "Add Gmail source storage schema"
```

## Task 3: Implement Gmail Polling Sync And OAuth Client

**Files:**
- Create: `analysts/src/analysts/sources/gmail/client.py`
- Create: `analysts/src/analysts/sources/gmail/sync.py`
- Create: `analysts/tests/test_gmail_sync.py`

- [ ] **Step 1: Write the failing Gmail sync tests**

```python
# analysts/tests/test_gmail_sync.py
from pathlib import Path

from analysts.sources.gmail.models import GmailMessageRecord
from analysts.sources.gmail.storage import GmailStore
from analysts.sources.gmail.sync import GmailPollingSync


class FakeGmailApi:
    def list_message_ids(self, *, query: str, page_token: str | None = None, limit: int = 50):
        return {"messages": [{"id": "msg-1", "threadId": "thread-1"}], "next_page_token": None}

    def get_message(self, *, message_id: str) -> dict:
        return {
            "id": "msg-1",
            "threadId": "thread-1",
            "historyId": "200",
            "labelIds": ["Label_Reports"],
            "snippet": "Morning wrap",
            "internalDate": "1713247200000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "broker@example.com"},
                    {"name": "Subject", "value": "Morning wrap"},
                ],
                "mimeType": "text/plain",
                "body": {"data": "U3RydWN0dXJlZCByZXBvcnQgYm9keQ"},
            },
        }


def test_polling_sync_records_new_messages(tmp_path: Path) -> None:
    store = GmailStore(tmp_path / "gmail.sqlite3")
    sync = GmailPollingSync(api=FakeGmailApi(), store=store, account_name="reports-primary", query="label:broker-reports")

    result = sync.sync_once(limit=10)

    assert result.fetched == 1
    assert store.get_message("msg-1").subject == "Morning wrap"
    assert store.get_sync_state("reports-primary").last_history_id == "200"
```

- [ ] **Step 2: Run the sync test and confirm it fails**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_gmail_sync.py -q`

Expected: FAIL because the Gmail API client and polling sync classes are missing.

- [ ] **Step 3: Implement Gmail API wrapper and polling sync**

```python
# analysts/src/analysts/sources/gmail/client.py
class GmailApiClient:
    def __init__(self, *, credentials_path: Path, token_path: Path) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path

    def ensure_authorized(self) -> None:
        # use InstalledAppFlow + token refresh and persist token json
        ...

    def list_message_ids(self, *, query: str, page_token: str | None = None, limit: int = 50) -> dict:
        ...

    def get_message(self, *, message_id: str) -> dict:
        ...
```

```python
# analysts/src/analysts/sources/gmail/sync.py
@dataclass(frozen=True)
class GmailSyncResult:
    fetched: int
    skipped_existing: int
    last_history_id: str | None


class GmailPollingSync:
    def sync_once(self, *, limit: int) -> GmailSyncResult:
        listed = self.api.list_message_ids(query=self.query, limit=limit)
        fetched = 0
        skipped_existing = 0
        last_history_id = None
        for item in listed["messages"]:
            if self.store.get_message(item["id"]) is not None:
                skipped_existing += 1
                continue
            payload = self.api.get_message(message_id=item["id"])
            record = build_message_record(account_name=self.account_name, query=self.query, payload=payload)
            self.store.record_message(record)
            fetched += 1
            last_history_id = payload.get("historyId") or last_history_id
        if last_history_id is not None:
            self.store.set_sync_state(account_name=self.account_name, last_history_id=last_history_id, full_sync_required=False)
        return GmailSyncResult(fetched=fetched, skipped_existing=skipped_existing, last_history_id=last_history_id)
```

- [ ] **Step 4: Run the sync test again and verify it passes**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_gmail_sync.py -q`

Expected: PASS with one fetched message and persisted sync state.

- [ ] **Step 5: Commit the Gmail sync layer**

```bash
git add analysts/src/analysts/sources/gmail/client.py analysts/src/analysts/sources/gmail/sync.py analysts/tests/test_gmail_sync.py
git commit -m "Add Gmail OAuth client and polling sync"
```

## Task 4: Add Candidate Generation, Body Promotion, ZIP Allowlist, And Dedupe

**Files:**
- Create: `analysts/src/analysts/sources/gmail/normalize.py`
- Create: `analysts/tests/test_gmail_normalize.py`

- [ ] **Step 1: Write the failing normalization tests**

```python
# analysts/tests/test_gmail_normalize.py
from pathlib import Path
import io
import zipfile

from analysts.config import BodyCandidateRules
from analysts.sources.gmail.models import GmailAttachmentRecord, GmailMessageRecord
from analysts.sources.gmail.normalize import GmailCandidateBuilder


def test_body_candidate_is_created_only_when_rules_match(tmp_path: Path) -> None:
    message = GmailMessageRecord(
        gmail_message_id="msg-1",
        gmail_thread_id="thread-1",
        history_id="200",
        account_name="reports-primary",
        subject="Morning wrap",
        sender="broker@example.com",
        internal_date="2026-04-16T06:00:00Z",
        label_ids=("Label_Reports",),
        snippet="Top line",
        body_plain="Section A\n\nRevenue up 10%\n\nRisk factors listed below." * 40,
        body_html=None,
        raw_payload_json={},
        sync_status="synced",
        query_fingerprint="qhash",
    )
    builder = GmailCandidateBuilder(tmp_path, body_rules=BodyCandidateRules(min_chars=200, require_structure=True), zip_allow_extensions=(".pdf", ".txt", ".html"))

    candidates = builder.build_candidates(message=message, attachments=[])

    assert [candidate.candidate_kind for candidate in candidates] == ["email_body"]


def test_zip_only_emits_allowlisted_entries(tmp_path: Path) -> None:
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("inside/report.txt", "text report")
        archive.writestr("inside/report.pdf", b"%PDF-1.4 fake")
        archive.writestr("inside/model.xlsx", b"xlsx bytes")

    attachment = GmailAttachmentRecord(
        gmail_message_id="msg-1",
        attachment_id="att-1",
        filename="bundle.zip",
        mime_type="application/zip",
        size_bytes=zip_path.stat().st_size,
        sha256="ziphash",
        raw_path=zip_path,
        is_zip=True,
        extraction_status="stored",
    )

    builder = GmailCandidateBuilder(tmp_path, body_rules=BodyCandidateRules(), zip_allow_extensions=(".pdf", ".txt", ".html"))
    candidates = builder.extract_attachment_candidates(message_id="msg-1", thread_id="thread-1", attachment=attachment)

    assert {candidate.candidate_kind for candidate in candidates} == {"zip_entry_txt", "zip_entry_pdf"}
```

- [ ] **Step 2: Run the normalization tests and confirm they fail**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_gmail_normalize.py -q`

Expected: FAIL because `GmailAttachmentRecord` and `GmailCandidateBuilder` are not implemented yet.

- [ ] **Step 3: Implement attachment/body normalization and dedupe-key generation**

```python
# analysts/src/analysts/sources/gmail/models.py
@dataclass(frozen=True)
class GmailAttachmentRecord:
    gmail_message_id: str
    attachment_id: str
    filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    raw_path: Path
    is_zip: bool
    extraction_status: str
```

```python
# analysts/src/analysts/sources/gmail/normalize.py
class GmailCandidateBuilder:
    def build_candidates(self, *, message: GmailMessageRecord, attachments: list[GmailAttachmentRecord]) -> list[GmailCandidateDocument]:
        candidates: list[GmailCandidateDocument] = []
        body_candidate = self._build_body_candidate(message)
        if body_candidate is not None:
            candidates.append(body_candidate)
        for attachment in attachments:
            candidates.extend(self.extract_attachment_candidates(message_id=message.gmail_message_id, thread_id=message.gmail_thread_id, attachment=attachment))
        return candidates

    def _build_body_candidate(self, message: GmailMessageRecord) -> GmailCandidateDocument | None:
        text = (message.body_plain or "").strip()
        if len(text) < self.body_rules.min_chars:
            return None
        if self.body_rules.require_structure and "\n\n" not in text:
            return None
        body_hash = sha256(text.encode("utf-8")).hexdigest()
        return GmailCandidateDocument(
            candidate_id=f"body::{message.gmail_message_id}",
            gmail_message_id=message.gmail_message_id,
            gmail_thread_id=message.gmail_thread_id,
            candidate_kind="email_body",
            source_path=f"body://{message.gmail_message_id}",
            title=message.subject,
            mime_type="text/plain",
            dedupe_key=f"body::{message.gmail_message_id}::{body_hash}",
            sha256=body_hash,
            promotion_reason="body_rule:structured",
            raw_path=self._write_body_text(message.gmail_message_id, text),
            normalized_text_path=self._write_body_text(message.gmail_message_id, text),
            status="ready",
        )
```

- [ ] **Step 4: Run the normalization tests again and verify they pass**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_gmail_normalize.py -q`

Expected: PASS with body-promotion and ZIP allowlist coverage.

- [ ] **Step 5: Commit the candidate generation layer**

```bash
git add analysts/src/analysts/sources/gmail/models.py analysts/src/analysts/sources/gmail/normalize.py analysts/tests/test_gmail_normalize.py
git commit -m "Add Gmail candidate document normalization"
```

## Task 5: Connect Gmail Candidates To The Shared Summarize Path And CLI

**Files:**
- Create: `analysts/src/analysts/sources/gmail/pipeline.py`
- Modify: `analysts/src/analysts/pipeline.py`
- Modify: `analysts/src/analysts/cli.py`
- Modify: `analysts/README.md`
- Create: `analysts/tests/test_gmail_cli.py`
- Modify: `analysts/tests/test_pipeline.py`

- [ ] **Step 1: Write the failing pipeline and CLI tests**

```python
# analysts/tests/test_pipeline.py
from pathlib import Path

from analysts.domain import CanonicalDocument
from analysts.pipeline import ArasPipeline


def test_pipeline_summarizes_text_backed_canonical_document(tmp_path: Path, fixture_pipeline: ArasPipeline) -> None:
    raw_path = tmp_path / "body.txt"
    raw_path.write_text("Revenue up 10%\n\nMargin stable\n\nRisk: FX")
    document = CanonicalDocument(
        source="gmail",
        source_message_id="msg-1",
        source_thread_id="thread-1",
        source_feed="reports-primary",
        document_kind="email_body",
        title="Morning wrap",
        published_at="2026-04-16T06:00:00Z",
        sender_or_origin="broker@example.com",
        mime_type="text/plain",
        dedupe_key="body::msg-1::hash",
        raw_path=raw_path,
        normalized_text_path=raw_path,
        metadata={},
    )

    execution = fixture_pipeline.summarize_canonical(document)

    assert len(execution.summaries) == 2
    assert execution.summary.next_offset == "msg-1"


# analysts/tests/test_gmail_cli.py
from analysts.cli import main


def test_gmail_sync_once_command_runs(monkeypatch) -> None:
    called = {}

    def fake_run(*, base_dir, limit):
        called["base_dir"] = str(base_dir)
        called["limit"] = limit
        return 0

    monkeypatch.setattr("analysts.cli.run_gmail_sync_once", fake_run)

    exit_code = main(["gmail-sync-once", "--base-dir", "analysts", "--limit", "5"])

    assert exit_code == 0
    assert called == {"base_dir": "analysts", "limit": 5}
```

- [ ] **Step 2: Run the focused tests and confirm they fail**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_pipeline.py tests/test_gmail_cli.py -q`

Expected: FAIL because `summarize_canonical` and Gmail CLI commands do not exist.

- [ ] **Step 3: Implement Gmail source pipeline orchestration and CLI plumbing**

```python
# analysts/src/analysts/pipeline.py
class ArasPipeline:
    def summarize_canonical(self, document: CanonicalDocument) -> PipelineExecution:
        if document.mime_type == "application/pdf":
            report = canonical_document_to_report(document)
            return self.summarize_report(report)

        text = document.normalized_text_path.read_text() if document.normalized_text_path else document.raw_path.read_text()
        report = canonical_text_document_to_report(document=document, text=text)
        parsed = DocumentParser().parse(report)
        routes = TaskRouter().route(parsed)
        packet = SummaryReadyExtractor(self.config).build_packet(report=report, parsed=parsed, routes=routes)
        summaries = self._build_summaries(packet)
        outputs = SummaryArtifactWriter(self.config).write(packet=packet, summaries=summaries)
        return PipelineExecution(
            summary=PipelineRunSummary(downloaded=0, duplicates=0, ignored=0, next_offset=document.source_message_id),
            processed_files=[outputs.json_path, outputs.markdown_path],
            summaries=summaries,
        )
```

```python
# analysts/src/analysts/cli.py
 gmail_auth = subparsers.add_parser("gmail-auth-login")
 gmail_auth.add_argument("--base-dir", default=".")

 gmail_sync_once = subparsers.add_parser("gmail-sync-once")
 gmail_sync_once.add_argument("--base-dir", default=".")
 gmail_sync_once.add_argument("--limit", type=int, default=20)

 gmail_sync_recent = subparsers.add_parser("gmail-sync-recent")
 gmail_sync_recent.add_argument("--base-dir", default=".")
 gmail_sync_recent.add_argument("--limit", type=int, default=20)

 gmail_summarize_latest = subparsers.add_parser("gmail-summarize-latest")
 gmail_summarize_latest.add_argument("--base-dir", default=".")
```

- [ ] **Step 4: Run the focused tests again and verify they pass**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_pipeline.py tests/test_gmail_cli.py -q`

Expected: PASS for Gmail text-backed summarization and CLI command dispatch.

- [ ] **Step 5: Run the broader Gmail-focused regression slice**

Run: `cd analysts && PYTHONPATH=src ../.venv/bin/pytest tests/test_config.py tests/test_gmail_storage.py tests/test_gmail_sync.py tests/test_gmail_normalize.py tests/test_gmail_cli.py tests/test_pipeline.py -q`

Expected: PASS with Gmail schema, sync, normalization, and summarize coverage.

- [ ] **Step 6: Update README and commit the integration surface**

```markdown
# analysts/README.md additions
## Gmail source
- `gmail-auth-login`
- `gmail-sync-once --limit N`
- `gmail-summarize-latest`
- Gmail lives under `data/raw/gmail`, `data/processed/gmail`, and `data/state/gmail.sqlite3`
- One Gmail message can emit multiple candidate documents; body promotion is rule-based and ZIP extraction is allowlisted to PDF/TXT/HTML.
```

```bash
git add analysts/src/analysts/sources/gmail/pipeline.py analysts/src/analysts/pipeline.py analysts/src/analysts/cli.py analysts/README.md analysts/tests/test_gmail_cli.py analysts/tests/test_pipeline.py
git commit -m "Connect Gmail candidates to the shared summarize flow"
```

## Self-Review

### Spec coverage
- Strong Telegram/Gmail separation: Tasks 1-5 keep Gmail inside `sources/gmail` and avoid Telegram fetcher reuse.
- Gmail API + OAuth: Task 3 adds the OAuth client and polling sync.
- One email -> many candidates: Tasks 2 and 4 model Gmail messages, attachments, and candidates separately.
- Rule-based body promotion: Task 4 implements and tests heuristics.
- ZIP allowlist: Task 4 limits ZIP extraction to PDF/TXT/HTML.
- Candidate-level dedupe: Task 2 schema and Task 4 keys encode candidate-level uniqueness.
- Push-friendly polling-first: Task 3 persists sync state and `historyId` without requiring watch/PubSub yet.
- Shared summarize convergence: Task 5 extends `ArasPipeline` to summarize canonical Gmail documents.

### Placeholder scan
- No `TODO` / `TBD` markers remain.
- Each task lists concrete files, tests, commands, and code snippets.

### Type consistency
- `GmailConfig`, `BodyCandidateRules`, `CanonicalDocument`, `GmailMessageRecord`, `GmailAttachmentRecord`, and `GmailCandidateDocument` are introduced before later tasks depend on them.
- `summarize_canonical()` is introduced only after canonical types and Gmail candidate generation are defined.
