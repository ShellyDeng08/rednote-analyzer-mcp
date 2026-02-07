"""Search-related models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .note import RedNoteNote


class SortOrder(StrEnum):
    """Sort order for search results."""

    HOT = "hot"
    RECENT = "recent"
    RELEVANT = "relevant"


class SearchParams(BaseModel):
    """Parameters for searching notes."""

    query: str = Field(description="Search keyword or topic")
    sort: SortOrder = Field(default=SortOrder.HOT, description="Sort order")
    limit: int = Field(default=20, ge=1, le=100, description="Max results to return")


class SearchResult(BaseModel):
    """Search results container."""

    notes: list[RedNoteNote] = Field(default_factory=list, description="Matching notes")
    total: int = Field(default=0, description="Total matching notes")
    query: str = Field(description="Original search query")


class NoteDetail(BaseModel):
    """Full note detail with optional comments."""

    note: RedNoteNote = Field(description="The note")
    comments: list[dict] = Field(default_factory=list, description="Note comments")
