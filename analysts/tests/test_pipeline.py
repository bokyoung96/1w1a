from pathlib import Path

from analysts.config import build_config
from analysts.pipeline import ArasPipeline
from analysts.storage import SqliteArasStore


class FakeTelegramClient:
    def __init__(self, updates: list[dict], file_payloads: dict[str, bytes]) -> None:
        self._updates = updates
        self._file_payloads = file_payloads

    def get_updates(self, *, offset: int | None, limit: int) -> list[dict]:
        return [update for update in self._updates if offset is None or update["update_id"] >= offset][:limit]

    @staticmethod
    def get_file(file_id: str) -> dict[str, str]:
        return {"file_path": f"docs/{file_id}.pdf"}

    def download_file(self, file_path: str) -> bytes:
        return self._file_payloads[Path(file_path).stem]


def test_runs_fetch_parse_route_analyze_wiki_and_signal_end_to_end(tmp_path: Path) -> None:
    updates = [
        {
            "update_id": 100,
            "channel_post": {
                "message_id": 501,
                "date": 1713081000,
                "chat": {"id": -1001234567890, "title": "DOC_POOL"},
                "caption": "AI Capacity Update",
                "document": {
                    "file_id": "file-001",
                    "file_unique_id": "uniq-001",
                    "file_name": "ai-capacity-update.pdf",
                    "mime_type": "application/pdf",
                },
            },
        }
    ]
    file_payloads = {
        "file-001": (
            b"Executive Summary:\nNVIDIA (NVDA) and TSMC are expanding advanced packaging.\n\n"
            b"Risks:\nSupply concentration remains a risk for AI accelerators."
        )
    }
    config = build_config(tmp_path)
    store = SqliteArasStore(config.paths.state_db)
    pipeline = ArasPipeline(
        client=FakeTelegramClient(updates, file_payloads),
        store=store,
        config=config,
    )

    first_run = pipeline.run_once(channel="DOC_POOL")
    second_run = pipeline.run_once(channel="DOC_POOL")

    assert first_run.downloaded == 1
    assert first_run.duplicates == 0
    assert first_run.ignored == 0
    assert first_run.next_offset == 101

    assert second_run.downloaded == 0
    assert second_run.duplicates == 0
    assert second_run.next_offset == 101

    wiki_page = tmp_path / "data" / "wiki" / "sector" / "semiconductors" / "source-1.md"
    signal_snapshot = tmp_path / "data" / "signals" / "semiconductors.json"
    assert wiki_page.exists()
    assert signal_snapshot.exists()
    assert "Semiconductors: NVIDIA (NVDA) and TSMC are expanding advanced packaging." in wiki_page.read_text()
    assert '"topic": "semiconductors"' in signal_snapshot.read_text()
