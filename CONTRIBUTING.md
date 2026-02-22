# Contributing / 开发指南

> 想深入学习项目架构和技术实现？请阅读 [技术架构详解](docs/ARCHITECTURE.md)

## 本地开发

```bash
git clone https://github.com/ShellyDeng08/rednote-analyzer-mcp.git
cd rednote-analyzer-mcp
poetry install
```

```bash
# 运行 lint
poetry run ruff check src/

# 运行测试
poetry run pytest

# 用 MCP Inspector 测试（Web UI）
poetry run mcp dev src/rednote_analyzer_mcp/server.py
```

## 项目结构

```
src/rednote_analyzer_mcp/
├── server.py              # MCP 服务器入口
├── login.py               # 登录脚本
├── models.py              # 数据模型
├── adapters/
│   ├── base.py            # Adapter 接口
│   ├── mock.py            # 模拟数据（开发用）
│   └── playwright.py      # 浏览器适配器
└── tools/
    ├── discovery.py       # 搜索、获取详情
    ├── analysis.py        # 分析、提取规律
    └── generation.py      # 生成、改写
```

## 发布新版本

### 1. 更新版本号

```bash
# 修 bug（0.1.1 → 0.1.2）
poetry version patch

# 新功能（0.1.2 → 0.2.0）
poetry version minor

# 大改动（0.2.0 → 1.0.0）
poetry version major
```

### 2. 提交代码

```bash
git add .
git commit -m "Release vX.X.X: 简要说明"
git tag vX.X.X
git push && git push --tags
```

把 `X.X.X` 换成实际版本号。

### 3. 构建并发布到 PyPI

```bash
poetry build
poetry publish
```

### 4. 验证发布

```bash
# 等几分钟后
pipx upgrade rednote-analyzer-mcp
```

## 自定义 Adapter

实现 `RedNoteAdapter` 接口：

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
