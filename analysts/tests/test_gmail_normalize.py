from pathlib import Path
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
    builder = GmailCandidateBuilder(
        tmp_path,
        body_rules=BodyCandidateRules(min_chars=200, require_structure=True),
        zip_allow_extensions=(".pdf", ".txt", ".html"),
    )

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

    builder = GmailCandidateBuilder(
        tmp_path,
        body_rules=BodyCandidateRules(),
        zip_allow_extensions=(".pdf", ".txt", ".html"),
    )
    candidates = builder.extract_attachment_candidates(message_id="msg-1", thread_id="thread-1", attachment=attachment)

    assert {candidate.candidate_kind for candidate in candidates} == {"zip_entry_txt", "zip_entry_pdf"}
