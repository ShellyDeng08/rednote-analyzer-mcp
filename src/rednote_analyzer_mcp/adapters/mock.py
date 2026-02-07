"""Mock adapter with realistic sample RedNote data for development and testing."""

from __future__ import annotations

from datetime import UTC, datetime

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import RedNoteAuthor, RedNoteComment, RedNoteNote

# --- Mock Data ---

_AUTHORS = [
    RedNoteAuthor(
        id="author_001",
        nickname="投资小白日记",
        avatar="https://example.com/avatar1.jpg",
        followers=52300,
        verified=False,
    ),
    RedNoteAuthor(
        id="author_002",
        nickname="美股研究员Luna",
        avatar="https://example.com/avatar2.jpg",
        followers=128000,
        verified=True,
    ),
    RedNoteAuthor(
        id="author_003",
        nickname="生活方式博主Coco",
        avatar="https://example.com/avatar3.jpg",
        followers=89000,
        verified=True,
    ),
    RedNoteAuthor(
        id="author_004",
        nickname="数码测评师老王",
        avatar="https://example.com/avatar4.jpg",
        followers=210000,
        verified=True,
    ),
    RedNoteAuthor(
        id="author_005",
        nickname="理财小姐姐",
        avatar="https://example.com/avatar5.jpg",
        followers=67000,
        verified=False,
    ),
]

