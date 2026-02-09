# RedNote Analyzer MCP

> An MCP server that enables AI assistants (Claude, GPT, etc.) to **search, analyze, and generate** RedNote (小红书/Xiaohongshu) content through structured tools and prompts.

[English](#what-is-this) | [中文](#中文文档)

---

## What is this?

**RedNote Analyzer MCP** connects your AI assistant to the world of RedNote (小红书) — China's most popular lifestyle and content sharing platform.

Once installed, you can talk to Claude (or any MCP-compatible LLM) in natural language and it will:

- **Search** for real RedNote content by topic
- **Analyze** what makes certain posts go viral
- **Find patterns** across hundreds of notes (title styles, engagement, tags)
- **Generate** new post outlines optimized for RedNote's audience
- **Rewrite** your existing text into RedNote-friendly style

### Who is this for?

- **Content creators** who post on RedNote and want data-driven insights
- **Marketers** researching trends and engagement patterns on the platform
- **Investors** tracking discussion about US stocks (美股) and financial topics on RedNote
- **Developers** building tools around RedNote content analysis
- **Researchers** studying social media content patterns

---

## Quick Start

### Step 1: Install

```bash
# Option A: Using pip
pip install rednote-analyzer-mcp

# Option B: Using uv (recommended)
uv tool install rednote-analyzer-mcp
```

### Step 2: Connect to your AI assistant

**Claude Desktop** — Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  }
}
```

<details>
<summary>Where is claude_desktop_config.json?</summary>

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Create the file if it doesn't exist.
</details>

**Claude Code (CLI):**

```bash
claude mcp add rednote-analyzer-mcp -- uvx rednote-analyzer-mcp
```

### Step 3: Start chatting!

Open Claude and try these prompts:

> "Search for trending posts about US stocks (美股) on RedNote"

> "Analyze the content patterns of popular investment notes on RedNote"

> "Help me write a RedNote post about ETF investing for beginners"

That's it! The server ships with **built-in sample data** covering investment, tech, lifestyle, and fashion — so everything works out of the box with zero configuration.

---

## What can it do? (Tools Reference)

This MCP server provides **6 tools** and **3 prompts**. Here's what each one does, with examples of how to use them in conversation.

### Tool 1: `rednote_search_notes`

**Search RedNote notes by keyword or topic.**

Finds notes matching your query, sorted by popularity or recency. Supports Chinese and English keywords.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *(required)* | Search keyword (e.g., "美股", "穿搭", "iPhone") |
| `sort` | string | `"hot"` | Sort order: `"hot"` (most popular), `"recent"` (newest), `"relevant"` |
| `limit` | int | `20` | Max results (1-100) |

**Example prompts that use this tool:**

> "Search for RedNote posts about AI stocks"
>
> "Find the most recent posts about spring fashion on RedNote"
>
> "搜索小红书上关于基金定投的热门笔记"

**What you get back:** A list of notes with title, author, likes, bookmarks, comments, tags, and publish time.

---

### Tool 2: `rednote_get_note_detail`

**Get the full content of a specific note.**

Retrieves complete note content including text body, images, all engagement metrics, author info, and optionally the comments section.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `note_id` | string | *(required)* | The note's unique ID (from search results) |
| `include_comments` | bool | `false` | Also fetch the comments |

**Example prompts:**

> "Show me the full content of note_002"
>
> "Get the details of that NVDA post, including comments"

**What you get back:** Full note text, image URLs, engagement metrics (likes/collects/comments/shares), author details, tags, topics, location, and publish time. Optionally includes reader comments with likes and reply threads.

---

### Tool 3: `rednote_analyze_note`

**Deep analysis of a note's structure, sentiment, and patterns.**

Breaks down a note into its components: what title technique was used, what content type it is, whether the sentiment is positive/negative, what hooks and CTAs are used, emoji density, and more.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `note_id` | string | `""` | Note ID to analyze (fetches from data source) |
| `content` | string | `""` | OR provide raw text to analyze directly |
| `title` | string | `""` | Title text (used with `content` param) |

You can either provide a `note_id` (it will fetch the note) or paste `content` + `title` directly.

**Example prompts:**

> "Analyze note_001 — what makes it engaging?"
>
> "Analyze this text as a RedNote post: '今天分享一下我的投资心得...'"

**What you get back:**

| Field | Description | Example values |
|-------|-------------|----------------|
| `title_pattern` | Title writing technique | `question`, `number_list`, `emotional_hook`, `how_to`, `story`, `contrast`, `authority_claim` |
| `content_type` | Content category | `干货` (tutorial), `情绪` (emotional), `观点` (opinion), `经历` (experience), `测评` (review) |
| `sentiment` | Overall sentiment | `positive`, `negative`, `neutral`, `mixed` |
| `engagement_level` | Based on like count | `viral` (10K+), `popular` (1K-10K), `moderate` (100-1K), `low` (<100) |
| `hooks` | Identified hooks | Opening line, CTA keywords |
| `call_to_action` | CTA phrase if found | "评论区聊聊", "你们觉得", "关注我" |
| `emoji_density` | Emojis per 100 chars | `2.5` |
| `paragraph_count` | Number of paragraphs | `5` |
| `has_list` | Uses numbered/bullet lists | `true` / `false` |
| `word_count` | Character count | `350` |
| `summary` | Human-readable summary | "A viral tutorial note with number_list title pattern. Sentiment: positive. 5 paragraphs, 8 emojis." |

---

### Tool 4: `rednote_extract_patterns`

**Batch analysis: find patterns across many notes on a topic.**

This is the power tool. It searches for multiple notes on a topic, analyzes them all, and tells you what the **common patterns** are — what title styles work, what content types dominate, which tags are popular, and what the average engagement looks like.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *(required)* | Topic to analyze (e.g., "美股投资", "iPhone测评") |
| `limit` | int | `20` | Number of notes to analyze |

**Example prompts:**

> "What are the common patterns in popular US stock posts on RedNote?"
>
> "Analyze the top 20 iPhone review posts — what patterns do viral ones share?"
>
> "提取小红书上关于基金定投的爆款规律"

**What you get back:**

| Field | Description |
|-------|-------------|
| `notes_analyzed` | How many notes were analyzed |
| `title_patterns` | Distribution: e.g., `{"number_list": 8, "emotional_hook": 5, "question": 4, ...}` |
| `content_types` | Distribution: e.g., `{"干货": 10, "测评": 5, "经历": 3, ...}` |
| `common_tags` | Top 10 most used hashtags |
| `avg_likes` | Average likes across analyzed notes |
| `avg_collects` | Average bookmarks |
| `insights` | Key findings (e.g., "Most common title pattern: number_list", "High average engagement — this is a hot topic") |
| `top_performing_titles` | Top 5 best-performing titles (by likes) |

---

### Tool 5: `rednote_generate_post`

**Generate a structured RedNote post outline.**

Creates a post template with title suggestions, content structure, hashtags, and posting tips. Supports 5 content styles and 5 content verticals.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | string | *(required)* | What to write about |
| `style` | string | `"干货"` | Content style (see below) |
| `vertical` | string | `"general"` | Content vertical (see below) |
| `target_audience` | string | `""` | Optional audience description |

**Styles:**

| Style | Meaning | Structure | Tone |
|-------|---------|-----------|------|
| `干货` | Tutorial / how-to | Hook → Key Points (numbered) → Summary → CTA | Informative, helpful, structured |
| `情绪` | Emotional content | Emotional hook → Story → Insight → CTA | Personal, emotional, relatable |
| `测评` | Product review | Overview → Pros → Cons → Verdict | Objective, detailed, comparison-focused |
| `经验` | Personal experience | Background → What happened → Lessons → Advice | Personal, authentic, storytelling |
| `casual` | Casual sharing | Hook → Body → CTA | Friendly, conversational, approachable |

**Verticals:**

| Vertical | Auto-tags | Notes |
|----------|-----------|-------|
| `investment` | #投资 #理财 #美股 | Auto-adds risk disclaimer |
| `tech` | #数码 #科技 #测评 | |
| `lifestyle` | #生活方式 #日常 | |
| `fashion` | #穿搭 #时尚 #OOTD | |
| `general` | *(none)* | |

**Example prompts:**

> "Generate a RedNote post about ETF investing for beginners, tutorial style"
>
> "Create a review-style post outline for iPhone 17 Pro"
>
> "帮我写一篇关于极简生活的小红书文案，经验分享风格"

**What you get back:** Title suggestions, content outline with structure guidance, suggested hashtags, posting tips (best times, emoji usage, cover image advice), and an investment disclaimer if the topic involves financial content.

---

### Tool 6: `rednote_rewrite_in_style`

**Transform any text into RedNote-optimized style.**

Takes your raw text and provides a detailed rewrite plan: what to change, how to structure it, what tone to use, where to add emojis and hooks.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | string | *(required)* | Your original text to rewrite |
| `style` | string | `"casual"` | Target style (same 5 options as generate) |
| `reference_note_id` | string | `""` | Optional: mimic the style of this specific note |

**Example prompts:**

> "Rewrite this paragraph in RedNote casual style: 'Today I want to talk about my investment strategy...'"
>
> "Take this product review and make it RedNote-friendly in 测评 style"
>
> "把这段文字改写成小红书风格: '基金定投是一种长期投资策略...'"

**What you get back:**

| Field | Description |
|-------|-------------|
| `rewritten` | The original text wrapped with detailed style guidelines for the LLM to follow |
| `title_suggestion` | A suggested title for the rewritten content |
| `hashtags` | Suggested hashtags |
| `changes` | List of specific changes to make (e.g., "Add emojis", "Break into short paragraphs", "Add a hook in the first line") |
| `style_notes` | Description of the target style and tone |

---

## Prompts (Workflow Templates)

Prompts are pre-built multi-step workflows. When you use a prompt, the AI assistant automatically chains multiple tools together.

### Prompt 1: `analyze_trending`

**Full trend analysis workflow.**

Input: a topic (e.g., "美股")

What Claude does automatically:
1. Searches for notes on the topic
2. Extracts patterns across all results
3. Picks 2-3 interesting notes for deep analysis
4. Summarizes findings: best title patterns, content styles, common hashtags, creator insights

**How to trigger:** Ask Claude to "analyze trending content about [topic] on RedNote" or use the prompt directly in Claude Desktop's prompt selector.

---

### Prompt 2: `write_post`

**Research-driven post writing workflow.**

Input: a topic + style (e.g., "基金定投", "干货")

What Claude does automatically:
1. Researches what works for this topic (pattern extraction)
2. Generates a post template
3. Writes a complete post in Chinese with: catchy title, engaging hook, structured body with emojis, interactive CTA, relevant hashtags

---

### Prompt 3: `investment_briefing`

**Specialized investment content workflow.**

Input: a stock ticker or investment topic (e.g., "NVDA", "美股入门")

What Claude does automatically:
1. Searches for existing investment posts on this topic
2. Analyzes engagement patterns
3. Generates an investment post that: explains concepts simply, includes data/analysis, has proper risk disclaimers (⚠️ 投资有风险), ends with engagement CTA

---

## Sample Data

The server ships with **10 built-in sample notes** covering diverse topics. No configuration needed — these work out of the box:

| Note ID | Title | Topic | Likes |
|---------|-------|-------|-------|
| `note_001` | 我靠美股赚了第一个10万 | US Stock Investing | 15,234 |
| `note_002` | 2026年最值得关注的5只AI股票 | AI Stocks | 28,901 |
| `note_003` | 小白也能懂的基金定投指南 | Fund Investing | 5,621 |
| `note_004` | iPhone 17 Pro 深度测评 | Tech Review | 42,150 |
| `note_005` | NVDA暴跌15%！发生了什么？ | Stock Analysis | 31,200 |
| `note_006` | 30天极简生活挑战 | Lifestyle | 18,500 |
| `note_007` | 为什么我从A股转战美股？ | Investing | 8,900 |
| `note_008` | MacBook Pro M5 vs M4 实测对比 | Tech Review | 35,000 |
| `note_009` | 月薪8000如何理财？ | Personal Finance | 12,300 |
| `note_010` | 2026春季穿搭灵感 | Fashion | 24,000 |

Search keywords that work with mock data: `美股`, `投资`, `AI`, `iPhone`, `MacBook`, `理财`, `穿搭`, `极简`, `NVDA`, `基金`, `定投`

---

## Using Real Data (Playwright Adapter)

Want to search **real** RedNote content instead of sample data? The Playwright adapter launches a headless browser to fetch live content from xiaohongshu.com.

### Setup

```bash
# 1. Install with browser support
pip install rednote-analyzer-mcp[browser]

