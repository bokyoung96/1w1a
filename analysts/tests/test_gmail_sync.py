from pathlib import Path

from analysts.config import BodyCandidateRules, build_config
from analysts.domain import AnalystSummary
from analysts.pipeline import ArasPipeline
from analysts.sources.gmail.storage import GmailStore
from analysts.sources.gmail.models import GmailMessageRecord
from analysts.sources.gmail.pipeline import GmailSourcePipeline
from analysts.sources.gmail.sync import GmailPollingSync
from analysts.storage import SqliteArasStore


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


class FakeSummarizer:
    @staticmethod
    def lane_plan(packet) -> list[tuple[str, str]]:
        return [("sector", "general"), ("macro", "general")]

    def summarize(self, *, packet, lane: str, topic: str) -> AnalystSummary:
        return AnalystSummary(
            lane=lane,
            topic=topic,
            headline=f"{lane} headline",
            executive_summary=f"{lane} summary",
            key_points=[f"{lane} point"],
            key_numbers=["42%"],
            risks=[f"{lane} risk"],
            confidence="medium",
            cited_pages=[1],
            follow_up_questions=[f"{lane} question"],
        )


def test_polling_sync_records_new_messages(tmp_path) -> None:
    store = GmailStore(tmp_path / "gmail.sqlite3")
    sync = GmailPollingSync(api=FakeGmailApi(), store=store, account_name="reports-primary", query="label:broker-reports")

    result = sync.sync_once(limit=10)

    assert result.fetched == 1
    assert store.get_message("msg-1").subject == "Morning wrap"
    assert store.get_sync_state("reports-primary").last_history_id == "200"


def test_gmail_source_pipeline_summarizes_latest_body_candidate(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    gmail_store = GmailStore(tmp_path / "gmail.sqlite3")
    gmail_store.record_message(
        GmailMessageRecord(
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
            raw_payload_json={"id": "msg-1"},
            sync_status="synced",
            query_fingerprint="label:broker-reports",
        )
    )
    analysts_pipeline = ArasPipeline(
        client=object(),
        store=SqliteArasStore(config.paths.state_db),
        config=config,
        summarizer=FakeSummarizer(),
    )
    source_pipeline = GmailSourcePipeline(
        config=config,
        api=FakeGmailApi(),
        store=gmail_store,
        analysts_pipeline=analysts_pipeline,
        account_name="reports-primary",
        query="label:broker-reports",
        body_rules=BodyCandidateRules(min_chars=200, require_structure=True),
        zip_allow_extensions=(".pdf", ".txt", ".html"),
    )

    execution = source_pipeline.summarize_latest()

    assert len(execution.summaries) == 2
    assert execution.summary.next_offset == "msg-1"
