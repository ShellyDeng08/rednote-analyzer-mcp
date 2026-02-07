"""Generation tools: create and rewrite RedNote content."""

from __future__ import annotations

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import GeneratedPost, RewrittenPost

# --- Style templates ---

_STYLE_TEMPLATES = {
    "干货": {
        "title_prefix": "",
        "structure": "Hook → Key Points (numbered) → Summary → CTA",
        "tone": "informative, helpful, structured",
        "emoji_level": "moderate",
    },
    "情绪": {
        "title_prefix": "",
        "structure": "Emotional hook → Story → Insight → CTA",
        "tone": "personal, emotional, relatable",
        "emoji_level": "heavy",
    },
    "测评": {
        "title_prefix": "",
        "structure": "Overview → Pros → Cons → Verdict",
        "tone": "objective, detailed, comparison-focused",
        "emoji_level": "moderate",
    },
    "经验": {
        "title_prefix": "",
        "structure": "Background → What happened → Lessons → Advice",
        "tone": "personal, authentic, storytelling",
        "emoji_level": "light-moderate",
    },
    "casual": {
        "title_prefix": "",
        "structure": "Hook → Body → CTA",
        "tone": "friendly, conversational, approachable",
        "emoji_level": "heavy",
    },
}

_INVESTMENT_DISCLAIMER = "\n\n⚠️ 投资有风险，本文不构成投资建议。请根据自己的风险承受能力做决策。"

_VERTICAL_TAGS = {
    "investment": ["投资", "理财", "美股"],
    "tech": ["数码", "科技", "测评"],
    "lifestyle": ["生活方式", "日常"],
    "fashion": ["穿搭", "时尚", "OOTD"],
    "general": [],
}


async def generate_post(
    adapter: RedNoteAdapter,
    topic: str,
    style: str = "干货",
    vertical: str = "general",
    target_audience: str = "",
) -> dict:
    """Generate a RedNote post based on topic, style, and vertical.

    This tool generates a structured post outline that an LLM can further
    refine. It uses patterns from analyzed notes to create engaging content.
    """
    style_config = _STYLE_TEMPLATES.get(style, _STYLE_TEMPLATES["干货"])

    # Build title suggestions based on style
    title_templates = {
        "干货": [
            f"小白也能懂的{topic}指南📚",
            f"{topic}：3个你必须知道的关键点💡",
            f"一文搞懂{topic}，建议收藏✅",
        ],
        "情绪": [
            f"关于{topic}，我有话说...",
            f"聊聊{topic}这件事，真的太有感触了",
            f"{topic}改变了我的生活🌟",
        ],
        "测评": [
            f"{topic}深度测评：真的值得吗？",
            f"用了一个月的{topic}，来说说真实体验",
            f"{topic}优缺点全分析，看完再决定",
        ],
        "经验": [
            f"我的{topic}经历，希望对你有帮助",
            f"从零开始的{topic}之路💪",
            f"关于{topic}，我踩过的坑和学到的经验",
        ],
        "casual": [
            f"今天聊聊{topic}～",
            f"{topic}分享来啦✨",
            f"关于{topic}的一些想法💭",
        ],
    }

    titles = title_templates.get(style, title_templates["干货"])
    chosen_title = titles[0]

    # Build content structure
    audience_note = f"\n\n🎯 目标受众：{target_audience}" if target_audience else ""

    content = (
        f"[根据以下结构撰写关于「{topic}」的RedNote帖子]\n\n"
        f"📋 内容结构：{style_config['structure']}\n"
        f"🎨 风格：{style_config['tone']}\n"
        f"✨ Emoji使用：{style_config['emoji_level']}"
        f"{audience_note}\n\n"
        f"---\n\n"
        f"[在此处展开你的内容...]\n\n"
        f"---\n\n"
        f"💬 互动引导：在结尾添加一个问题引导评论互动"
    )

    # Add investment disclaimer if relevant
    is_investment = vertical == "investment" or any(
        kw in topic for kw in ["投资", "股票", "基金", "理财", "美股"]
    )
    if is_investment:
        content += _INVESTMENT_DISCLAIMER

    # Build hashtags
    base_tags = _VERTICAL_TAGS.get(vertical, [])
    topic_tags = [topic] if topic not in base_tags else []
    hashtags = [f"#{tag}" for tag in (topic_tags + base_tags)]

    # Tips
    tips = [
        f"使用{style_config['emoji_level']} emoji 来增加阅读体验",
        "第一张图片很重要，决定了点击率",
        "标题控制在20字以内效果最佳",
        "发布时间建议：早8-9点、午12-13点、晚20-22点",
    ]
    if is_investment:
        tips.append("务必添加投资风险提示")

    result = GeneratedPost(
        title=chosen_title,
        content=content,
        hashtags=hashtags,
        tips=tips,
        estimated_engagement="moderate",
    )
    return result.model_dump(mode="json")


async def rewrite_in_style(
    adapter: RedNoteAdapter,
    content: str,
    style: str = "casual",
    reference_note_id: str = "",
) -> dict:
    """Rewrite content in RedNote style with appropriate formatting.

    Provides a structured rewrite plan with style guidance. The actual
    rewriting is best done by the LLM using these guidelines.
    """
    style_config = _STYLE_TEMPLATES.get(style, _STYLE_TEMPLATES["casual"])

    # Analyze the input content
    char_count = len(content)
    has_paragraphs = "\n\n" in content
    has_emoji = any(ord(c) > 0x1F600 for c in content)

    # Reference note analysis
    reference_style = ""
    if reference_note_id:
        ref_note = await adapter.get_note_detail(reference_note_id)
        if ref_note:
            reference_style = (
                f"\n\n📎 参考笔记风格：\n"
                f"- 标题：{ref_note.title}\n"
                f"- 标签：{', '.join(ref_note.tags)}\n"
                f"- 互动数据：{ref_note.likes} 赞 / {ref_note.collects} 收藏"
            )

    # Build rewrite guidelines
    changes = []
    if not has_emoji:
        changes.append("Add emojis for visual appeal (📌 💡 ✅ 🔥 etc.)")
    if not has_paragraphs:
        changes.append("Break into short paragraphs with line breaks")
    if char_count > 1000:
        changes.append("Consider condensing — ideal RedNote length is 300-800 chars")
    elif char_count < 100:
        changes.append("Expand content — add more detail, examples, or personal touches")

    changes.extend([
        f"Apply {style} tone: {style_config['tone']}",
        f"Follow structure: {style_config['structure']}",
        "Add a hook in the first line",
        "End with an interactive question (CTA)",
    ])

    rewritten = (
        f"[使用以下指南重写此内容为RedNote风格]\n\n"
        f"🎨 目标风格：{style}\n"
        f"📋 结构：{style_config['structure']}\n"
        f"🎭 语气：{style_config['tone']}\n"
        f"✨ Emoji密度：{style_config['emoji_level']}\n"
        f"{reference_style}\n\n"
        f"--- 原文 ---\n{content}\n--- 原文结束 ---\n\n"
        f"请按照以上风格指南重写原文，使其更适合RedNote平台。"
    )

    # Suggest hashtags based on content keywords
    hashtag_candidates = ["分享", "干货", "生活"]
    hashtags = [f"#{tag}" for tag in hashtag_candidates]

    result = RewrittenPost(
        rewritten=rewritten,
        title_suggestion="[基于内容生成一个吸引人的标题]",
        hashtags=hashtags,
        changes=changes,
        style_notes=f"Target style: {style}. {style_config['tone']}.",
    )
    return result.model_dump(mode="json")
