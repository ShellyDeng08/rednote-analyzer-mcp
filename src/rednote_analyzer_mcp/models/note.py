"""Core data models for RedNote (小红书) content."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class NoteType(StrEnum):
    """Type of RedNote note."""

    NORMAL = "normal"
    VIDEO = "video"


class ContentType(StrEnum):
    """Content category classification."""

    TUTORIAL = "干货"  # Tutorial / how-to
    EMOTION = "情绪"  # Emotional content
    OPINION = "观点"  # Opinion piece
    EXPERIENCE = "经历"  # Personal experience
    REVIEW = "测评"  # Product review
    OTHER = "其他"  # Other


class Sentiment(StrEnum):
    """Sentiment classification."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EngagementLevel(StrEnum):
    """Engagement level based on likes."""

    VIRAL = "viral"  # >10K likes
    POPULAR = "popular"  # 1K-10K likes
    MODERATE = "moderate"  # 100-1K likes
    LOW = "low"  # <100 likes


class TitlePattern(StrEnum):
    """Common title patterns on RedNote."""

    QUESTION = "question"  # 问句式
    NUMBER_LIST = "number_list"  # 数字列表式
    EMOTIONAL_HOOK = "emotional_hook"  # 情绪钩子
    AUTHORITY_CLAIM = "authority_claim"  # 权威声明
    HOW_TO = "how_to"  # 教程式
    STORY = "story"  # 故事式
    CONTRAST = "contrast"  # 对比式
    OTHER = "other"


class RedNoteAuthor(BaseModel):
    """RedNote content author."""

    id: str = Field(description="Author unique ID")
    nickname: str = Field(description="Display name")
    avatar: str | None = Field(default=None, description="Avatar URL")
    followers: int | None = Field(default=None, description="Follower count")
    verified: bool = Field(default=False, description="Verified status")


class RedNoteNote(BaseModel):
    """A RedNote (小红书) note/post."""

    id: str = Field(description="Note unique ID")
    title: str = Field(description="Note title")
    content: str = Field(description="Main text content")
    note_type: NoteType = Field(default=NoteType.NORMAL, description="Note type")
    images: list[str] = Field(default_factory=list, description="Image URLs")
    video_url: str | None = Field(default=None, description="Video URL if video note")

    # Engagement metrics
    likes: int = Field(default=0, description="点赞数 (likes)")
    collects: int = Field(default=0, description="收藏数 (bookmarks)")
    comments_count: int = Field(default=0, description="评论数 (comments)")
    shares: int = Field(default=0, description="分享数 (shares)")

    # Metadata
    tags: list[str] = Field(default_factory=list, description="Hashtags / topics")
    topics: list[str] = Field(default_factory=list, description="Associated topics")
    publish_time: datetime = Field(description="Publish datetime")
    last_update_time: datetime | None = Field(default=None, description="Last edit time")

    # Author
    author: RedNoteAuthor = Field(description="Note author")

    # Location
    location: str | None = Field(default=None, description="Location name")

    @property
    def engagement_level(self) -> EngagementLevel:
        """Classify engagement level based on likes."""
        if self.likes >= 10000:
            return EngagementLevel.VIRAL
        elif self.likes >= 1000:
            return EngagementLevel.POPULAR
        elif self.likes >= 100:
            return EngagementLevel.MODERATE
        return EngagementLevel.LOW

    @property
    def total_engagement(self) -> int:
        """Total engagement score."""
        return self.likes + self.collects + self.comments_count + self.shares


class RedNoteComment(BaseModel):
    """A comment on a RedNote note."""

    id: str = Field(description="Comment unique ID")
    content: str = Field(description="Comment text")
    likes: int = Field(default=0, description="Comment likes")
    author: RedNoteAuthor = Field(description="Comment author")
    replies: list[RedNoteComment] = Field(default_factory=list, description="Replies")
    create_time: datetime | None = Field(default=None, description="Comment time")
