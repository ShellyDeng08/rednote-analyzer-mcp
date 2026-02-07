"""Analysis tools: analyze notes and extract patterns."""

from __future__ import annotations

import re
from datetime import UTC

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import (
    AnalysisResult,
    ContentType,
    PatternInsight,
    PatternResult,
    RedNoteNote,
    Sentiment,
    TitlePattern,
)


def _classify_title_pattern(title: str) -> TitlePattern:
    """Classify the title pattern of a note."""
    if "?" in title or "？" in title or "吗" in title or "呢" in title:
        return TitlePattern.QUESTION
    if any(c.isdigit() for c in title) and any(
        kw in title for kw in ["个", "条", "步", "招", "种", "只", "套"]
    ):
        return TitlePattern.NUMBER_LIST
    if any(kw in title for kw in ["震惊", "暴", "绝了", "太", "！", "❗", "🔥", "💰", "😱"]):
        return TitlePattern.EMOTIONAL_HOOK
    if any(kw in title for kw in ["深度", "分析", "专业", "权威", "研究"]):
        return TitlePattern.AUTHORITY_CLAIM
    if any(kw in title for kw in ["如何", "怎么", "教你", "指南", "方法", "攻略"]):
        return TitlePattern.HOW_TO
    if any(kw in title for kw in ["我", "经历", "亲测", "真实"]):
        return TitlePattern.STORY
    if "vs" in title.lower() or "对比" in title or "还是" in title:
        return TitlePattern.CONTRAST
    return TitlePattern.OTHER


def _classify_content_type(content: str) -> ContentType:
    """Classify the content type of a note."""
    tutorial_keywords = ["步骤", "方法", "教程", "指南", "第一步", "第二步", "✅", "📌"]
    emotion_keywords = ["感动", "哭了", "太难了", "崩溃", "开心", "幸福"]
    opinion_keywords = ["我认为", "我觉得", "我的看法", "观点", "分析"]
    experience_keywords = ["我的经历", "亲身", "真实体验", "分享一下", "用了"]
    review_keywords = ["测评", "评测", "优点", "缺点", "推荐", "值不值"]

    scores = {
        ContentType.TUTORIAL: sum(1 for kw in tutorial_keywords if kw in content),
        ContentType.EMOTION: sum(1 for kw in emotion_keywords if kw in content),
        ContentType.OPINION: sum(1 for kw in opinion_keywords if kw in content),
        ContentType.EXPERIENCE: sum(1 for kw in experience_keywords if kw in content),
        ContentType.REVIEW: sum(1 for kw in review_keywords if kw in content),
    }

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    return best if scores[best] > 0 else ContentType.OTHER


def _classify_sentiment(content: str) -> Sentiment:
    """Simple keyword-based sentiment classification."""
    positive = ["好", "棒", "推荐", "值得", "喜欢", "赚", "涨", "增长", "优秀", "🔥", "💪", "✅"]
    negative = ["差", "烂", "亏", "跌", "暴跌", "风险", "坑", "😭", "💔", "⚠️"]

    pos_score = sum(1 for kw in positive if kw in content)
    neg_score = sum(1 for kw in negative if kw in content)

    if pos_score > 0 and neg_score > 0:
        return Sentiment.MIXED
    if pos_score > neg_score:
        return Sentiment.POSITIVE
    if neg_score > pos_score:
        return Sentiment.NEGATIVE
    return Sentiment.NEUTRAL


def _count_emojis(text: str) -> int:
    """Count emoji characters in text."""
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
        "\U0001f1e0-\U0001f1ff\u2702-\u27b0\u24c2-\U0001f251"
        "\U0001f900-\U0001f9ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff"
        "\u2600-\u26ff\u2700-\u27bf]+",
        flags=re.UNICODE,
    )
    return len(emoji_pattern.findall(text))


def _find_hooks(content: str) -> list[str]:
    """Extract hook phrases from content."""
    hooks = []
    lines = content.strip().split("\n")
    if lines:
        first_line = lines[0].strip()
        if first_line and len(first_line) < 100:
            hooks.append(f"Opening: {first_line}")

    cta_patterns = ["评论区", "关注", "点赞", "收藏", "转发", "一起", "你们觉得", "你们有"]
    for pattern in cta_patterns:
        if pattern in content:
            hooks.append(f"CTA: contains '{pattern}'")
            break

    return hooks


def _find_cta(content: str) -> str | None:
    """Find call-to-action in content."""
    cta_patterns = [
        "评论区聊聊",
        "评论区交流",
        "你们觉得",
        "你们有",
        "一起来",
        "关注我",
        "想试试",
    ]
    for pattern in cta_patterns:
        if pattern in content:
            return pattern
    return None