# 2. Install Chromium browser engine
playwright install chromium

# 3. First run: log in interactively (opens a browser window)
REDNOTE_ADAPTER=playwright REDNOTE_HEADLESS=false rednote-analyzer-mcp
# → Browser opens xiaohongshu.com → Log in with your phone number → Cookies are saved automatically

# 4. Subsequent runs: headless mode (no browser window)
REDNOTE_ADAPTER=playwright rednote-analyzer-mcp
```

### Claude Desktop Config (Real Data)

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp[browser]"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

> **Note:** Xiaohongshu requires login to view search results. The Playwright adapter saves cookies after your first interactive login so you don't have to log in again.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDNOTE_ADAPTER` | `mock` | Data source: `mock` (built-in sample data) or `playwright` (real browser) |
| `REDNOTE_HEADLESS` | `true` | Browser mode: set to `false` for first-time interactive login |
| `REDNOTE_COOKIE_PATH` | `~/.rednote-mcp/cookies.json` | Custom path for cookie storage |

---

## Architecture

```
Your AI Assistant (Claude / GPT / etc.)
         ↕ MCP Protocol (stdio)
   RedNote Analyzer MCP Server
         ↕ Adapter Interface
┌──────────────────────────────────────┐
│  MockAdapter    - Built-in samples   │
│  PlaywrightAdapter - Real browser    │
│  YourAdapter    - Custom impl        │
└──────────────────────────────────────┘
```

