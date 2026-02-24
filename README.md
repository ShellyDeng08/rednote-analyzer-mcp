# RedNote Analyzer MCP - 小红书 AI 分析工具

[![PyPI version](https://img.shields.io/pypi/v/rednote-analyzer-mcp.svg)](https://pypi.org/project/rednote-analyzer-mcp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/rednote-analyzer-mcp.svg)](https://pypi.org/project/rednote-analyzer-mcp/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

**Install**: `pipx install rednote-analyzer-mcp` | **PyPI**: [pypi.org/project/rednote-analyzer-mcp](https://pypi.org/project/rednote-analyzer-mcp/)

> **MCP Server for Xiaohongshu (小红书/RED)** - 让 Claude、ChatGPT 等 AI 助手能够**搜索、分析、生成**小红书内容。
>
> A Model Context Protocol server that enables AI assistants to search, analyze, and generate content for China's leading lifestyle social media platform.

**Keywords**: 小红书 API, 小红书爬虫, 小红书数据分析, XHS API, RedNote API, MCP Server, Claude Tools, AI Content Generation, 小红书笔记分析, 爆款分析

[English](#english) | [中文](#安装)

![Screenshot](https://raw.githubusercontent.com/ShellyDeng08/rednote-analyzer-mcp/master/assets/screenshot.png)

---

## 先决条件

- Python 3.11+
- [pipx](https://pipx.pypa.io/) 或 [uv](https://github.com/astral-sh/uv)

## 安装

### 第一步：安装

```bash
pipx install rednote-analyzer-mcp
```

### 第二步：登录小红书（必须）

```bash
rednote-login
```

浏览器会打开小红书，扫码或手机号登录，登录成功后自动保存 Cookie。

> ⚠️ 不登录直接用会返回空结果！

> ⚠️ **风控提示**：小红书有严格的反爬机制。本工具已内置限流（每分钟最多 10 次请求，每次请求间隔至少 3 秒），但仍建议：
> - 避免短时间内大量请求
> - 如果账号被限制，等待 24 小时后再试
> - 仅用于个人学习研究，不要用于商业爬取

### 第三步：配置 AI 工具

选择你用的工具：

#### Claude Code

在项目根目录创建 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

或者用命令添加：

```bash
# 添加到当前项目
claude mcp add rednote-analyzer-mcp -s local \
  -e REDNOTE_ADAPTER=playwright \
  -e REDNOTE_HEADLESS=true \
  -- uvx rednote-analyzer-mcp

# 添加到全局（所有项目可用）
claude mcp add rednote-analyzer-mcp -s user \
  -e REDNOTE_ADAPTER=playwright \
  -e REDNOTE_HEADLESS=true \
  -- uvx rednote-analyzer-mcp
```

#### Claude Desktop

编辑 `claude_desktop_config.json`：

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### Cursor

创建 `.cursor/mcp.json`（项目级）或 `~/.cursor/mcp.json`（全局）：

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### VS Code (GitHub Copilot)

创建 `.vscode/mcp.json`：

```json
{
  "servers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### Windsurf

编辑 `~/.codeium/mcp_config.json`：

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### 其他工具

通用配置模式：

| 配置项 | 值 |
|-------|---|
| command | `uvx` |
| args | `["rednote-analyzer-mcp"]` |
| env | `{"REDNOTE_ADAPTER": "playwright", "REDNOTE_HEADLESS": "true"}` |

---

## 使用

配置完成后，直接跟 AI 对话：

> "搜索小红书上关于美股的热门笔记"
>
> "分析这些笔记的爆款规律"
>
> "帮我写一篇关于基金定投的小红书文案"
>
> "把这段文字改写成小红书风格"

---

## 工具列表

| 工具 | 功能 |
|------|------|
| `rednote_search_notes` | 搜索笔记 |
| `rednote_get_note_detail` | 获取笔记详情和评论 |
| `rednote_analyze_note` | 分析笔记结构和爆款元素 |
| `rednote_extract_patterns` | 批量分析，提取规律 |
| `rednote_generate_post` | 生成帖子大纲 |
| `rednote_rewrite_in_style` | 改写为小红书风格 |

---

## 常见问题

**Q: 怎么更新？**

```bash
pipx upgrade rednote-analyzer-mcp
```

**Q: 搜索返回空结果？**

A: 没有登录。运行 `rednote-login` 登录一次。

**Q: Cookie 过期了？**

A: 重新运行 `rednote-login`。

**Q: 怎么查看 MCP 是否连接成功？**

A: Claude Code 运行 `claude mcp list`，其他工具看各自的 MCP 状态面板。

---

## License

MIT | [开发指南](CONTRIBUTING.md)

---

# English

## What is RedNote Analyzer MCP?

RedNote Analyzer MCP is a **Model Context Protocol (MCP) server** that connects AI assistants like Claude to Xiaohongshu (小红书/RED/RedNote), China's most popular lifestyle social media platform with 300M+ users.

### Use Cases
- **Content Research**: Search and analyze trending posts on any topic
- **Viral Pattern Analysis**: Extract what makes content go viral on RedNote
- **Content Generation**: Generate RedNote-style posts with AI assistance
- **Market Research**: Understand Chinese consumer trends and preferences

## Prerequisites

- Python 3.11+
- [pipx](https://pipx.pypa.io/) or [uv](https://github.com/astral-sh/uv)
- Chromium browser (auto-downloaded during install)

## Installation

### Step 1: Install

```bash
pipx install rednote-analyzer-mcp
```

### Step 2: Log in to Xiaohongshu (required)

```bash
rednote-login
```

A browser will open. Log in with your phone number or scan QR code. Cookies are saved automatically after login.

> ⚠️ Skipping login will result in empty search results!

> ⚠️ **Risk Warning**: Xiaohongshu has strict anti-scraping measures. This tool has built-in rate limiting (max 10 requests/minute, min 3 seconds between requests), but please:
> - Avoid making too many requests in a short time
> - If your account gets restricted, wait 24 hours before retrying
> - Use only for personal learning and research, not commercial scraping

### Step 3: Configure your AI tool

Choose your tool:

#### Claude Code

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

Or use CLI:

```bash
# Add to current project
claude mcp add rednote-analyzer-mcp -s local \
  -e REDNOTE_ADAPTER=playwright \
  -e REDNOTE_HEADLESS=true \
  -- uvx rednote-analyzer-mcp

# Add globally (all projects)
claude mcp add rednote-analyzer-mcp -s user \
  -e REDNOTE_ADAPTER=playwright \
  -e REDNOTE_HEADLESS=true \
  -- uvx rednote-analyzer-mcp
```

#### Claude Desktop

Edit `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### Cursor

Create `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### VS Code (GitHub Copilot)

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### Windsurf

Edit `~/.codeium/mcp_config.json`:

```json
{
  "mcpServers": {
    "rednote-analyzer-mcp": {
      "command": "uvx",
      "args": ["rednote-analyzer-mcp"],
      "env": {
        "REDNOTE_ADAPTER": "playwright",
        "REDNOTE_HEADLESS": "true"
      }
    }
  }
}
```

#### Other Tools

General config pattern:

| Key | Value |
|-----|-------|
| command | `uvx` |
| args | `["rednote-analyzer-mcp"]` |
| env | `{"REDNOTE_ADAPTER": "playwright", "REDNOTE_HEADLESS": "true"}` |

---

## Usage

After setup, talk to your AI:

> "Search for trending posts about US stocks (美股) on RedNote"
>
> "Analyze the viral patterns of these notes"
>
> "Help me write a RedNote post about ETF investing"
>
> "Rewrite this text in RedNote style"

---

## Tools

| Tool | Function |
|------|----------|
| `rednote_search_notes` | Search notes |
| `rednote_get_note_detail` | Get note details and comments |
| `rednote_analyze_note` | Analyze note structure and viral elements |
| `rednote_extract_patterns` | Batch analyze, extract patterns |
| `rednote_generate_post` | Generate post outline |
| `rednote_rewrite_in_style` | Rewrite in RedNote style |

---

## FAQ

**Q: How to update?**

```bash
pipx upgrade rednote-analyzer-mcp
```

**Q: Search returns empty results?**

A: You haven't logged in. Run `rednote-login` to log in.

**Q: Cookie expired?**

A: Run `rednote-login` again.

**Q: How to check if MCP is connected?**

A: Claude Code: run `claude mcp list`. Other tools: check their MCP status panel.

---

## License

MIT | [Contributing](CONTRIBUTING.md)
