from pathlib import Path

from analysts.domain import InsightRecord
from analysts.wiki import WikiBuilder


def _make_insight(*, topic: str, lane: str, summary: str, document_id: int) -> InsightRecord:
    return InsightRecord(
        topic=topic,
        lane=lane,
        summary=summary,
        bull_case=f"Upside case: {summary}",
        bear_case="Downside case: Risk disclosures were limited in the parsed document.",
        confidence="high",
        key_drivers=["NVDA", "TSM"],
        risk_factors=["Risk disclosures were limited in the parsed document."],
        source_document_id=document_id,
    )


def test_writes_deterministic_wiki_pages_and_keeps_index_idempotent(tmp_path: Path) -> None:
    builder = WikiBuilder(base_dir=tmp_path)
    insight = _make_insight(
        topic="semiconductors",
        lane="sector",
        summary="Semiconductors: NVIDIA and TSMC are expanding advanced packaging.",
        document_id=7,
    )

    first_result = builder.materialize([insight])
    second_result = builder.materialize([insight])

    expected_page = tmp_path / "data" / "wiki" / "sector" / "semiconductors" / "source-7.md"
    assert first_result.page_paths == [expected_page]
    assert second_result.page_paths == [expected_page]
    assert expected_page.exists()
    page_text = expected_page.read_text()
    assert "# Semiconductors" in page_text
    assert "Upside case: Semiconductors: NVIDIA and TSMC are expanding advanced packaging." in page_text

    index_path = tmp_path / "data" / "wiki" / "index.json"
    assert index_path.exists()
    index_payload = index_path.read_text()
    assert index_payload.count('"source_document_id": 7') == 1


def test_merges_multiple_topics_into_stable_index_entries(tmp_path: Path) -> None:
    builder = WikiBuilder(base_dir=tmp_path)
    insights = [
        _make_insight(
            topic="semiconductors",
            lane="sector",
            summary="Semiconductors: NVIDIA and TSMC are expanding advanced packaging.",
            document_id=7,
        ),
        _make_insight(
            topic="rates",
            lane="macro",
            summary="Rates: Treasury yields stayed elevated after hawkish Fed commentary.",
            document_id=8,
        ),
    ]

    result = builder.materialize(insights)

    assert len(result.page_paths) == 2
    index_path = tmp_path / "data" / "wiki" / "index.json"
    index_payload = index_path.read_text()
    assert '"topic": "semiconductors"' in index_payload
    assert '"topic": "rates"' in index_payload