def _analyze_single_note(note: RedNoteNote) -> AnalysisResult:
    """Analyze a single note."""
    content = note.content
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    emoji_count = _count_emojis(content)
    char_count = len(content)

    return AnalysisResult(
        title_pattern=_classify_title_pattern(note.title),
        content_type=_classify_content_type(content),
        sentiment=_classify_sentiment(content),
        engagement_level=note.engagement_level,
        hooks=_find_hooks(content),
        call_to_action=_find_cta(content),
        emoji_density=round(emoji_count / max(char_count, 1) * 100, 2),
        paragraph_count=len(paragraphs),
        has_list=bool(
            re.search(r"[1-9][.、️⃣]|[•·]|^[-*]", content, re.MULTILINE)
        ),
        word_count=char_count,
        summary=(
            f"A {note.engagement_level.value} {_classify_content_type(content).value} "
            f"note with {_classify_title_pattern(note.title).value} title pattern. "
            f"Sentiment: {_classify_sentiment(content).value}. "
            f"{len(paragraphs)} paragraphs, {emoji_count} emojis."
        ),
    )


async def analyze_note(
    adapter: RedNoteAdapter,
    note_id: str = "",
    content: str = "",
    title: str = "",
) -> dict:
    """Analyze a note's structure, sentiment, and engagement patterns.

    Can analyze by note_id (fetches from adapter) or by providing content directly.
    """
    if note_id:
        note = await adapter.get_note_detail(note_id)
        if note is None:
            return {"error": f"Note '{note_id}' not found"}
    elif content:
        from datetime import datetime

        from rednote_analyzer_mcp.models import RedNoteAuthor

        note = RedNoteNote(
            id="inline",
            title=title or "Untitled",
            content=content,
            publish_time=datetime.now(tz=UTC),
            author=RedNoteAuthor(id="inline", nickname="inline"),
        )
    else:
        return {"error": "Provide either note_id or content"}

    result = _analyze_single_note(note)
    return result.model_dump(mode="json")


async def extract_patterns(
    adapter: RedNoteAdapter,
    query: str,
    limit: int = 20,
) -> dict:
    """Extract common patterns from multiple notes on a topic."""
    notes, total = await adapter.search_notes(query, "hot", limit)

    if not notes:
        return PatternResult(query=query, notes_analyzed=0).model_dump(mode="json")

    # Analyze each note
    analyses = [_analyze_single_note(note) for note in notes]

    # Aggregate title patterns
    title_patterns: dict[str, int] = {}
    for a in analyses:
        key = a.title_pattern.value
        title_patterns[key] = title_patterns.get(key, 0) + 1

    # Aggregate content types
    content_types: dict[str, int] = {}
    for a in analyses:
        key = a.content_type.value
        content_types[key] = content_types.get(key, 0) + 1

    # Common tags
    tag_counts: dict[str, int] = {}
    for note in notes:
        for tag in note.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    common_tags = sorted(tag_counts, key=tag_counts.get, reverse=True)[:10]  # type: ignore[arg-type]

    # Engagement stats
    avg_likes = sum(n.likes for n in notes) / len(notes)
    avg_collects = sum(n.collects for n in notes) / len(notes)

    # Top titles
    top_notes = sorted(notes, key=lambda n: n.likes, reverse=True)[:5]
    top_titles = [n.title for n in top_notes]

    # Build insights
    insights = []
    if title_patterns:
        top_pattern = max(title_patterns, key=title_patterns.get)  # type: ignore[arg-type]
        insights.append(
            PatternInsight(
                category="title_pattern",
                description=f"Most common title pattern: {top_pattern}",
                frequency=title_patterns[top_pattern] / len(analyses),
                examples=[
                    n.title
                    for n in notes
                    if _classify_title_pattern(n.title).value == top_pattern
                ][:3],
            )
        )

    if avg_likes > 10000:
        insights.append(
            PatternInsight(
                category="engagement",
                description=(
                    f"High average engagement ({avg_likes:.0f} avg likes)"
                    " — this is a hot topic"
                ),
                frequency=1.0,
            )
        )

    result = PatternResult(
        query=query,
        notes_analyzed=len(notes),
        title_patterns=title_patterns,
        content_types=content_types,
        common_tags=common_tags,
        avg_likes=round(avg_likes, 1),
        avg_collects=round(avg_collects, 1),
        insights=insights,
        top_performing_titles=top_titles,
    )
    return result.model_dump(mode="json")
