"""Analysis result models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .note import ContentType, EngagementLevel, Sentiment, TitlePattern


class AnalysisResult(BaseModel):
    """Result of analyzing a single note."""

    title_pattern: TitlePattern = Field(description="Title pattern category")
    content_type: ContentType = Field(description="Content type classification")
    sentiment: Sentiment = Field(description="Overall sentiment")
    engagement_level: EngagementLevel = Field(description="Engagement level")
    hooks: list[str] = Field(default_factory=list, description="Identified hooks in content")
    call_to_action: str | None = Field(default=None, description="Call-to-action if present")
    emoji_density: float = Field(default=0.0, description="Emoji count per 100 chars")
    paragraph_count: int = Field(default=0, description="Number of paragraphs")
    has_list: bool = Field(default=False, description="Whether content uses lists")
    word_count: int = Field(default=0, description="Total word/character count")
    summary: str = Field(default="", description="Brief analysis summary")


class PatternInsight(BaseModel):
    """A single insight from pattern extraction."""

    category: str = Field(description="Insight category")
    description: str = Field(description="Insight description")
    frequency: float = Field(default=0.0, description="How common this pattern is (0-1)")
    examples: list[str] = Field(default_factory=list, description="Example titles/content")


class PatternResult(BaseModel):
    """Result of extracting patterns from multiple notes."""

    query: str = Field(description="Original query")
    notes_analyzed: int = Field(default=0, description="Number of notes analyzed")
    title_patterns: dict[str, int] = Field(
        default_factory=dict, description="Title pattern distribution"
    )
    content_types: dict[str, int] = Field(
        default_factory=dict, description="Content type distribution"
    )
    common_tags: list[str] = Field(default_factory=list, description="Most common tags")
    avg_likes: float = Field(default=0.0, description="Average likes")
    avg_collects: float = Field(default=0.0, description="Average bookmarks")
    insights: list[PatternInsight] = Field(default_factory=list, description="Key insights")
    top_performing_titles: list[str] = Field(
        default_factory=list, description="Best performing titles"
    )


class GeneratedPost(BaseModel):
    """A generated RedNote post."""

    title: str = Field(description="Generated title")
    content: str = Field(description="Generated post content")
    hashtags: list[str] = Field(default_factory=list, description="Suggested hashtags")
    tips: list[str] = Field(default_factory=list, description="Tips for posting")
    estimated_engagement: str = Field(
        default="moderate", description="Estimated engagement level"
    )


class RewrittenPost(BaseModel):
    """Content rewritten in RedNote style."""

    rewritten: str = Field(description="Rewritten content")
    title_suggestion: str = Field(default="", description="Suggested title")
    hashtags: list[str] = Field(default_factory=list, description="Suggested hashtags")
    changes: list[str] = Field(default_factory=list, description="Changes made")
    style_notes: str = Field(default="", description="Notes on style applied")
