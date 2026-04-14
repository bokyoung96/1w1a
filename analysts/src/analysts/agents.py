from __future__ import annotations

from dataclasses import dataclass

from .domain import InsightRecord, ParseQuality, ParsedDocument, RouteDecision


@dataclass(frozen=True)
class AnalystCoordinator:
    def build_insights(
        self,
        parsed: ParsedDocument,
        routes: list[RouteDecision],
        *,
        source_document_id: int,
    ) -> list[InsightRecord]:
        return [
            self._build_single_insight(parsed, route, source_document_id=source_document_id)
            for route in routes
        ]

    def _build_single_insight(
        self,
        parsed: ParsedDocument,
        route: RouteDecision,
        *,
        source_document_id: int,
    ) -> InsightRecord:
        if parsed.parse_quality is ParseQuality.DEGRADED and not parsed.content:
            degraded_reason = parsed.degraded_reason or "unknown_parse_issue"
            return InsightRecord(
                topic=route.topic,
                lane=route.lane,
                summary=f"{route.topic.title()}: Source document was only partially readable.",
                bull_case="Upside case: Follow-up review required because the parsed content is limited.",
                bear_case=f"Downside case: Parsing degraded ({degraded_reason}).",
                confidence="low",
                key_drivers=["manual_review_required"],
                risk_factors=[f"Parsing degraded: {degraded_reason}"],
                source_document_id=source_document_id,
            )

        summary_body = self._first_body_line(parsed.sections) or parsed.title
        risk_body = self._risk_line(parsed.sections) or "Risk disclosures were limited in the parsed document."
        key_drivers = list(dict.fromkeys([*parsed.tickers, *parsed.entities]))

        return InsightRecord(
            topic=route.topic,
            lane=route.lane,
            summary=f"{route.topic.title()}: {summary_body}",
            bull_case=f"Upside case: {summary_body}",
            bear_case=f"Downside case: {risk_body}",
            confidence=self._confidence(parsed),
            key_drivers=key_drivers or ["manual_review_required"],
            risk_factors=[risk_body],
            source_document_id=source_document_id,
        )

    @staticmethod
    def _first_body_line(sections: list[str]) -> str | None:
        for section in sections:
            lines = [line.strip() for line in section.splitlines() if line.strip()]
            if len(lines) >= 2:
                return lines[1]
            if lines:
                return lines[0]
        return None

    @staticmethod
    def _risk_line(sections: list[str]) -> str | None:
        for section in sections:
            lines = [line.strip() for line in section.splitlines() if line.strip()]
            if lines and lines[0].rstrip(":").lower() == "risks":
                return lines[1] if len(lines) >= 2 else "Risk disclosures were limited in the parsed document."
        return None

    @staticmethod
    def _confidence(parsed: ParsedDocument) -> str:
        if parsed.parse_quality is ParseQuality.HIGH and parsed.sections:
            return "high"
        if parsed.content:
            return "medium"
        return "low"
