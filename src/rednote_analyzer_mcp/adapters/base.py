"""Abstract base adapter for RedNote data access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from rednote_analyzer_mcp.models import (
    RedNoteComment,
    RedNoteNote,
)


class RedNoteAdapter(ABC):
    """Abstract interface for RedNote data access.

    Implement this interface to connect the MCP server to your data source.
    The repo ships with MockAdapter for development/testing.
    Users can implement their own adapters (e.g., using the `xhs` Python library
    or `MediaCrawler`) without modifying the MCP server code.
    """

    @abstractmethod
    async def search_notes(
        self,
        query: str,
        sort: str = "hot",
        limit: int = 20,
    ) -> tuple[list[RedNoteNote], int]:
        """Search notes by keyword.

        Args:
            query: Search keyword or topic.
            sort: Sort order - "hot", "recent", or "relevant".
            limit: Maximum number of results.

        Returns:
            Tuple of (list of matching notes, total count).
        """
        ...

    @abstractmethod
    async def get_note_detail(self, note_id: str) -> RedNoteNote | None:
        """Get full details of a single note.

        Args:
            note_id: The note's unique ID.

        Returns:
            The note, or None if not found.
        """
        ...

    @abstractmethod
    async def get_note_comments(
        self,
        note_id: str,
        limit: int = 20,
    ) -> list[RedNoteComment]:
        """Get comments for a note.

        Args:
            note_id: The note's unique ID.
            limit: Maximum number of comments.

        Returns:
            List of comments.
        """
        ...

    @abstractmethod
    async def get_author_notes(
        self,
        author_id: str,
        limit: int = 20,
    ) -> list[RedNoteNote]:
        """Get notes by a specific author.

        Args:
            author_id: The author's unique ID.
            limit: Maximum number of results.

        Returns:
            List of the author's notes.
        """
        ...
