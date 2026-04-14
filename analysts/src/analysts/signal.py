from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .config import build_config
from .domain import InsightRecord, SignalSnapshot

_TOKEN_RE = re.compile(r"[a-z]{3,}")
_STOP_WORDS = {
    "case",
    "downside",
    "upside",
    "sector",
    "macro",
    "source",
    "document",
    "risk",
    "risks",
    "limited",
}
_POSITIVE_WORDS = {"strong", "normalize", "expanding", "upside"}
_NEGATIVE_WORDS = {"weak", "constrained", "risk", "downside", "degraded"}


@dataclass(frozen=True)
class SignalGenerationResult:
    snapshots: list[SignalSnapshot]
    snapshot_paths: list[Path]


class SignalEngine:
    def __init__(self, *, base_dir: Path) -> None:
        self.config = build_config(base_dir)

    def generate(self, insights: list[InsightRecord]) -> SignalGenerationResult:
        grouped: dict[str, list[InsightRecord]] = defaultdict(list)
        for insight in insights:
            grouped[insight.topic].append(insight)

        snapshots: list[SignalSnapshot] = []
        snapshot_paths: list[Path] = []
        for topic in sorted(grouped):
            topic_insights = grouped[topic]
            snapshot = self._build_snapshot(topic, topic_insights)
            snapshots.append(snapshot)
            path = self.config.paths.signals_dir / f"{topic}.json"
            path.write_text(
                json.dumps(
                    {
                        "topic": snapshot.topic,
                        "repeated_keywords": snapshot.repeated_keywords,
                        "sentiment_delta": snapshot.sentiment_delta,
                        "conflict_flags": snapshot.conflict_flags,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
            snapshot_paths.append(path)

        return SignalGenerationResult(snapshots=snapshots, snapshot_paths=snapshot_paths)

    def _build_snapshot(self, topic: str, insights: list[InsightRecord]) -> SignalSnapshot:
        counts = Counter()
        positive_hits = 0
        negative_hits = 0

        for insight in insights:
            for token in self._tokens(f"{insight.summary} {insight.bull_case} {insight.bear_case}"):
                counts[token] += 1
                if token in _POSITIVE_WORDS:
                    positive_hits += 1
                if token in _NEGATIVE_WORDS:
                    negative_hits += 1

        repeated_keywords = [
            token
            for token, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
            if count > 1
        ]

        if positive_hits and negative_hits:
            sentiment_delta = "mixed"
            conflict_flags = ["bull_vs_bear_keyword_conflict"]
        elif positive_hits:
            sentiment_delta = "positive"
            conflict_flags = []
        elif negative_hits:
            sentiment_delta = "negative"
            conflict_flags = []
        else:
            sentiment_delta = "neutral"
            conflict_flags = []

        return SignalSnapshot(
            topic=topic,
            repeated_keywords=repeated_keywords,
            sentiment_delta=sentiment_delta,
            conflict_flags=conflict_flags,
        )

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [token for token in _TOKEN_RE.findall(text.lower()) if token not in _STOP_WORDS]
