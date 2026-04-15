from pathlib import Path

from analysts.chunking import TextChunk
from analysts.domain import ExtractionPacket
from analysts.summary_agents import ChunkAwareSummaryPlanner



def test_summary_agent_planner_selects_route_aware_chunks():
    packet = ExtractionPacket(
        source_document_id=1,
        report_title='title',
        report_channel='DOC_POOL',
        message_id=1,
        published_at='2026-04-15T00:00:00Z',
        raw_pdf_path=Path('raw.pdf'),
        extraction_quality='high',
        extraction_reason=None,
        preferred_text='x',
        text_excerpt='x',
        route_hints=['sector:semiconductors'],
        entities=[],
        tickers=[],
    )
    chunks = [TextChunk(chunk_id='c1', chunk_index=0, text='chunk text', char_count=10)]

    result = ChunkAwareSummaryPlanner().select(packet=packet, chunks=chunks)

    assert result[0].lane == 'sector'
    assert result[0].topic == 'semiconductors'
    assert 'chunk text' in result[0].selected_text
