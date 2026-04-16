from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import zipfile

from analysts.config import BodyCandidateRules

from .models import GmailAttachmentRecord, GmailCandidateDocument, GmailMessageRecord


class GmailCandidateBuilder:
    def __init__(
        self,
        output_dir: Path,
        *,
        body_rules: BodyCandidateRules,
        zip_allow_extensions: tuple[str, ...],
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.body_rules = body_rules
        self.zip_allow_extensions = tuple(ext.lower() for ext in zip_allow_extensions)

    def build_candidates(
        self,
        *,
        message: GmailMessageRecord,
        attachments: list[GmailAttachmentRecord],
    ) -> list[GmailCandidateDocument]:
        candidates: list[GmailCandidateDocument] = []
        body_candidate = self._build_body_candidate(message)
        if body_candidate is not None:
            candidates.append(body_candidate)
        for attachment in attachments:
            candidates.extend(
                self.extract_attachment_candidates(
                    message_id=message.gmail_message_id,
                    thread_id=message.gmail_thread_id,
                    attachment=attachment,
                )
            )
        return candidates

    def extract_attachment_candidates(
        self,
        *,
        message_id: str,
        thread_id: str | None,
        attachment: GmailAttachmentRecord,
    ) -> list[GmailCandidateDocument]:
        if attachment.is_zip:
            return self._extract_zip_candidates(message_id=message_id, thread_id=thread_id, attachment=attachment)
        return []

    def _build_body_candidate(self, message: GmailMessageRecord) -> GmailCandidateDocument | None:
        text = (message.body_plain or "").strip()
        if len(text) < self.body_rules.min_chars:
            return None
        if self.body_rules.require_structure and "\n\n" not in text:
            return None
        body_hash = sha256(text.encode("utf-8")).hexdigest()
        body_path = self.output_dir / f"{message.gmail_message_id}-body.txt"
        body_path.write_text(text)
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
            raw_path=body_path,
            normalized_text_path=body_path,
            status="ready",
        )

    def _extract_zip_candidates(
        self,
        *,
        message_id: str,
        thread_id: str | None,
        attachment: GmailAttachmentRecord,
    ) -> list[GmailCandidateDocument]:
        candidates: list[GmailCandidateDocument] = []
        extract_dir = self.output_dir / f"{message_id}-{attachment.attachment_id}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(attachment.raw_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                extension = Path(member.filename).suffix.lower()
                if extension not in self.zip_allow_extensions:
                    continue
                entry_bytes = archive.read(member.filename)
                target_path = extract_dir / Path(member.filename).name
                target_path.write_bytes(entry_bytes)
                entry_hash = sha256(entry_bytes).hexdigest()
                candidates.append(
                    GmailCandidateDocument(
                        candidate_id=f"zip::{message_id}::{attachment.attachment_id}::{member.filename}",
                        gmail_message_id=message_id,
                        gmail_thread_id=thread_id,
                        candidate_kind=f"zip_entry_{extension.lstrip('.')}",
                        source_path=f"zip://{attachment.attachment_id}/{member.filename}",
                        title=Path(member.filename).name,
                        mime_type=_mime_type_for_extension(extension),
                        dedupe_key=f"zip-entry::{message_id}::{attachment.attachment_id}::{member.filename}::{entry_hash}",
                        sha256=entry_hash,
                        promotion_reason="zip_allowlist",
                        raw_path=target_path,
                        normalized_text_path=target_path if extension in {".txt", ".html"} else None,
                        status="ready",
                    )
                )
        return candidates


def _mime_type_for_extension(extension: str) -> str:
    return {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".html": "text/html",
    }[extension]
