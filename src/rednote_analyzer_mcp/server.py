"""RedNote Analyzer MCP Server.

An MCP server that enables LLMs to analyze, understand, and generate
RedNote (小红书/Xiaohongshu) content through structured tools and prompts.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.tools import analysis as analysis_tools
from rednote_analyzer_mcp.tools import discovery as discovery_tools
from rednote_analyzer_mcp.tools import generation as generation_tools

# --- Server Setup ---

mcp = FastMCP(
    "rednote-analyzer-mcp",
    instructions=(
        "RedNote Analyzer MCP: Search, analyze, and generate RedNote (小红书) content. "
        "Use rednote_search_notes to find notes, rednote_analyze_note for analysis, "
        "and rednote_generate_post to create content."
    ),
)

# Module-level singleton adapter.  Created once on first tool call and reused
# for the lifetime of the server process.  This is critical for the Playwright
# adapter which maintains a browser instance and an ``xsec_token`` cache that
# must persist across tool calls.
_adapter: RedNoteAdapter | None = None


def _get_adapter() -> RedNoteAdapter:
    """Return the shared adapter singleton, creating it on first call.

    Set REDNOTE_ADAPTER env var to switch:
      - "mock" (default): Uses built-in sample data
      - "playwright": Uses real browser to fetch live xiaohongshu.com data

    For playwright adapter, also set:
      - REDNOTE_HEADLESS=false (first run, to log in interactively)
      - REDNOTE_COOKIE_PATH (optional, custom cookie file path)
    """
    global _adapter  # noqa: PLW0603
    if _adapter is not None:
        return _adapter

    adapter_type = os.environ.get("REDNOTE_ADAPTER", "mock")
    if adapter_type == "playwright":
        try:
            from rednote_analyzer_mcp.adapters.playwright import PlaywrightAdapter
        except ImportError:
            raise RuntimeError(
                "Playwright adapter requires the [browser] extra. Install with:\n"
                "  pip install rednote-analyzer-mcp[browser]\n"
                "  playwright install chromium"
            )
        headless = os.environ.get("REDNOTE_HEADLESS", "true").lower() == "true"
        cookie_path = os.environ.get("REDNOTE_COOKIE_PATH")
        _adapter = PlaywrightAdapter(headless=headless, cookie_path=cookie_path)
    else:
        from rednote_analyzer_mcp.adapters.mock import MockAdapter

        _adapter = MockAdapter()

    return _adapter


# --- Discovery Tools ---


@mcp.tool()
async def rednote_search_notes(
    query: str,
    sort: str = "hot",
    limit: int = 20,
) -> dict:
    """Search RedNote (小红书) notes by keyword or topic.

    Find notes matching your query, sorted by popularity or recency.
    Supports Chinese and English keywords.

    Args:
        query: Search keyword or topic (e.g., "美股", "投资", "穿搭")
        sort: Sort order - "hot" (most popular), "recent" (newest), or "relevant"
        limit: Maximum number of results (1-100, default 20)
    """
    adapter = _get_adapter()
    return await discovery_tools.search_notes(adapter, query, sort, limit)


@mcp.tool()
async def rednote_get_note_detail(
    note_id: str,
    include_comments: bool = False,
) -> dict:
    """Get full details of a specific RedNote note.

    Retrieves the complete note content, engagement metrics, author info,
    and optionally comments.

    Args:
        note_id: The note's unique ID
        include_comments: Whether to include comments (default: False)
    """
    adapter = _get_adapter()
    return await discovery_tools.get_note_detail(adapter, note_id, include_comments)


# --- Analysis Tools ---


@mcp.tool()
async def rednote_analyze_note(
    note_id: str = "",
    content: str = "",
    title: str = "",
) -> dict:
    """Analyze a RedNote note's structure, sentiment, and engagement patterns.

    Can analyze by note_id (fetches the note) or by providing content directly.
    Returns title pattern, content type, sentiment, hooks, and structural analysis.

    Args:
        note_id: Note ID to analyze (fetches from data source)
        content: Or provide content text directly for analysis
        title: Title to analyze (used with content parameter)
    """
    adapter = _get_adapter()
    return await analysis_tools.analyze_note(adapter, note_id, content, title)


@mcp.tool()
async def rednote_extract_patterns(
    query: str,
    limit: int = 20,
) -> dict:
    """Extract common patterns from multiple RedNote notes on a topic.

    Searches for notes on the given topic and analyzes them collectively
    to identify title patterns, content structures, common tags,
    engagement metrics, and key insights.

    Args:
        query: Topic to analyze (e.g., "美股投资", "iPhone测评")
        limit: Number of notes to analyze (default 20)
    """
    adapter = _get_adapter()
    return await analysis_tools.extract_patterns(adapter, query, limit)


# --- Generation Tools ---


@mcp.tool()
async def rednote_generate_post(
    topic: str,
    style: str = "干货",
    vertical: str = "general",
    target_audience: str = "",
) -> dict:
    """Generate a RedNote post outline based on topic and style.

    Creates a structured post with title, content outline, hashtags,
    and posting tips. Styles: 干货(tutorial), 情绪(emotional),
    测评(review), 经验(experience), casual.

    Args:
        topic: Post topic (e.g., "美股入门", "iPhone 17测评")
        style: Content style - "干货", "情绪", "测评", "经验", "casual"
        vertical: Content vertical - "investment", "tech", "lifestyle", "fashion", "general"
        target_audience: Optional target audience description
    """
    adapter = _get_adapter()
    return await generation_tools.generate_post(adapter, topic, style, vertical, target_audience)


@mcp.tool()
async def rednote_rewrite_in_style(
    content: str,
    style: str = "casual",
    reference_note_id: str = "",
) -> dict:
    """Rewrite content in RedNote style with proper formatting and hooks.

    Takes any text and provides guidelines to rewrite it for the RedNote
    platform with appropriate tone, structure, emojis, and hashtags.

    Args:
        content: The original content to rewrite
        style: Target style - "干货", "情绪", "测评", "经验", "casual"
        reference_note_id: Optional note ID to use as style reference
    """
    adapter = _get_adapter()
    return await generation_tools.rewrite_in_style(adapter, content, style, reference_note_id)


# --- Prompts ---


@mcp.prompt()
def analyze_trending(topic: str) -> str:
    """Analyze trending RedNote notes for a given topic.

    Args:
        topic: The topic to analyze (e.g., "美股", "AI", "穿搭")
    """
    return (
        f"Please analyze the trending RedNote (小红书) notes about '{topic}'.\n\n"
        f"1. First, use rednote_search_notes to find notes about '{topic}'\n"
        f"2. Then use rednote_extract_patterns to identify common patterns\n"
        f"3. Pick 2-3 interesting notes and use rednote_analyze_note on each\n"
        f"4. Summarize your findings:\n"
        f"   - What title patterns work best?\n"
        f"   - What content styles get the most engagement?\n"
        f"   - What are the common hashtags?\n"
        f"   - What insights can a content creator learn from this?"
    )


@mcp.prompt()
def write_post(topic: str, style: str = "干货") -> str:
    """Write a RedNote post about a topic.

    Args:
        topic: What to write about
        style: Style to use (干货/情绪/测评/经验/casual)
    """
    return (
        f"Help me write a RedNote (小红书) post about '{topic}' in {style} style.\n\n"
        f"1. First, use rednote_extract_patterns to see what works for '{topic}'\n"
        f"2. Then use rednote_generate_post with topic='{topic}' and style='{style}'\n"
        f"3. Based on the patterns and template, write a complete post:\n"
        f"   - Catchy title (under 20 chars if possible)\n"
        f"   - Engaging opening hook\n"
        f"   - Well-structured body with emojis\n"
        f"   - Interactive CTA at the end\n"
        f"   - 3-5 relevant hashtags\n\n"
        f"Write the post in Chinese, optimized for RedNote's audience."
    )


@mcp.prompt()
def investment_briefing(ticker_or_topic: str) -> str:
    """Create investment content for RedNote.

    Args:
        ticker_or_topic: Stock ticker or investment topic (e.g., "NVDA", "美股入门")
    """
    return (
        f"Create a RedNote (小红书) investment post about '{ticker_or_topic}'.\n\n"
        f"1. Use rednote_search_notes to find existing investment posts about this topic\n"
        f"2. Use rednote_extract_patterns to see what engagement patterns work\n"
        f"3. Use rednote_generate_post with vertical='investment'\n"
        f"4. Write a complete post that:\n"
        f"   - Has an attention-grabbing title\n"
        f"   - Explains concepts simply (小白也能懂)\n"
        f"   - Includes relevant data/analysis\n"
        f"   - Has proper risk disclaimers (⚠️ 投资有风险)\n"
        f"   - Ends with engagement CTA\n"
        f"   - Uses appropriate hashtags\n\n"
        f"IMPORTANT: Include the disclaimer '⚠️ 投资有风险，本文不构成投资建议。'"
    )


# --- Entry Point ---


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
