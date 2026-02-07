"""Discovery tools: search and retrieve RedNote notes."""

from __future__ import annotations

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import NoteDetail, SearchResult


async def search_notes(
    adapter: RedNoteAdapter,
    query: str,
    sort: str = "hot",
    limit: int = 20,
) -> dict:
    """Search RedNote notes by keyword or topic.

    Returns matching notes sorted by the specified order.
    """
    notes, total = await adapter.search_notes(query, sort, limit)
    result = SearchResult(
        notes=notes,
        total=total,
        query=query,
    )
    return result.model_dump(mode="json")


async def get_note_detail(
    adapter: RedNoteAdapter,
    note_id: str,
    include_comments: bool = False,
) -> dict:
    """Get full details of a RedNote note, optionally including comments."""
    note = await adapter.get_note_detail(note_id)
    if note is None:
        return {"error": f"Note '{note_id}' not found"}

    comments = []
    if include_comments:
        raw_comments = await adapter.get_note_comments(note_id)
        comments = [c.model_dump(mode="json") for c in raw_comments]

    result = NoteDetail(
        note=note,
        comments=comments,
    )
    return result.model_dump(mode="json")
