from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from analysts.config import ArasConfig, BodyCandidateRules
from analysts.pipeline import ArasPipeline

from .models import GmailCandidateDocument
from .normalize import GmailCandidateBuilder
from .storage import GmailStore
from .sync import GmailPollingSync


@dataclass(frozen=True)
class GmailSourcePipeline:
    config: ArasConfig
    api: object
    store: GmailStore
    analysts_pipeline: ArasPipeline
    account_name: str
    query: str
    body_rules: BodyCandidateRules
    zip_allow_extensions: tuple[str, ...]
    raw_root: Path

    def sync_once(self, *, limit: int):
        return GmailPollingSync(
            api=self.api,
            store=self.store,
            account_name=self.account_name,
            query=self.query,
            raw_root=self.raw_root,
        ).sync_once(limit=limit)

    def summarize_latest(self):
        message = self.store.get_latest_message(account_name=self.account_name)
        if message is None:
            raise RuntimeError(f"No Gmail messages found for account {self.account_name}")
        candidates = GmailCandidateBuilder(
            self.config.paths.processed_dir / "gmail",
            body_rules=self.body_rules,
            zip_allow_extensions=self.zip_allow_extensions,
        ).build_candidates(message=message, attachments=[])
        if not candidates:
            raise RuntimeError(f"No Gmail candidates available for message {message.gmail_message_id}")
        candidate = candidates[0]
        return self.analysts_pipeline.summarize_canonical(_candidate_to_canonical(candidate, account_name=self.account_name))


def _candidate_to_canonical(candidate: GmailCandidateDocument, *, account_name: str):
    from analysts.domain import CanonicalDocument

    return CanonicalDocument(
        source="gmail",
        source_message_id=candidate.gmail_message_id,
        source_thread_id=candidate.gmail_thread_id,
        source_feed=account_name,
        document_kind=candidate.candidate_kind,
        title=candidate.title,
        published_at=None,
        sender_or_origin=None,
        mime_type=candidate.mime_type,
        dedupe_key=candidate.dedupe_key,
        raw_path=candidate.raw_path,
        normalized_text_path=candidate.normalized_text_path,
        metadata={},
    )