**Key design decisions:**
- **Adapter pattern** — Data fetching is decoupled from analysis logic. Switch data sources with one env var.
- **Pydantic models** — All data flows through validated, typed models with JSON schema auto-generation.
- **FastMCP** — Lightweight Python MCP SDK with decorator-based tool registration.
- **Lazy browser init** — Playwright only starts Chromium on first request, not at server startup.

### Custom Adapter

Want to use your own data source (API, database, etc.)? Implement the `RedNoteAdapter` interface:

```python
from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import RedNoteNote, RedNoteComment

class MyAdapter(RedNoteAdapter):
    async def search_notes(self, query, sort="hot", limit=20):
        # Return (list[RedNoteNote], total_count)
        ...

    async def get_note_detail(self, note_id):
        # Return RedNoteNote or None
        ...

    async def get_note_comments(self, note_id, limit=20):
        # Return list[RedNoteComment]
        ...

    async def get_author_notes(self, author_id, limit=20):
        # Return list[RedNoteNote]
        ...
```

---

## Development

```bash
# Clone and install
git clone https://github.com/ShellyDeng08/rednote-analyzer-mcp.git
cd rednote-analyzer-mcp
uv sync

# Run linter
uv run ruff check src/

# Run tests
uv run pytest

# Test with MCP Inspector (web UI)
uv run mcp dev src/rednote_analyzer_mcp/server.py
```

