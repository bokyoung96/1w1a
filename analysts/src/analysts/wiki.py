from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import build_config
from .domain import InsightRecord


@dataclass(frozen=True)
class WikiMaterializationResult:
    page_paths: list[Path]
    index_path: Path


class WikiBuilder:
    def __init__(self, *, base_dir: Path) -> None:
        self.config = build_config(base_dir)

    def materialize(self, insights: list[InsightRecord]) -> WikiMaterializationResult:
        page_paths: list[Path] = []
        index_entries = self._load_index()

        for insight in insights:
            page_path = self._page_path(insight)
            page_path.parent.mkdir(parents=True, exist_ok=True)
            page_path.write_text(self._render_page(insight))
            page_paths.append(page_path)

            key = f"{insight.lane}:{insight.topic}:{insight.source_document_id}"
            index_entries[key] = {
                "lane": insight.lane,
                "topic": insight.topic,
                "source_document_id": insight.source_document_id,
                "path": str(page_path.relative_to(self.config.paths.base_dir)),
            }

        index_path = self.config.paths.wiki_dir / "index.json"
        ordered_entries = [index_entries[key] for key in sorted(index_entries)]
        index_path.write_text(json.dumps(ordered_entries, indent=2, sort_keys=True) + "\n")
        return WikiMaterializationResult(page_paths=page_paths, index_path=index_path)

    def _load_index(self) -> dict[str, dict[str, object]]:
        index_path = self.config.paths.wiki_dir / "index.json"
        if not index_path.exists():
            return {}

        payload = json.loads(index_path.read_text())
        return {
            f"{entry['lane']}:{entry['topic']}:{entry['source_document_id']}": entry
            for entry in payload
        }

    def _page_path(self, insight: InsightRecord) -> Path:
        return (
            self.config.paths.wiki_dir
            / insight.lane
            / insight.topic
            / f"source-{insight.source_document_id}.md"
        )

    @staticmethod
    def _render_page(insight: InsightRecord) -> str:
        return "\n".join(
            [
                f"# {insight.topic.title()}",
                "",
                f"- Lane: {insight.lane}",
                f"- Source document id: {insight.source_document_id}",
                f"- Confidence: {insight.confidence}",
                "",
                "## Summary",
                insight.summary,
                "",
                "## Bull case",
                insight.bull_case,
                "",
                "## Bear case",
                insight.bear_case,
                "",
                "## Key drivers",
                *[f"- {driver}" for driver in insight.key_drivers],
                "",
                "## Risk factors",
                *[f"- {risk}" for risk in insight.risk_factors],
                "",
            ]
        )