_MOCK_NOTES: list[RedNoteNote] = [
    RedNoteNote(
        id="note_001",
        title="我靠美股赚了第一个10万💰新手也能学会的方法",
        content=(
            "大家好！今天分享一下我从零开始投资美股的经历。\n\n"
            "去年3月，我还是一个完全不懂投资的小白。看到身边朋友都在聊美股，"
            "我也决定试试。\n\n"
            "📌 我的方法很简单：\n"
            "1. 每月定投 SPY（标普500 ETF）\n"
            "2. 不追涨杀跌\n"
            "3. 坚持记录每一笔交易\n\n"
            "一年下来，收益率达到了28%！虽然不算特别高，但对于新手来说，"
            "稳定才是最重要的。\n\n"
            "⚠️ 投资有风险，本文不构成投资建议。每个人的情况不同，"
            "请根据自己的风险承受能力做决策。"
        ),
        note_type="normal",
        images=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
        likes=15234,
        collects=8921,
        comments_count=432,
        shares=1205,
        tags=["美股", "投资", "理财", "SPY", "ETF"],
        topics=["投资理财", "美股入门"],
        publish_time=datetime(2026, 1, 15, 10, 30, 0, tzinfo=UTC),
        author=_AUTHORS[0],
        location="上海",
    ),
    RedNoteNote(
        id="note_002",
        title="2026年最值得关注的5只AI股票🤖深度分析",
        content=(
            "AI浪潮还在继续！2026年，这5只AI股票值得重点关注：\n\n"
            "1️⃣ NVDA（英伟达）- AI芯片之王\n"
            "目前市场份额超过80%，新一代Blackwell芯片需求爆炸。\n\n"
            "2️⃣ MSFT（微软）- Copilot生态\n"
            "Azure AI收入同比增长60%+，企业AI adoption加速。\n\n"
            "3️⃣ GOOGL（谷歌）- Gemini发力\n"
            "搜索+AI双引擎驱动，Cloud业务持续高增长。\n\n"
            "4️⃣ META - AI社交\n"
            "Llama开源模型影响力大增，广告业务AI赋能。\n\n"
            "5️⃣ PLTR（Palantir）- AI平台\n"
            "政府+商业双轮驱动，AIP平台增速惊人。\n\n"
            "⚠️ 以上仅为个人研究分享，不构成投资建议！"
        ),
        note_type="normal",
        images=[
            "https://example.com/ai1.jpg",
            "https://example.com/ai2.jpg",
            "https://example.com/ai3.jpg",
        ],
        likes=28901,
        collects=15432,
        comments_count=1203,
        shares=3421,
        tags=["AI股票", "美股", "NVDA", "英伟达", "投资分析"],
        topics=["美股分析", "AI投资"],
        publish_time=datetime(2026, 1, 20, 14, 0, 0, tzinfo=UTC),
        author=_AUTHORS[1],
        location="北京",
    ),
    RedNoteNote(
        id="note_003",
        title="小白也能懂的基金定投指南📚3步搞定",
        content=(
            "很多姐妹问我怎么开始理财，其实基金定投是最简单的方式！\n\n"
            "✅ 第一步：选一个靠谱的平台\n"
            "推荐用大平台，手续费低，操作简单。\n\n"
            "✅ 第二步：选基金\n"
            "新手建议从宽基指数基金开始，比如沪深300、中证500。\n\n"
            "✅ 第三步：设定计划\n"
            "每月固定日期、固定金额，坚持就好！\n\n"
            "💡 定投的精髓就是：不择时、不追涨、不杀跌。\n"
            "让时间和复利帮你赚钱～\n\n"
            "你们有在定投吗？评论区聊聊～"
        ),
        note_type="normal",
        images=["https://example.com/fund1.jpg"],
        likes=5621,
        collects=4102,
        comments_count=289,
        shares=567,
        tags=["基金定投", "理财入门", "投资小白"],
        topics=["理财入门"],
        publish_time=datetime(2026, 1, 25, 9, 0, 0, tzinfo=UTC),
        author=_AUTHORS[4],
        location="杭州",
    ),
    RedNoteNote(
        id="note_004",
        title="iPhone 17 Pro 深度测评：这次真的值得升级吗？",
        content=(
            "iPhone 17 Pro 用了两周，来说说真实体验。\n\n"
            "🔥 优点：\n"
            "• A19 Pro芯片性能炸裂，多任务流畅\n"
            "• 新的4800万潜望长焦，拍月亮清清楚楚\n"
            "• 电池续航终于够用了，重度使用一天没问题\n"
            "• USB-C 速度提升到 40Gbps\n\n"
            "😐 缺点：\n"
            "• 价格又涨了...\n"
            "• 重量略增\n"
            "• 新配色没有想象中好看\n\n"
            "总结：如果你用的是15 Pro以前的机型，值得升级。"
            "15 Pro/16 Pro用户可以再等等。\n\n"
            "你们觉得值不值？"
        ),
        note_type="normal",
        images=[
            "https://example.com/iphone1.jpg",
            "https://example.com/iphone2.jpg",
            "https://example.com/iphone3.jpg",
            "https://example.com/iphone4.jpg",
        ],
        likes=42150,
        collects=12340,
        comments_count=3201,
        shares=5432,
        tags=["iPhone17Pro", "苹果", "数码测评", "手机推荐"],
        topics=["数码科技", "手机测评"],
        publish_time=datetime(2026, 1, 28, 20, 0, 0, tzinfo=UTC),
        author=_AUTHORS[3],
        location="深圳",
    ),
    RedNoteNote(
        id="note_005",
        title="NVDA暴跌15%！发生了什么？要抄底吗？",
        content=(
            "今天英伟达暴跌15%，很多朋友慌了。我来分析一下。\n\n"
            "📉 下跌原因：\n"
            "1. 新的出口管制政策\n"
            "2. 部分大客户推迟采购\n"
            "3. 市场整体回调\n\n"
            "🧐 我的看法：\n"
            "短期利空确实存在，但AI需求的长期趋势没有改变。"
            "英伟达的护城河依然很深——\n"
            "• CUDA生态无人能替代\n"
            "• 下一代产品路线图清晰\n"
            "• 数据中心收入仍在增长\n\n"
            "💡 操作建议：\n"
            "如果你是长期投资者，可以考虑分批建仓。\n"
            "如果你是短线选手，建议等技术面企稳再进。\n\n"
            "⚠️ 投资有风险，以上仅为个人观点，不构成投资建议。"
        ),
        note_type="normal",
        images=["https://example.com/nvda1.jpg", "https://example.com/nvda2.jpg"],
        likes=31200,
        collects=9800,
        comments_count=2100,
        shares=4300,
        tags=["NVDA", "英伟达", "美股", "AI", "抄底"],
        topics=["美股分析", "AI投资"],
        publish_time=datetime(2026, 2, 1, 16, 0, 0, tzinfo=UTC),
        author=_AUTHORS[1],
        location="北京",
    ),
    RedNoteNote(
        id="note_006",
        title="30天极简生活挑战🌿改变了我的人生观",
        content=(
            "上个月，我尝试了30天极简生活挑战。结果出乎意料！\n\n"
            "📋 规则：\n"
            "• 每天扔掉/捐出1样东西\n"
            "• 不买任何非必需品\n"
            "• 每天记录感受\n\n"
            "🌟 30天后的变化：\n"
            "1. 扔掉了87件物品（真的有这么多不需要的东西！）\n"
            "2. 省下了将近3000元\n"
            "3. 房间变得超级整洁\n"
            "4. 心情变好了，焦虑减少了\n\n"
            "最大的感悟：我们拥有的东西远比需要的多。\n"
            "当你减少物质的负担，内心反而更丰富。\n\n"
            "想试试的姐妹们，一起来打卡呀～"
        ),
        note_type="normal",
        images=["https://example.com/minimalism1.jpg", "https://example.com/minimalism2.jpg"],
        likes=18500,
        collects=12300,
        comments_count=890,
        shares=2100,
        tags=["极简生活", "断舍离", "生活方式", "自我提升"],
        topics=["生活方式", "极简主义"],
        publish_time=datetime(2026, 1, 22, 8, 0, 0, tzinfo=UTC),
        author=_AUTHORS[2],
        location="成都",
    ),
    RedNoteNote(
        id="note_007",
        title="为什么我从A股转战美股？3个真实原因",
        content=(
            "炒了5年A股，去年开始转战美股。分享3个真实原因：\n\n"
            "1️⃣ 交易机制更公平\n"
            "T+0交易，没有涨跌停限制，市场效率更高。\n\n"
            "2️⃣ 可以投资全球最好的公司\n"
            "苹果、谷歌、英伟达...这些公司的增长是实打实的。\n\n"
            "3️⃣ 信息更透明\n"
            "SEC监管严格，财报质量有保障。\n\n"
            "当然，美股也有风险：\n"
            "• 汇率波动\n"
            "• 时差问题（盘前盘后要熬夜）\n"
            "• 信息差（英文研报为主）\n\n"
            "总的来说，分散投资是最好的策略。A股美股都配一些。\n\n"
            "⚠️ 本文不构成投资建议。"
        ),
        note_type="normal",
        images=["https://example.com/stock1.jpg"],
        likes=8900,
        collects=5600,
        comments_count=670,
        shares=1200,
        tags=["美股", "A股", "投资", "股票"],
        topics=["投资理财", "美股入门"],
        publish_time=datetime(2026, 1, 18, 12, 0, 0, tzinfo=UTC),
        author=_AUTHORS[0],
        location="上海",
    ),
    RedNoteNote(
        id="note_008",
        title="MacBook Pro M5 vs M4：实测对比！提升有多大？",
        content=(
            "M5芯片的MacBook Pro终于到手了！和M4版本做个详细对比。\n\n"
            "🖥️ 基准测试：\n"
            "• Geekbench 单核：M5 3890 vs M4 3200（+21%）\n"
            "• Geekbench 多核：M5 22100 vs M4 17500（+26%）\n"
            "• 视频导出（4K 10min）：M5 2分15秒 vs M4 3分02秒\n\n"
            "💡 实际体验差异：\n"
            "• Xcode编译速度明显提升\n"
            "• AI/ML任务（Core ML）快了约40%\n"
            "• 日常使用体感差异不大\n"
            "• 续航略有提升（约1-2小时）\n\n"
            "结论：如果你是开发者或创作者，值得升级。\n"
            "普通用户M4完全够用，不需要追新。"
        ),
        note_type="video",
        images=["https://example.com/mac1.jpg"],
        video_url="https://example.com/mac_review.mp4",
        likes=35000,
        collects=8900,
        comments_count=1500,
        shares=3200,
        tags=["MacBookPro", "M5芯片", "苹果", "数码测评", "电脑推荐"],
        topics=["数码科技"],
        publish_time=datetime(2026, 2, 3, 18, 0, 0, tzinfo=UTC),
        author=_AUTHORS[3],
        location="深圳",
    ),
    RedNoteNote(
        id="note_009",
        title="月薪8000如何理财？我的真实分配方案💡",
        content=(
            "月薪8000，扣完五险一金到手大概6500。\n"
            "我的分配方案分享给大家：\n\n"
            "🏠 固定支出（3000）：\n"
            "• 房租 2000\n"
            "• 通勤 200\n"
            "• 话费网费 100\n"
            "• 水电燃气 200\n"
            "• 保险 500\n\n"
            "🍜 生活费（1500）：\n"
            "• 吃饭 1000\n"
            "• 日用品 300\n"
            "• 社交 200\n\n"
            "💰 储蓄+投资（2000）：\n"
            "• 应急基金 500（存够6个月就停）\n"
            "• 基金定投 1000\n"
            "• 学习基金 500\n\n"
            "关键是坚持！哪怕金额不多，习惯比金额更重要。\n\n"
            "你们月薪多少？怎么分配的？评论区交流～"
        ),
        note_type="normal",
        images=["https://example.com/budget1.jpg", "https://example.com/budget2.jpg"],
        likes=12300,
        collects=9800,
        comments_count=1100,
        shares=2300,
        tags=["理财", "月薪8000", "存钱", "预算分配"],
        topics=["理财入门", "生活方式"],
        publish_time=datetime(2026, 1, 10, 7, 30, 0, tzinfo=UTC),
        author=_AUTHORS[4],
        location="广州",
    ),
    RedNoteNote(
        id="note_010",
        title="2026春季穿搭灵感🌸这5套照着穿就对了",
        content=(
            "春天来了！分享5套我最近的穿搭，适合通勤和周末～\n\n"
            "Look 1️⃣ 温柔奶油风\n"
            "米白色针织 + 卡其色阔腿裤 + 乐福鞋\n\n"
            "Look 2️⃣ 知性文艺\n"
            "条纹衬衫 + 牛仔半裙 + 帆布包\n\n"
            "Look 3️⃣ 休闲运动\n"
            "连帽卫衣 + 束脚裤 + 新百伦990\n\n"
            "Look 4️⃣ 法式浪漫\n"
            "碎花连衣裙 + 小白鞋 + 草编包\n\n"
            "Look 5️⃣ 职场精英\n"
            "西装外套 + 高腰裤 + 尖头鞋\n\n"
            "春天就是要多尝试不同风格！\n"
            "你们最喜欢哪一套？"
        ),
        note_type="normal",
        images=[
            "https://example.com/outfit1.jpg",
            "https://example.com/outfit2.jpg",
            "https://example.com/outfit3.jpg",
            "https://example.com/outfit4.jpg",
            "https://example.com/outfit5.jpg",
        ],
        likes=24000,
        collects=18000,
        comments_count=560,
        shares=3100,
        tags=["春季穿搭", "穿搭灵感", "OOTD", "时尚"],
        topics=["穿搭", "时尚"],
        publish_time=datetime(2026, 2, 5, 11, 0, 0, tzinfo=UTC),
        author=_AUTHORS[2],
        location="成都",
    ),
]