---

## Compliance

- This project does **not** contain scraping/crawling code — the browser adapter navigates pages like a normal user
- Investment-related content automatically includes risk disclaimers
- Please comply with Xiaohongshu's Terms of Service and applicable laws
- Sample data is fictional and for development/testing only

## License

MIT

---

---

# 中文文档

## 这是什么？

**RedNote Analyzer MCP** 是一个 MCP 服务器，让 AI 助手（如 Claude、GPT）能够**搜索、分析和生成**小红书内容。

安装后，你可以用自然语言跟 Claude 对话：

> "搜索小红书上关于美股的热门笔记"
>
> "分析这些笔记的爆款规律"
>
> "帮我写一篇关于基金定投的小红书文案"
>
> "把这段文字改写成小红书风格"

AI 会自动调用工具完成所有操作，并返回结构化的分析结果。

---

## 快速开始

### 安装

```bash
pip install rednote-analyzer-mcp
```

### 添加到 Claude Desktop

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  }
}
```

配置文件位置：
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 添加到 Claude Code

```bash
claude mcp add rednote-analyzer-mcp -- uvx rednote-analyzer-mcp
```

---

## 功能一览

### 6 个工具

| 工具 | 功能 | 示例用法 |
|------|------|----------|
| `rednote_search_notes` | 按关键词搜索笔记 | "搜索关于美股的笔记" |
| `rednote_get_note_detail` | 获取笔记完整内容和评论 | "查看 note_002 的详情" |
| `rednote_analyze_note` | 分析笔记结构、情感、互动 | "分析这篇笔记为什么是爆款" |
| `rednote_extract_patterns` | 批量分析，提取爆款规律 | "分析美股类笔记的共性" |
| `rednote_generate_post` | 生成帖子大纲和标题 | "帮我写一篇关于ETF的文案" |
| `rednote_rewrite_in_style` | 将文字改写为小红书风格 | "把这段话改成小红书风格" |

### 3 个提示词模板

| 模板 | 功能 | 输入 |
|------|------|------|
| `analyze_trending` | 热门趋势分析（搜索→分析→总结） | 主题（如"美股"） |
| `write_post` | 数据驱动写文案（研究→生成→创作） | 主题 + 风格 |
| `investment_briefing` | 投资内容专用创作（含风险提示） | 股票代码或投资主题 |

---

## 分析能力详解

### 标题类型识别

系统自动识别 7 种常见小红书标题类型：

| 类型 | 中文名 | 识别特征 | 示例 |
|------|--------|----------|------|
| `question` | 问句式 | 含"?"、"吗"、"呢" | "为什么我从A股转战美股？" |
| `number_list` | 数字列表 | 含数字+量词 | "5只AI股票🤖深度分析" |
| `emotional_hook` | 情绪钩子 | 含"震惊"、"绝了"、"！" | "NVDA暴跌15%！发生了什么？" |
| `how_to` | 教程式 | 含"如何"、"怎么"、"指南" | "小白也能懂的基金定投指南" |
| `story` | 故事式 | 含"我"、"经历"、"亲测" | "我靠美股赚了第一个10万" |
| `contrast` | 对比式 | 含"vs"、"对比"、"还是" | "MacBook M5 vs M4 实测对比" |
| `authority_claim` | 权威声明 | 含"深度"、"专业"、"分析" | "2026年AI行业深度研究报告" |

### 内容分类

| 类型 | 识别关键词 |
|------|-----------|
| 干货（教程） | 步骤、方法、教程、指南、第一步、✅、📌 |
| 情绪 | 感动、哭了、太难了、崩溃、开心、幸福 |
| 观点 | 我认为、我觉得、我的看法、观点、分析 |
| 经历 | 我的经历、亲身、真实体验、分享一下 |
| 测评 | 测评、评测、优点、缺点、推荐、值不值 |

### 情感分析

基于关键词的情感分类：正面、负面、中性、混合。

### 互动等级

| 等级 | 点赞范围 |
|------|---------|
| `viral` 爆款 | 10,000+ |
| `popular` 热门 | 1,000 - 10,000 |
| `moderate` 一般 | 100 - 1,000 |
| `low` 低互动 | < 100 |

---

## 5 种内容风格

生成和改写工具支持 5 种风格：

| 风格 | 内容结构 | 语气 | Emoji密度 |
|------|---------|------|----------|
| `干货` | 钩子 → 要点（编号） → 总结 → 互动 | 专业、实用、有条理 | 适中 |
| `情绪` | 情感钩子 → 故事 → 感悟 → 互动 | 个人、感性、有共鸣 | 多 |
| `测评` | 概览 → 优点 → 缺点 → 结论 | 客观、详细、对比 | 适中 |
| `经验` | 背景 → 经过 → 教训 → 建议 | 个人、真实、叙事 | 中等 |
| `casual` | 钩子 → 正文 → 互动 | 友好、随意、亲切 | 多 |

---

## 使用真实数据

默认使用内置的 10 条模拟数据。要获取真实小红书数据：

```bash
# 1. 安装浏览器适配器
pip install rednote-analyzer-mcp[browser]
playwright install chromium

