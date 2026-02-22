# RedNote Analyzer MCP - 技术架构详解

> 本文档面向想要学习这个项目的开发者，详细讲解项目的架构设计、技术选型和 Python 技巧。

## 目录

1. [项目概述](#项目概述)
2. [整体架构](#整体架构)
3. [核心技术栈](#核心技术栈)
4. [目录结构详解](#目录结构详解)
5. [设计模式与架构原则](#设计模式与架构原则)
6. [核心模块详解](#核心模块详解)
7. [Python 技巧与最佳实践](#python-技巧与最佳实践)
8. [MCP 协议介绍](#mcp-协议介绍)
9. [数据流图](#数据流图)

---

## 项目概述

这是一个 **MCP (Model Context Protocol) 服务器**，让 AI 助手（如 Claude）能够：
- 搜索小红书笔记
- 分析笔记的爆款规律
- 生成小红书风格的内容

### 核心价值

传统方式：用户 → 手动搜索 → 手动分析 → 手动写作
本项目方式：用户 → AI 助手 → (通过 MCP) → 自动搜索/分析/生成

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI 助手 (Claude)                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ MCP 协议 (JSON-RPC)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server (server.py)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Tools      │  │   Prompts    │  │   Resources  │           │
│  │  (6个工具)    │  │  (3个模板)    │  │   (暂无)     │           │
│  └──────┬───────┘  └──────────────┘  └──────────────┘           │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Discovery   │  │   Analysis   │  │  Generation  │           │
│  │  (搜索发现)   │  │   (分析)     │  │   (生成)     │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Adapter Layer (适配器层)                      │
│              ┌─────────────────────────────┐                     │
│              │   RedNoteAdapter (抽象基类)   │                     │
│              └─────────────┬───────────────┘                     │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                  │
│         ▼                                     ▼                  │
│  ┌──────────────┐                     ┌──────────────┐          │
│  │ MockAdapter  │                     │ Playwright   │          │
│  │  (模拟数据)   │                     │   Adapter    │          │
│  └──────────────┘                     │ (真实数据)    │          │
│                                       └──────┬───────┘          │
└──────────────────────────────────────────────┼──────────────────┘
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │  xiaohongshu.com │
                                    │    (小红书网站)    │
                                    └──────────────────┘
```

---

## 核心技术栈

### 1. MCP SDK (`mcp[cli]`)

MCP (Model Context Protocol) 是 Anthropic 开源的协议，让 AI 模型可以调用外部工具。

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rednote-analyzer-mcp")

@mcp.tool()
async def my_tool(param: str) -> dict:
    """工具描述，会显示给 AI"""
    return {"result": "..."}
```

### 2. Pydantic (`pydantic>=2.0`)

用于数据验证和序列化的现代 Python 库。

```python
from pydantic import BaseModel, Field

class RedNoteNote(BaseModel):
    id: str = Field(description="笔记ID")
    title: str = Field(description="标题")
    likes: int = Field(default=0, description="点赞数")
```

### 3. Playwright (`playwright>=1.40`)

现代浏览器自动化库，用于抓取小红书数据。

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto("https://www.xiaohongshu.com")
```

---

## 目录结构详解

```
src/rednote_analyzer_mcp/
├── __init__.py              # 包初始化
├── server.py                # MCP 服务器入口 ⭐
├── login.py                 # 登录脚本
│
├── models/                  # 数据模型层
│   ├── __init__.py          # 导出所有模型
│   ├── note.py              # 笔记相关模型 (RedNoteNote, RedNoteAuthor)
│   ├── search.py            # 搜索相关模型 (SearchResult, SearchParams)
│   └── analysis.py          # 分析相关模型 (AnalysisResult, PatternResult)
│
├── adapters/                # 数据适配器层 (策略模式)
│   ├── __init__.py
│   ├── base.py              # 抽象基类 RedNoteAdapter ⭐
│   ├── mock.py              # 模拟数据适配器 (开发测试用)
│   └── playwright.py        # Playwright 浏览器适配器 (生产用) ⭐
│
├── tools/                   # 业务逻辑层
│   ├── __init__.py
│   ├── discovery.py         # 搜索和获取笔记详情
│   ├── analysis.py          # 分析笔记、提取规律
│   └── generation.py        # 生成和改写内容
│
└── prompts/                 # MCP Prompts (模板)
    └── __init__.py
```

### 分层架构说明

| 层级 | 目录 | 职责 |
|------|------|------|
| **入口层** | `server.py` | MCP 协议处理、工具注册 |
| **业务层** | `tools/` | 业务逻辑、算法实现 |
| **模型层** | `models/` | 数据结构定义、验证 |
| **适配层** | `adapters/` | 数据源抽象、可替换实现 |

---

## 设计模式与架构原则

### 1. 适配器模式 (Adapter Pattern)

**问题**：数据可能来自不同来源（模拟数据、真实网站、API）

**解决方案**：定义统一接口，不同实现可以替换

```python
# base.py - 抽象基类
class RedNoteAdapter(ABC):
    @abstractmethod
    async def search_notes(self, query: str, ...) -> tuple[list[RedNoteNote], int]:
        ...

# mock.py - 模拟实现
class MockAdapter(RedNoteAdapter):
    async def search_notes(self, query: str, ...) -> tuple[list[RedNoteNote], int]:
        return MOCK_DATA, len(MOCK_DATA)

# playwright.py - 真实实现
class PlaywrightAdapter(RedNoteAdapter):
    async def search_notes(self, query: str, ...) -> tuple[list[RedNoteNote], int]:
        # 真正去小红书抓数据
        ...
```

**使用时切换**：
```python
adapter_type = os.environ.get("REDNOTE_ADAPTER", "mock")
if adapter_type == "playwright":
    adapter = PlaywrightAdapter()
else:
    adapter = MockAdapter()
```

### 2. 单例模式 (Singleton Pattern)

**问题**：Playwright 浏览器实例创建开销大，不能每次请求都创建

**解决方案**：全局单例复用

```python
# server.py
_adapter: RedNoteAdapter | None = None

def _get_adapter() -> RedNoteAdapter:
    global _adapter
    if _adapter is not None:
        return _adapter  # 返回已有实例

    # 首次调用才创建
    _adapter = PlaywrightAdapter()
    return _adapter
```

### 3. 依赖注入 (Dependency Injection)

**问题**：业务逻辑不应该依赖具体的数据源

**解决方案**：通过参数传入 adapter

```python
# tools/discovery.py
async def search_notes(
    adapter: RedNoteAdapter,  # 注入依赖
    query: str,
    ...
) -> dict:
    notes, total = await adapter.search_notes(query, ...)
    ...
```

### 4. 分层架构 (Layered Architecture)

```
┌────────────────────┐
│   Presentation     │  ← server.py (MCP 协议)
├────────────────────┤
│   Business Logic   │  ← tools/*.py (业务逻辑)
├────────────────────┤
│   Data Access      │  ← adapters/*.py (数据访问)
├────────────────────┤
│   Domain Model     │  ← models/*.py (数据结构)
└────────────────────┘
```

---

## 核心模块详解

### 1. server.py - MCP 服务器入口

```python
from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP(
    "rednote-analyzer-mcp",
    instructions="..."  # 给 AI 的使用说明
)

# 注册工具 - 使用装饰器语法
@mcp.tool()
async def rednote_search_notes(query: str, sort: str = "hot", limit: int = 20) -> dict:
    """搜索小红书笔记。

    Args:
        query: 搜索关键词
        sort: 排序方式
        limit: 最大结果数
    """
    adapter = _get_adapter()
    return await discovery_tools.search_notes(adapter, query, sort, limit)

# 注册 Prompt 模板
@mcp.prompt()
def analyze_trending(topic: str) -> str:
    """分析某话题的热门笔记。"""
    return f"请分析关于 '{topic}' 的热门小红书笔记..."

# 启动服务器
def main():
    mcp.run()
```

**关键点**：
- `@mcp.tool()` 装饰器将函数暴露为 MCP 工具
- 函数的 docstring 会作为工具描述发送给 AI
- 返回值必须是 JSON 可序列化的

### 2. adapters/playwright.py - 浏览器适配器

这是项目中最复杂的模块，负责实际的数据抓取。

#### 核心流程

```python
class PlaywrightAdapter(RedNoteAdapter):
    async def search_notes(self, query: str, ...) -> tuple[list[RedNoteNote], int]:
        # 1. 确保浏览器已启动
        await self._ensure_browser()

        # 2. 限流控制
        await self._rate_limit()

        # 3. 创建新页面
        page = await self._context.new_page()

        # 4. 设置 API 响应拦截
        api_data = None
        async def capture_response(response):
            nonlocal api_data
            if "/api/sns/web/v1/search/notes" in response.url:
                api_data = await response.json()

        page.on("response", capture_response)

        # 5. 导航到搜索页面
        await page.goto(f"https://www.xiaohongshu.com/search_result?keyword={query}")

        # 6. 等待页面加载
        await page.wait_for_timeout(8000)

        # 7. 解析 API 数据
        notes = [_parse_search_item(item) for item in api_data["data"]["items"]]

        return notes, len(notes)
```

#### API 拦截技术

小红书是 SPA (单页应用)，数据通过 XHR/Fetch 加载。我们可以拦截这些请求：

```python
async def capture_response(response):
    # 检查是否是我们需要的 API
    if SEARCH_API in response.url:
        try:
            api_data = await response.json()  # 直接获取 JSON
        except Exception:
            pass

# 注册监听器
page.on("response", capture_response)

# 触发页面加载（会发起 API 请求）
await page.goto(url)

# 等待 API 返回
await page.wait_for_timeout(8000)

# 此时 api_data 已被填充
```

#### 限流机制

```python
# 常量定义
MIN_REQUEST_INTERVAL_MS = 3000  # 每次请求最少间隔 3 秒
MAX_REQUESTS_PER_MINUTE = 10    # 每分钟最多 10 次请求

async def _rate_limit(self) -> None:
    current_time = time.time()

    # 清理 60 秒前的记录
    self._request_times = [t for t in self._request_times if current_time - t < 60]

    # 检查每分钟限制
    if len(self._request_times) >= MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (current_time - self._request_times[0])
        if wait_time > 0:
            await asyncio.sleep(wait_time)

    # 检查最小间隔
    if self._last_request_time:
        elapsed = (current_time - self._last_request_time) * 1000
        if elapsed < MIN_REQUEST_INTERVAL_MS:
            await asyncio.sleep((MIN_REQUEST_INTERVAL_MS - elapsed) / 1000)

    # 记录本次请求
    self._last_request_time = time.time()
    self._request_times.append(self._last_request_time)
```

### 3. tools/analysis.py - 分析逻辑

使用关键词匹配进行内容分类：

```python
def _classify_title_pattern(title: str) -> TitlePattern:
    """分类标题模式"""
    # 问句式：包含问号或疑问词
    if "?" in title or "？" in title or "吗" in title:
        return TitlePattern.QUESTION

    # 数字列表式：包含数字 + 量词
    if any(c.isdigit() for c in title) and any(
        kw in title for kw in ["个", "条", "步", "招"]
    ):
        return TitlePattern.NUMBER_LIST

    # 情绪钩子：包含情绪化表达
    if any(kw in title for kw in ["震惊", "暴", "绝了", "🔥"]):
        return TitlePattern.EMOTIONAL_HOOK

    ...
```

### 4. models/note.py - 数据模型

使用 Pydantic 定义强类型模型：

```python
class RedNoteNote(BaseModel):
    """小红书笔记模型"""

    id: str = Field(description="笔记唯一ID")
    title: str = Field(description="笔记标题")
    content: str = Field(description="笔记内容")
    likes: int = Field(default=0, description="点赞数")

    # 计算属性
    @property
    def engagement_level(self) -> EngagementLevel:
        if self.likes >= 10000:
            return EngagementLevel.VIRAL
        elif self.likes >= 1000:
            return EngagementLevel.POPULAR
        ...
```

---

## Python 技巧与最佳实践

### 1. 类型注解 (Type Hints)

```python
# 基础类型
def search(query: str, limit: int = 20) -> list[str]:
    ...

# 可选类型
def get_note(note_id: str) -> RedNoteNote | None:
    ...

# 元组返回值
async def search_notes(...) -> tuple[list[RedNoteNote], int]:
    return notes, total_count

# 泛型
_adapter: RedNoteAdapter | None = None
```

### 2. 装饰器 (Decorators)

```python
# 基础装饰器使用
@mcp.tool()
async def my_tool():
    ...

# 理解装饰器原理
def mcp_tool():
    def decorator(func):
        # 注册函数到 MCP
        register_tool(func)
        return func
    return decorator
```

### 3. 异步编程 (Async/Await)

```python
# 定义异步函数
async def fetch_data() -> dict:
    await asyncio.sleep(1)  # 异步等待
    return {"data": "..."}

# 并发执行多个异步任务
async def fetch_multiple():
    results = await asyncio.gather(
        fetch_data(),
        fetch_data(),
        fetch_data(),
    )
    return results

# 异步上下文管理器
async with async_playwright() as p:
    browser = await p.chromium.launch()
```

### 4. 抽象基类 (ABC)

```python
from abc import ABC, abstractmethod

class RedNoteAdapter(ABC):
    """定义接口，强制子类实现"""

    @abstractmethod
    async def search_notes(self, query: str) -> list:
        """子类必须实现此方法"""
        ...
```

### 5. 枚举类 (Enum)

```python
from enum import StrEnum

class ContentType(StrEnum):
    TUTORIAL = "干货"
    EMOTION = "情绪"
    REVIEW = "测评"

# 使用
content_type = ContentType.TUTORIAL
print(content_type.value)  # "干货"
```

### 6. 闭包 (Closure) - API 拦截

```python
async def search_notes(self, query: str):
    api_data = None  # 外层变量

    async def capture_response(response):
        nonlocal api_data  # 声明使用外层变量
        if "/api/" in response.url:
            api_data = await response.json()

    page.on("response", capture_response)
    await page.goto(url)

    # 此时 api_data 已被内部函数修改
    return api_data
```

### 7. 正则表达式

```python
import re

# 提取笔记 ID
def extract_note_id(url: str) -> str:
    match = re.search(r"/explore/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else ""

# 计算 Emoji 数量
def count_emojis(text: str) -> int:
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f]",  # 表情符号
        flags=re.UNICODE,
    )
    return len(emoji_pattern.findall(text))
```

### 8. 环境变量配置

```python
import os

# 获取环境变量，带默认值
adapter_type = os.environ.get("REDNOTE_ADAPTER", "mock")
headless = os.environ.get("REDNOTE_HEADLESS", "true").lower() == "true"

# 布尔值转换技巧
# "true" -> True, "false" -> False, "True" -> True
is_headless = os.environ.get("HEADLESS", "true").lower() == "true"
```

### 9. Path 处理

```python
from pathlib import Path

# 跨平台路径处理
cookie_path = Path.home() / ".rednote-mcp" / "cookies.json"

# 创建目录（包括父目录）
cookie_path.parent.mkdir(parents=True, exist_ok=True)

# 读写文件
cookies = json.loads(cookie_path.read_text(encoding="utf-8"))
cookie_path.write_text(json.dumps(cookies), encoding="utf-8")
```

### 10. 延迟导入 (Lazy Import)

```python
def _get_adapter() -> RedNoteAdapter:
    if adapter_type == "playwright":
        # 只有需要时才导入（playwright 可能未安装）
        from rednote_analyzer_mcp.adapters.playwright import PlaywrightAdapter
        return PlaywrightAdapter()
    else:
        from rednote_analyzer_mcp.adapters.mock import MockAdapter
        return MockAdapter()
```

---

## MCP 协议介绍

### 什么是 MCP？

MCP (Model Context Protocol) 是 Anthropic 开发的开放协议，让 AI 模型能够安全地与外部工具交互。

### MCP 三大组件

| 组件 | 说明 | 本项目示例 |
|------|------|-----------|
| **Tools** | AI 可调用的函数 | `rednote_search_notes`, `rednote_analyze_note` |
| **Prompts** | 预定义的提示模板 | `analyze_trending`, `write_post` |
| **Resources** | 可读取的数据源 | (本项目未使用) |

### Tool 注册示例

```python
@mcp.tool()
async def rednote_search_notes(
    query: str,
    sort: str = "hot",
    limit: int = 20,
) -> dict:
    """Search RedNote notes by keyword.  # <- 这段会发给 AI

    Args:
        query: Search keyword (e.g., "美股", "投资")  # <- 参数说明
        sort: Sort order - "hot", "recent", "relevant"
        limit: Max results (1-100)
    """
    ...
```

AI 会看到：
```
Tool: rednote_search_notes
Description: Search RedNote notes by keyword.
Parameters:
  - query (string, required): Search keyword
  - sort (string, optional): Sort order
  - limit (integer, optional): Max results
```

---

## 数据流图

### 搜索笔记流程

```
1. 用户对 AI 说: "搜索关于美股的热门笔记"

2. AI 调用 MCP 工具:
   rednote_search_notes(query="美股", sort="hot", limit=20)

3. server.py 接收请求:
   @mcp.tool()
   async def rednote_search_notes(...):
       adapter = _get_adapter()
       return await discovery_tools.search_notes(adapter, ...)

4. discovery.py 处理业务逻辑:
   async def search_notes(adapter, query, ...):
       notes, total = await adapter.search_notes(query, ...)
       return SearchResult(notes=notes, ...).model_dump()

5. playwright.py 获取真实数据:
   - 启动浏览器
   - 限流检查
   - 导航到搜索页面
   - 拦截 API 响应
   - 解析 JSON 数据
   - 返回 RedNoteNote 列表

6. 数据返回给 AI:
   {
     "notes": [
       {"id": "xxx", "title": "美股入门...", "likes": 1234},
       ...
     ],
     "total": 20
   }

7. AI 向用户展示结果
```

---

## 如何扩展

### 添加新的数据适配器

```python
# my_adapter.py
from rednote_analyzer_mcp.adapters.base import RedNoteAdapter

class MyAPIAdapter(RedNoteAdapter):
    """使用官方 API 的适配器"""

    async def search_notes(self, query, sort, limit):
        response = await self.api_client.search(query)
        return self._parse_response(response)

    async def get_note_detail(self, note_id):
        ...
```

### 添加新的分析工具

```python
# tools/my_analysis.py
async def analyze_author(adapter: RedNoteAdapter, author_id: str) -> dict:
    """分析某个作者的内容风格"""
    notes = await adapter.get_author_notes(author_id)
    # 分析逻辑...
    return result

# server.py 中注册
@mcp.tool()
async def rednote_analyze_author(author_id: str) -> dict:
    """分析作者的内容风格"""
    adapter = _get_adapter()
    return await my_analysis.analyze_author(adapter, author_id)
```

---

## 总结

这个项目展示了如何构建一个现代的 Python MCP 服务器：

1. **分层架构** - 清晰的职责分离
2. **适配器模式** - 数据源可替换
3. **异步编程** - 高效的 I/O 处理
4. **类型安全** - Pydantic + Type Hints
5. **限流保护** - 避免触发反爬

希望这份文档能帮助你理解项目的设计思路和实现细节！