_MOCK_COMMENTS: dict[str, list[RedNoteComment]] = {
    "note_001": [
        RedNoteComment(
            id="comment_001",
            content="太厉害了！我也想开始定投，请问用什么平台好？",
            likes=89,
            author=RedNoteAuthor(id="user_101", nickname="小萌新"),
            create_time=datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        ),
        RedNoteComment(
            id="comment_002",
            content="28%收益率真的很不错了，向你学习！",
            likes=45,
            author=RedNoteAuthor(id="user_102", nickname="理财小学生"),
            create_time=datetime(2026, 1, 15, 14, 30, 0, tzinfo=UTC),
        ),
        RedNoteComment(
            id="comment_003",
            content="投资有风险，新手还是要谨慎",
            likes=120,
            author=RedNoteAuthor(id="user_103", nickname="老股民"),
            create_time=datetime(2026, 1, 16, 8, 0, 0, tzinfo=UTC),
        ),
    ],
    "note_002": [
        RedNoteComment(
            id="comment_004",
            content="NVDA我已经拿了两年了，坚定看好！",
            likes=234,
            author=RedNoteAuthor(id="user_104", nickname="AI信仰者"),
            create_time=datetime(2026, 1, 20, 16, 0, 0, tzinfo=UTC),
        ),
        RedNoteComment(
            id="comment_005",
            content="分析很专业，但PLTR估值是不是太高了？",
            likes=67,
            author=RedNoteAuthor(id="user_105", nickname="价值投资人"),
            create_time=datetime(2026, 1, 21, 9, 0, 0, tzinfo=UTC),
        ),
    ],
    "note_005": [
        RedNoteComment(
            id="comment_006",
            content="我刚买完就跌了😭",
            likes=312,
            author=RedNoteAuthor(id="user_106", nickname="韭菜本菜"),
            create_time=datetime(2026, 2, 1, 17, 0, 0, tzinfo=UTC),
        ),
        RedNoteComment(
            id="comment_007",
            content="长期看好AI，逢跌加仓",
            likes=189,
            author=RedNoteAuthor(id="user_107", nickname="定投达人"),
            create_time=datetime(2026, 2, 1, 18, 30, 0, tzinfo=UTC),
        ),
    ],
}


