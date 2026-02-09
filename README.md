# RedNote Analyzer MCP

[![PyPI version](https://img.shields.io/pypi/v/rednote-analyzer-mcp.svg)](https://pypi.org/project/rednote-analyzer-mcp/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An MCP server that enables AI assistants to **search, analyze, and generate** RedNote (小红书/Xiaohongshu) content — with real-time data from the platform.

[English](#what-is-this) | [中文](#中文文档)

---

## What is this?

**RedNote Analyzer MCP** connects your AI assistant to [RedNote (小红书)](https://www.xiaohongshu.com) — China's most popular lifestyle and content sharing platform with 300M+ monthly active users.

Once installed, you can talk to your AI assistant in natural language and it will:

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

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Install the package

```bash
# Using pip
pip install rednote-analyzer-mcp

# Using uv (recommended — faster)
uv tool install rednote-analyzer-mcp
```

### For real Xiaohongshu data (optional)

```bash
# Install with browser support
pip install rednote-analyzer-mcp[browser]
playwright install chromium
```

---

## Setup with Your AI Tool

This MCP server works with **any MCP-compatible AI client**. Choose your tool below:

### Claude Desktop

Add to your `claude_desktop_config.json`:

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

| OS | Path |
|---|---|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |

Create the file if it doesn't exist. Restart Claude Desktop after editing.
</details>

<details>
<summary>Use real data instead of sample data</summary>

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

See [Using Real Data](#using-real-data-playwright-adapter) for first-time login setup.
</details>

---

### Claude Code (CLI)

```bash
# Basic (sample data)
claude mcp add rednote-analyzer-mcp -- uvx rednote-analyzer-mcp

# With real data
claude mcp add rednote-analyzer-mcp \
  -e REDNOTE_ADAPTER=playwright \
  -e REDNOTE_HEADLESS=true \
  -- uvx "rednote-analyzer-mcp[browser]"
```

Verify it's connected:

```bash
claude mcp list
```

---

### Cursor

Add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

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

MCP tools are available in **Cursor Composer** (Agent mode).

---

### Windsurf (Codeium)

Add to `~/.codeium/mcp_config.json`:

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

Or go to **Settings > Tools > Windsurf Settings > Add Server**.

---

### VS Code (GitHub Copilot)

Add to `.vscode/mcp.json` in your project:

> **Note:** VS Code uses `"servers"` instead of `"mcpServers"`.

```json
{
  "servers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  }
}
```

Requires Agent Mode enabled (`chat.agent.enabled: true`).

---

### Cline (VS Code Extension)

Open Cline pane > MCP Servers icon > Configure > **Configure MCP Servers**, then add:

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

### Zed

Add to Zed's `settings.json` (Zed > Settings > Open Settings):

> **Note:** Zed uses `"context_servers"` instead of `"mcpServers"`.

```json
{
  "context_servers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  }
}
```

---

### Continue.dev

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "rednote-analyzer-mcp",
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  ]
}
```

Works in both VS Code and JetBrains IDEs.

---

### Other MCP-Compatible Tools

This server works with any tool that supports the [Model Context Protocol](https://modelcontextprotocol.io/), including:

| Tool | Config Notes |
|------|-------------|
| **Amazon Q CLI** | `brew install amazon-q`, add MCP via config |
| **ChatGPT** | Remote MCP servers via connections UI |
| **Roo Code** | Similar to Cline config |
| **LM Studio** | Uses `mcp.json` config |
| **JetBrains AI** | See [JetBrains docs](https://www.jetbrains.com/help/ai-assistant/mcp.html) |
| **Gemini CLI** | See [Gemini CLI docs](https://geminicli.com/docs/tools/mcp-server/) |
| **goose** | See [Goose extensions](https://block.github.io/goose/docs/getting-started/using-extensions/) |

The general pattern for any stdio MCP client is:
- **Command:** `uvx`
- **Args:** `["rednote-analyzer-mcp"]`
- **Env (for real data):** `{"REDNOTE_ADAPTER": "playwright", "REDNOTE_HEADLESS": "true"}`

---

## Quick Start

Once connected, try these prompts in your AI assistant:

> "Search for trending posts about US stocks (美股) on RedNote"

> "Analyze the content patterns of popular investment notes on RedNote"

> "Help me write a RedNote post about ETF investing for beginners"

> "搜索小红书上关于基金定投的热门笔记"

The server ships with **built-in sample data** covering investment, tech, lifestyle, and fashion — so everything works out of the box with zero configuration.

---

## Tools Reference

This MCP server provides **6 tools** and **3 prompts**.

### `rednote_search_notes`

**Search RedNote notes by keyword or topic.**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *(required)* | Search keyword (e.g., "美股", "穿搭", "iPhone") |
| `sort` | string | `"hot"` | `"hot"` (popular), `"recent"` (newest), `"relevant"` |
| `limit` | int | `20` | Max results (1-100) |

**Returns:** List of notes with title, author, likes, bookmarks, comments, tags, and publish time.

---

### `rednote_get_note_detail`

**Get the full content of a specific note.**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `note_id` | string | *(required)* | The note's unique ID (from search results) |
| `include_comments` | bool | `false` | Also fetch the comments |

**Returns:** Full note text, images, engagement metrics, author details, tags, and optionally comments with reply threads.

---

### `rednote_analyze_note`

**Deep analysis of a note's structure, sentiment, and patterns.**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `note_id` | string | `""` | Note ID to analyze |
| `content` | string | `""` | OR provide raw text directly |
| `title` | string | `""` | Title text (used with `content`) |

**Returns:** Title pattern (`question`, `number_list`, `emotional_hook`, `how_to`, `story`, `contrast`, `authority_claim`), content type, sentiment, engagement level, hooks, CTA, emoji density, and more.

---

### `rednote_extract_patterns`

**Batch analysis: find patterns across many notes on a topic.**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *(required)* | Topic to analyze |
| `limit` | int | `20` | Number of notes to analyze |

**Returns:** Title pattern distribution, content type distribution, common tags, average engagement metrics, key insights, and top-performing titles.

---

### `rednote_generate_post`

**Generate a structured RedNote post outline.**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | string | *(required)* | What to write about |
| `style` | string | `"干货"` | `"干货"` (tutorial), `"情绪"` (emotional), `"测评"` (review), `"经验"` (experience), `"casual"` |
| `vertical` | string | `"general"` | `"investment"`, `"tech"`, `"lifestyle"`, `"fashion"`, `"general"` |
| `target_audience` | string | `""` | Optional audience description |

**Returns:** Title suggestions, content outline, hashtags, and posting tips.

---

### `rednote_rewrite_in_style`

**Transform any text into RedNote-optimized style.**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | string | *(required)* | Your original text |
| `style` | string | `"casual"` | Target style (same 5 options as generate) |
| `reference_note_id` | string | `""` | Optional: mimic a specific note's style |

**Returns:** Rewrite guidelines, title suggestion, hashtags, list of specific changes, and style notes.

---

## Prompts (Workflow Templates)

Prompts are pre-built multi-step workflows that chain multiple tools together automatically.

| Prompt | What it does | Input |
|--------|-------------|-------|
| `analyze_trending` | Search → Extract patterns → Deep-analyze top notes → Summarize findings | Topic (e.g., "美股") |
| `write_post` | Research patterns → Generate template → Write complete post in Chinese | Topic + style |
| `investment_briefing` | Search investment posts → Analyze patterns → Generate post with risk disclaimers | Ticker or topic |

---

## Sample Data

The server ships with **10 built-in sample notes** for testing. No configuration needed:

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

Search keywords: `美股`, `投资`, `AI`, `iPhone`, `MacBook`, `理财`, `穿搭`, `极简`, `NVDA`, `基金`, `定投`

---

## Using Real Data (Playwright Adapter)

Want to search **real** RedNote content instead of sample data? The Playwright adapter uses a headless browser to fetch live content from xiaohongshu.com.

### First-time setup

```bash
# 1. Install with browser support
pip install rednote-analyzer-mcp[browser]

# 2. Install Chromium
playwright install chromium

# 3. First run: log in interactively (opens a browser window)
REDNOTE_ADAPTER=playwright REDNOTE_HEADLESS=false rednote-analyzer-mcp
# → Browser opens xiaohongshu.com
# → Log in with your phone number or scan QR code
# → Cookies are saved automatically to ~/.rednote-mcp/cookies.json

# 4. Subsequent runs: headless mode (no browser window)
REDNOTE_ADAPTER=playwright rednote-analyzer-mcp
```

> **Note:** Xiaohongshu requires login to view content. The adapter saves cookies after your first login so you don't have to log in again. If cookies expire, re-run step 3.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDNOTE_ADAPTER` | `mock` | Data source: `mock` (sample data) or `playwright` (real browser) |
| `REDNOTE_HEADLESS` | `true` | Set to `false` for first-time interactive login |
| `REDNOTE_COOKIE_PATH` | `~/.rednote-mcp/cookies.json` | Custom path for cookie storage |

---

## Architecture

```
Your AI Assistant (Claude, Cursor, Copilot, etc.)
         ↕ MCP Protocol (stdio)
   RedNote Analyzer MCP Server
         ↕ Adapter Interface
┌──────────────────────────────────────┐
│  MockAdapter      - Built-in samples │
│  PlaywrightAdapter - Real browser    │
│  YourAdapter      - Custom impl      │
└──────────────────────────────────────┘
```

**Key design decisions:**
- **Adapter pattern** — Data fetching is decoupled from analysis logic. Switch data sources with one env var.
- **API interception** — The Playwright adapter intercepts XHS internal JSON APIs for reliable structured data, rather than fragile DOM scraping.
- **Singleton browser** — One Chromium instance is shared across all tool calls, with `xsec_token` caching for efficient navigation.
- **FastMCP** — Lightweight Python MCP SDK with decorator-based tool registration.

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

**RedNote Analyzer MCP** 是一个 MCP 服务器，让 AI 助手（Claude、Cursor、Copilot 等）能够**搜索、分析和生成**小红书内容。

安装后，你可以用自然语言跟 AI 对话：

> "搜索小红书上关于美股的热门笔记"
>
> "分析这些笔记的爆款规律"
>
> "帮我写一篇关于基金定投的小红书文案"
>
> "把这段文字改写成小红书风格"

AI 会自动调用工具完成所有操作，并返回结构化的分析结果。

---

## 安装

```bash
pip install rednote-analyzer-mcp
```

## 配置 AI 工具

### Claude Desktop

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

### Claude Code

```bash
claude mcp add rednote-analyzer-mcp -- uvx rednote-analyzer-mcp
```

### Cursor

添加到 `.cursor/mcp.json` 或 `~/.cursor/mcp.json`：

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

### Windsurf

添加到 `~/.codeium/mcp_config.json`：

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

### VS Code (GitHub Copilot)

添加到 `.vscode/mcp.json`（注意：VS Code 用 `"servers"` 而非 `"mcpServers"`）：

```json
{
  "servers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  }
}
```

### Cline

在 Cline MCP 配置中添加：

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Zed

添加到 Zed 的 `settings.json`（注意：Zed 用 `"context_servers"`）：

```json
{
  "context_servers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"]
    }
  }
}
```

---

## 6 个工具

| 工具 | 功能 | 示例用法 |
|------|------|----------|
| `rednote_search_notes` | 按关键词搜索笔记 | "搜索关于美股的笔记" |
| `rednote_get_note_detail` | 获取笔记完整内容和评论 | "查看 note_002 的详情" |
| `rednote_analyze_note` | 分析笔记结构、情感、互动 | "分析这篇笔记为什么是爆款" |
| `rednote_extract_patterns` | 批量分析，提取爆款规律 | "分析美股类笔记的共性" |
| `rednote_generate_post` | 生成帖子大纲和标题 | "帮我写一篇关于ETF的文案" |
| `rednote_rewrite_in_style` | 将文字改写为小红书风格 | "把这段话改成小红书风格" |

## 3 个提示词模板

| 模板 | 功能 | 输入 |
|------|------|------|
| `analyze_trending` | 热门趋势分析（搜索→分析→总结） | 主题（如"美股"） |
| `write_post` | 数据驱动写文案（研究→生成→创作） | 主题 + 风格 |
| `investment_briefing` | 投资内容专用创作（含风险提示） | 股票代码或投资主题 |

---

## 使用真实数据

默认使用内置模拟数据。要获取真实小红书数据：

```bash
# 1. 安装浏览器适配器
pip install rednote-analyzer-mcp[browser]
playwright install chromium

# 2. 首次运行：打开浏览器登录
REDNOTE_ADAPTER=playwright REDNOTE_HEADLESS=false rednote-analyzer-mcp
# → 浏览器打开小红书 → 扫码或手机号登录 → Cookie 自动保存

# 3. 之后运行：无头模式
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
uv run ruff check src/
uv run pytest
uv run mcp dev src/rednote_analyzer_mcp/server.py
```

---

## 合规说明

- 本项目**不包含爬虫代码** — 浏览器适配器通过正常浏览获取公开内容
- 投资相关内容自动附带风险提示
- 请遵守小红书用户协议和相关法律法规
- 模拟数据为虚构内容，仅供开发测试使用

## License

MIT
