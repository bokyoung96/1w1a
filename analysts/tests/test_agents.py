from analysts.domain import ParseQuality, ParsedDocument, RouteDecision
from analysts.agents import AnalystCoordinator


def test_builds_deterministic_semiconductor_insight_from_route_and_sections() -> None:
    parsed = ParsedDocument(
        title="AI Capacity Update",
        content=(
            "NVIDIA and TSMC are expanding advanced packaging. "
            "Demand remains strong, but supply concentration is still a risk."
        ),
        sections=[
            "Executive Summary:\nNVIDIA and TSMC are expanding advanced packaging.",
            "Risks:\nSupply concentration remains a risk for AI accelerators.",
        ],
        entities=["NVIDIA", "TSMC"],
        tickers=["NVDA", "TSM"],
        routes=[],
        parse_quality=ParseQuality.HIGH,
    )
    routes = [RouteDecision(topic="semiconductors", lane="sector", rationale="matched_keywords: ai, nvidia, tsmc")]

    insights = AnalystCoordinator().build_insights(parsed, routes, source_document_id=7)

    assert len(insights) == 1
    insight = insights[0]
    assert insight.topic == "semiconductors"
    assert insight.lane == "sector"
    assert insight.source_document_id == 7
    assert insight.summary == "Semiconductors: NVIDIA and TSMC are expanding advanced packaging."
    assert insight.bull_case == "Upside case: NVIDIA and TSMC are expanding advanced packaging."
    assert insight.bear_case == "Downside case: Supply concentration remains a risk for AI accelerators."
    assert insight.confidence == "high"
    assert insight.key_drivers == ["NVDA", "TSM", "NVIDIA", "TSMC"]
    assert insight.risk_factors == ["Supply concentration remains a risk for AI accelerators."]


def test_builds_stable_fallback_insight_for_degraded_general_documents() -> None:
    parsed = ParsedDocument(
        title="Desk Notes",
        content="",
        sections=[],
        entities=[],
        tickers=[],
        routes=[],
        parse_quality=ParseQuality.DEGRADED,
        degraded_reason="unable_to_decode_pdf_payload",
    )
    routes = [RouteDecision(topic="general", lane="macro", rationale="fallback:no_taxonomy_match")]

    insights = AnalystCoordinator().build_insights(parsed, routes, source_document_id=9)

    assert len(insights) == 1
    insight = insights[0]
    assert insight.summary == "General: Source document was only partially readable."
    assert insight.bull_case == "Upside case: Follow-up review required because the parsed content is limited."
    assert insight.bear_case == "Downside case: Parsing degraded (unable_to_decode_pdf_payload)."
    assert insight.confidence == "low"
    assert insight.key_drivers == ["manual_review_required"]
    assert insight.risk_factors == ["Parsing degraded: unable_to_decode_pdf_payload"]
