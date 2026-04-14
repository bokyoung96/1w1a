from pathlib import Path

from analysts.domain import InsightRecord
from analysts.signal import SignalEngine


def _make_insight(
    *,
    topic: str,
    lane: str,
    summary: str,
    bull_case: str,
    bear_case: str,
    confidence: str,
    document_id: int,
) -> InsightRecord:
    return InsightRecord(
        topic=topic,
        lane=lane,
        summary=summary,
        bull_case=bull_case,
        bear_case=bear_case,
        confidence=confidence,
        key_drivers=["NVDA", "TSM"],
        risk_factors=[bear_case.replace("Downside case: ", "")],
        source_document_id=document_id,
    )


def test_detects_repeated_keywords_and_conflicting_sentiment_idempotently(tmp_path: Path) -> None:
    engine = SignalEngine(base_dir=tmp_path)
    insights = [
        _make_insight(
            topic="semiconductors",
            lane="sector",
            summary="Semiconductors: NVIDIA packaging demand remains strong.",
            bull_case="Upside case: Demand remains strong.",
            bear_case="Downside case: Supply remains constrained.",
            confidence="high",
            document_id=7,
        ),
        _make_insight(
            topic="semiconductors",
            lane="sector",
            summary="Semiconductors: NVIDIA supply remains constrained.",
            bull_case="Upside case: Supply may normalize.",
            bear_case="Downside case: Demand remains weak if hyperscaler budgets slow.",
            confidence="medium",
            document_id=8,
        ),
    ]

    first_result = engine.generate(insights)
    second_result = engine.generate(insights)

    assert [snapshot.topic for snapshot in first_result.snapshots] == ["semiconductors"]
    snapshot = first_result.snapshots[0]
    assert "nvidia" in snapshot.repeated_keywords
    assert "remains" in snapshot.repeated_keywords
    assert snapshot.sentiment_delta == "mixed"
    assert snapshot.conflict_flags == ["bull_vs_bear_keyword_conflict"]

    snapshot_path = tmp_path / "data" / "signals" / "semiconductors.json"
    assert snapshot_path.exists()
    assert second_result.snapshot_paths == [snapshot_path]
    assert snapshot_path.read_text().count('"topic": "semiconductors"') == 1