class MockAdapter(RedNoteAdapter):
    """Mock adapter with realistic sample data for development and testing.

    This adapter returns pre-defined Chinese-language RedNote content
    covering investment, tech, lifestyle, and fashion topics.
    No network access is required.
    """

    def __init__(self) -> None:
        self._notes = {note.id: note for note in _MOCK_NOTES}
        self._comments = _MOCK_COMMENTS

    async def search_notes(
        self,
        query: str,
        sort: str = "hot",
        limit: int = 20,
    ) -> tuple[list[RedNoteNote], int]:
        """Search mock notes by keyword matching in title, content, and tags."""
        query_lower = query.lower()
        matches = [
            note
            for note in _MOCK_NOTES
            if query_lower in note.title.lower()
            or query_lower in note.content.lower()
            or any(query_lower in tag.lower() for tag in note.tags)
            or any(query_lower in topic.lower() for topic in note.topics)
        ]

        # Sort
        if sort == "hot":
            matches.sort(key=lambda n: n.likes, reverse=True)
        elif sort == "recent":
            matches.sort(key=lambda n: n.publish_time, reverse=True)

        limited = matches[:limit]
        return limited, len(matches)

    async def get_note_detail(self, note_id: str) -> RedNoteNote | None:
        """Get a mock note by ID."""
        return self._notes.get(note_id)

    async def get_note_comments(
        self,
        note_id: str,
        limit: int = 20,
    ) -> list[RedNoteComment]:
        """Get mock comments for a note."""
        comments = self._comments.get(note_id, [])
        return comments[:limit]

    async def get_author_notes(
        self,
        author_id: str,
        limit: int = 20,
    ) -> list[RedNoteNote]:
        """Get mock notes by author ID."""
        notes = [note for note in _MOCK_NOTES if note.author.id == author_id]
        notes.sort(key=lambda n: n.publish_time, reverse=True)
        return notes[:limit]