# 2. 首次运行：打开浏览器登录（必须）
REDNOTE_ADAPTER=playwright REDNOTE_HEADLESS=false rednote-analyzer-mcp
# → 浏览器打开小红书 → 扫码或手机号登录 → Cookie 自动保存到 ~/.rednote-mcp/cookies.json

# 3. 之后运行：无头模式（后台运行）
REDNOTE_ADAPTER=playwright rednote-analyzer-mcp
```

Claude Desktop 配置（真实数据）：

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp[browser]"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `REDNOTE_ADAPTER` | `mock` | 数据源：`mock`（模拟数据）或 `playwright`（真实浏览器） |
| `REDNOTE_HEADLESS` | `true` | 浏览器模式：首次登录设为 `false` |
| `REDNOTE_COOKIE_PATH` | `~/.rednote-mcp/cookies.json` | Cookie 存储路径 |

---

## 开发

```bash
git clone https://github.com/ShellyDeng08/rednote-analyzer-mcp.git
cd rednote-analyzer-mcp
uv sync

# 代码检查
uv run ruff check src/

# 运行测试
uv run pytest

# MCP Inspector 测试
uv run mcp dev src/rednote_analyzer_mcp/server.py
```

---

## 合规说明

- 本项目**不包含爬虫代码** — 浏览器适配器通过正常浏览获取公开内容
- 投资相关内容自动附带风险提示（⚠️ 投资有风险，本文不构成投资建议）
- 请遵守小红书用户协议和相关法律法规
- 模拟数据为虚构内容，仅供开发测试使用

## License

MIT
