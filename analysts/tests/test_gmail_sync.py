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


def test_polling_sync_records_new_messages(tmp_path) -> None:
    store = GmailStore(tmp_path / "gmail.sqlite3")
    sync = GmailPollingSync(api=FakeGmailApi(), store=store, account_name="reports-primary", query="label:broker-reports")

    result = sync.sync_once(limit=10)

    assert result.fetched == 1
    assert store.get_message("msg-1").subject == "Morning wrap"
    assert store.get_sync_state("reports-primary").last_history_id == "200"
