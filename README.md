# RedNote Analyzer MCP 📕🤖

> An MCP server that enables LLMs to **search, analyze, and generate** RedNote (小红书/Xiaohongshu) content through structured tools and prompts.

[English](#features) | [中文](#功能特性)

---

## Features

- 🔍 **Search** — Find RedNote notes by keyword, sorted by popularity or recency
- 📊 **Analyze** — Structural analysis: title patterns, content types, sentiment, engagement
- 🧠 **Extract Patterns** — Identify trends across multiple notes on a topic
- ✍️ **Generate** — Create post outlines with titles, hashtags, and style templates
- 🔄 **Rewrite** — Transform any text into RedNote-optimized style
- 🔌 **Adapter Pattern** — Pluggable data layer: Mock (built-in) or Playwright (real browser)

## Quick Start

### Install

```bash
# Basic (mock data)
pip install rednote-analyzer-mcp

# With browser adapter (real data)
pip install rednote-analyzer-mcp[browser]
playwright install chromium
```

### Add to Claude Desktop

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

### Add to Claude Code

```bash
claude mcp add rednote-analyzer-mcp -- uvx rednote-analyzer-mcp
```

Then just chat with Claude:

> "帮我分析小红书上关于美股的热门内容"
>
> "帮我写一篇关于ETF定投的小红书文案"
>
> "分析最近的AI投资笔记，找出爆款规律"

## Tools

| Tool | Description |
|------|-------------|
| `rednote_search_notes` | Search notes by keyword with sort and limit |
| `rednote_get_note_detail` | Get full note content, metrics, and comments |
| `rednote_analyze_note` | Analyze title pattern, content type, sentiment |
| `rednote_extract_patterns` | Extract trends from multiple notes on a topic |
| `rednote_generate_post` | Generate post outline with title, hashtags, tips |
| `rednote_rewrite_in_style` | Rewrite content in RedNote style |

## Prompts

| Prompt | Description |
|--------|-------------|
| `analyze_trending` | Workflow: search → analyze → summarize trends |
| `write_post` | Workflow: research patterns → generate → write post |
| `investment_briefing` | Workflow: specialized investment content creation |

## Architecture

```
LLM (Claude / GPT / etc.)
   ↓ MCP Protocol (stdio)
RedNote MCP Server (FastMCP)
   ↓ Adapter Interface
┌────────────────────────────────────┐
│  MockAdapter (built-in, 10 notes)  │
│  PlaywrightAdapter (real browser)  │
│  YourAdapter (implement your own)  │
└────────────────────────────────────┘
```

## Data Adapters

### MockAdapter (default)

Ships with 10 realistic Chinese-language sample notes covering investment, tech, lifestyle, and fashion. No external access needed — great for development and demos.

```bash
# Uses mock data by default
rednote-analyzer-mcp
```

### PlaywrightAdapter (real data)

Uses a headless Chromium browser to fetch real content from xiaohongshu.com. Requires one-time interactive login.

```bash
# First run: log in interactively
REDNOTE_ADAPTER=playwright REDNOTE_HEADLESS=false rednote-analyzer-mcp

# After login: cookies are saved, headless mode works
REDNOTE_ADAPTER=playwright rednote-analyzer-mcp
```

**Claude Desktop config (with Playwright):**

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

### Custom Adapter

Implement your own adapter by extending `RedNoteAdapter`:

```python
from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import RedNoteNote, RedNoteComment

class MyAdapter(RedNoteAdapter):
    async def search_notes(self, query, sort="hot", limit=20):
        # Your implementation here
        ...

    async def get_note_detail(self, note_id):
        ...

    async def get_note_comments(self, note_id, limit=20):
        ...

    async def get_author_notes(self, author_id, limit=20):
        ...
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDNOTE_ADAPTER` | `mock` | Adapter type: `mock` or `playwright` |
| `REDNOTE_HEADLESS` | `true` | Browser mode: `false` for interactive login |
| `REDNOTE_COOKIE_PATH` | `~/.rednote-mcp/cookies.json` | Cookie storage path |

## Development

```bash
# Clone and install
git clone https://github.com/xueliandeng/rednote-analyzer-mcp.git
cd rednote-analyzer-mcp
uv sync

# Run linter
uv run ruff check src/

# Run tests
uv run pytest

# Test with MCP Inspector
uv run mcp dev src/rednote_analyzer_mcp/server.py
```

## License

MIT

---

# 中文文档

## 功能特性

- 🔍 **搜索笔记** — 按关键词搜索小红书笔记，支持热门/最新排序
- 📊 **分析笔记** — 标题类型、内容分类、情感分析、互动数据
- 🧠 **提取规律** — 批量分析笔记，找出爆款共性和趋势
- ✍️ **生成文案** — 根据主题和风格生成帖子大纲、标题、标签
- 🔄 **风格改写** — 将任意文本改写为小红书风格
- 💹 **投资垂类** — 内置美股/投资领域专用模板和风险提示

## 快速开始

```bash
# 安装
pip install rednote-analyzer-mcp

# 添加到 Claude Desktop（在 claude_desktop_config.json 中添加）
```

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

然后直接跟 Claude 对话：

> "搜索小红书上关于美股的笔记"
>
> "分析这些笔记的爆款规律"
>
> "帮我写一篇关于基金定投的小红书文案"

## 使用真实数据

默认使用内置的模拟数据。要获取真实小红书数据：

```bash
# 1. 安装浏览器适配器
pip install rednote-analyzer-mcp[browser]
playwright install chromium

# 2. 首次运行：打开浏览器登录
REDNOTE_ADAPTER=playwright REDNOTE_HEADLESS=false rednote-analyzer-mcp
# → 浏览器打开 → 用手机号登录 → Cookie 自动保存

# 3. 之后运行：自动使用保存的 Cookie
REDNOTE_ADAPTER=playwright rednote-analyzer-mcp
```

## 合规说明

- 本项目不包含任何爬虫代码 — 浏览器适配器通过正常浏览获取公开内容
- 投资相关内容自动附带风险提示
- 请遵守小红书用户协议和相关法律法规
- 模拟数据为虚构内容，仅供开发测试使用
