from __future__ import annotations

from dataclasses import dataclass

from .chunking import TextChunk
from .domain import ExtractionPacket


@dataclass(frozen=True)
class ChunkSelection:
    lane: str
    topic: str
    selected_text: str


class ChunkAwareSummaryPlanner:
    def select(self, *, packet: ExtractionPacket, chunks: list[TextChunk]) -> list[ChunkSelection]:
        route_pairs: list[tuple[str, str]] = []
        for hint in packet.route_hints:
            if ':' not in hint:
                continue
            lane, topic = hint.split(':', 1)
            pair = (lane, topic)
            if pair not in route_pairs:
                route_pairs.append(pair)
        if not route_pairs:
            route_pairs = [('macro', 'general')]
        selected = '\n\n'.join(chunk.text for chunk in chunks[:3]) if chunks else packet.text_excerpt
        return [ChunkSelection(lane=lane, topic=topic, selected_text=selected) for lane, topic in route_pairs]
