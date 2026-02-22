"""Playwright browser adapter for real RedNote data.

Uses a headless (or visible) browser to navigate xiaohongshu.com and extract
real note data. The adapter works in two modes:

  - **Search**: Intercepts the XHS internal JSON API response from
    ``edith.xiaohongshu.com/api/sns/web/v1/search/notes`` which provides
    structured data (title, author, engagement counts, images, etc.).
  - **Note detail**: Extracts data from the rendered DOM (``#detail-title``,
    ``#detail-desc``, ``.like-wrapper .count``, etc.) after the page's
    Vue SPA hydrates.
  - **Comments**: Intercepts the comment JSON API from
    ``edith.xiaohongshu.com/api/sns/web/v2/comment/page``.

Requires authentication — on first run, set ``REDNOTE_HEADLESS=false``
to log in interactively. Cookies are saved for subsequent headless runs.

Install::

    pip install rednote-analyzer-mcp[browser]
    playwright install chromium
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import RedNoteAuthor, RedNoteComment, RedNoteNote

logger = logging.getLogger(__name__)

# --- Constants ---

DEFAULT_COOKIE_PATH = Path.home() / ".rednote-mcp" / "cookies.json"
DEFAULT_TIMEOUT = 30000
CONTENT_WAIT_MS = 8000  # Time to wait for SPA content to load

# Rate limiting settings (to avoid triggering XHS anti-scraping)
MIN_REQUEST_INTERVAL_MS = 3000  # Minimum 3 seconds between requests
MAX_REQUESTS_PER_MINUTE = 10  # Maximum 10 requests per minute
XHS_BASE_URL = "https://www.xiaohongshu.com"
XHS_SEARCH_URL = f"{XHS_BASE_URL}/search_result"
XHS_EXPLORE_URL = f"{XHS_BASE_URL}/explore"
XHS_USER_URL = f"{XHS_BASE_URL}/user/profile"

# API endpoints (used for response interception)
SEARCH_API = "/api/sns/web/v1/search/notes"
COMMENT_API = "/api/sns/web/v2/comment/page"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# DOM selectors for note detail page
DETAIL_SELECTORS = {
    "title": "#detail-title, [class*='title']",
    "content": "#detail-desc, [class*='desc']",
    "likes": ".like-wrapper .count, [class*='like'] [class*='count']",
    "collects": ".collect-wrapper .count, [class*='collect'] [class*='count']",
    "comments_count": ".chat-wrapper .count, [class*='chat'] [class*='count']",
    "author": ".username, [class*='user-nickname'], [class*='author'] [class*='name']",
    "time": "span.date, .publish-date, [class*='date']",
    "tags": "#hash-tag-anchor-element, [class*='tag'] a, a[href*='/search_result?keyword=']",
    "images": "img[src*='xhscdn'], [class*='slide'] img",
}


def _parse_count(text: str) -> int:
    """Parse engagement count text like '1.2万' or '832' into an integer."""
    text = text.strip()
    if not text:
        return 0
    text = text.replace(",", "")
    if "万" in text:
        try:
            return int(float(text.replace("万", "")) * 10000)
        except ValueError:
            return 0
    if "亿" in text:
        try:
            return int(float(text.replace("亿", "")) * 100000000)
        except ValueError:
            return 0
    try:
        return int(text)
    except ValueError:
        return 0


def _extract_note_id_from_url(url: str) -> str:
    """Extract note ID from a URL like /explore/abc123 or /discovery/item/abc123."""
    match = re.search(r"/explore/([a-zA-Z0-9]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/item/([a-zA-Z0-9]+)", url)
    if match:
        return match.group(1)
    return ""


def _parse_search_item(item: dict) -> RedNoteNote | None:
    """Parse a single item from the search API JSON into a RedNoteNote."""
    try:
        note_id = item.get("id", "")
        card = item.get("note_card", {})
        if not card or not note_id:
            return None

        title = card.get("display_title", "Untitled")
        note_type = card.get("type", "normal")

        # Author
        user = card.get("user", {})
        author = RedNoteAuthor(
            id=user.get("user_id", ""),
            nickname=user.get("nickname") or user.get("nick_name", "Unknown"),
            avatar=user.get("avatar"),
        )

        # Engagement
        interact = card.get("interact_info", {})
        likes = _parse_count(str(interact.get("liked_count", "0")))
        collects = _parse_count(str(interact.get("collected_count", "0")))
        comments_count = _parse_count(str(interact.get("comment_count", "0")))
        shares = _parse_count(str(interact.get("shared_count", "0")))

        # Images
        images = []
        cover = card.get("cover", {})
        cover_url = cover.get("url_default", "")
        if cover_url:
            images.append(cover_url)

        for img in card.get("image_list", [])[1:]:  # Skip first (same as cover)
            for info in img.get("info_list", []):
                if info.get("image_scene") == "WB_DFT":
                    images.append(info.get("url", ""))
                    break

        # Publish time (from corner tag like "3天前" or "2025-01-15")
        publish_time = datetime.now(tz=UTC)
        for tag in card.get("corner_tag_info", []):
            if tag.get("type") == "publish_time":
                time_text = tag.get("text", "")
                publish_time = _parse_relative_time(time_text)
                break

        # Video
        video_url = None
        if note_type == "video":
            video = card.get("video", {})
            if video:
                video_url = video.get("url", "")

        # Tags from card (search results don't always include tags)
        tags: list[str] = []

        return RedNoteNote(
            id=note_id,
            title=title,
            content="",  # Search results don't include full content
            note_type=note_type,
            images=images,
            video_url=video_url,
            likes=likes,
            collects=collects,
            comments_count=comments_count,
            shares=shares,
            tags=tags,
            publish_time=publish_time,
            author=author,
        )
    except Exception as e:
        logger.debug("Failed to parse search item: %s", e)
        return None


def _parse_relative_time(text: str) -> datetime:
    """Parse relative time strings like '3天前', '2小时前', '刚刚' into datetime."""
    now = datetime.now(tz=UTC)
    text = text.strip()
    if not text:
        return now

    # Absolute date formats
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue

    # Relative: "X天前", "X小时前", "X分钟前", "刚刚", "昨天"
    from datetime import timedelta

    if "刚刚" in text:
        return now
    if "昨天" in text:
        return now - timedelta(days=1)

    match = re.search(r"(\d+)\s*天前", text)
    if match:
        return now - timedelta(days=int(match.group(1)))
    match = re.search(r"(\d+)\s*小时前", text)
    if match:
        return now - timedelta(hours=int(match.group(1)))
    match = re.search(r"(\d+)\s*分钟前", text)
    if match:
        return now - timedelta(minutes=int(match.group(1)))

    return now


def _parse_comment_item(item: dict) -> RedNoteComment:
    """Parse a single comment from the comment API JSON."""
    user_info = item.get("user_info", {})
    author = RedNoteAuthor(
        id=user_info.get("user_id", ""),
        nickname=user_info.get("nickname", "Unknown"),
        avatar=user_info.get("image"),
    )

    create_time = None
    ts = item.get("create_time")
    if ts:
        try:
            create_time = datetime.fromtimestamp(ts / 1000, tz=UTC)
        except Exception:
            pass

    # Parse sub-comments (replies)
    replies = []
    for sub in item.get("sub_comments", []):
        replies.append(_parse_comment_item(sub))

    return RedNoteComment(
        id=item.get("id", ""),
        content=item.get("content", ""),
        likes=_parse_count(str(item.get("like_count", "0"))),
        author=author,
        create_time=create_time,
        replies=replies,
    )


class PlaywrightAdapter(RedNoteAdapter):
    """Browser-based adapter that fetches real data from xiaohongshu.com.

    Uses API response interception for search and comments (structured JSON),
    and DOM extraction for note detail pages (rendered HTML).

    Authentication flow:
    1. First run: Set REDNOTE_HEADLESS=false → browser opens → log in
    2. Cookies are saved to ~/.rednote-mcp/cookies.json
    3. Subsequent runs: cookies are loaded automatically, headless mode works

    Environment variables:
        REDNOTE_HEADLESS: "true" (default) or "false" for visible browser
        REDNOTE_COOKIE_PATH: Custom cookie file path
    """

    def __init__(
        self,
        headless: bool = True,
        cookie_path: Path | str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._headless = headless
        self._cookie_path = Path(cookie_path) if cookie_path else DEFAULT_COOKIE_PATH
        self._timeout = timeout
        self._pw = None
        self._browser = None
        self._context = None
        self._initialized = False
        # Cache xsec_tokens from search results (note_id -> xsec_token)
        self._xsec_tokens: dict[str, str] = {}
        # Rate limiting state
        self._last_request_time: float = 0
        self._request_times: list[float] = []  # Timestamps of recent requests

    async def _ensure_browser(self) -> None:
        """Lazy-initialize the browser and load cookies if available."""
        if self._initialized:
            return

        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            raise RuntimeError(
                "Playwright is not installed. Install with:\n"
                "  pip install rednote-analyzer-mcp[browser]\n"
                "  playwright install chromium"
            ) from e

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self._headless)
        self._context = await self._browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )

        # Load saved cookies if they exist
        if self._cookie_path.exists():
            try:
                cookies = json.loads(self._cookie_path.read_text(encoding="utf-8"))
                await self._context.add_cookies(cookies)
                logger.info("Loaded saved cookies from %s", self._cookie_path)
            except Exception as e:
                logger.warning("Failed to load cookies: %s", e)

        self._initialized = True

    async def _rate_limit(self) -> None:
        """Enforce rate limiting to avoid triggering XHS anti-scraping.

        - Ensures minimum interval between requests (3 seconds)
        - Limits to maximum 10 requests per minute
        """
        current_time = time.time()

        # Clean up old request timestamps (older than 60 seconds)
        self._request_times = [t for t in self._request_times if current_time - t < 60]

        # Check requests per minute limit
        if len(self._request_times) >= MAX_REQUESTS_PER_MINUTE:
            oldest_in_window = self._request_times[0]
            wait_time = 60 - (current_time - oldest_in_window)
            if wait_time > 0:
                logger.info(
                    "Rate limit: %d requests in last minute, waiting %.1f seconds...",
                    len(self._request_times),
                    wait_time,
                )
                await asyncio.sleep(wait_time)
                current_time = time.time()

        # Check minimum interval between requests
        time_since_last = (current_time - self._last_request_time) * 1000  # Convert to ms
        if time_since_last < MIN_REQUEST_INTERVAL_MS:
            wait_ms = MIN_REQUEST_INTERVAL_MS - time_since_last
            logger.debug("Rate limit: waiting %.0f ms before next request", wait_ms)
            await asyncio.sleep(wait_ms / 1000)

        # Record this request
        self._last_request_time = time.time()
        self._request_times.append(self._last_request_time)

    async def _check_login(self, page) -> bool:
        """Check if the session is authenticated by looking for login prompts.

        Returns True if logged in, False otherwise.
        If not headless and login is needed, waits for the user to log in.
        """
        # Check for common login indicators
        try:
            login_el = await page.query_selector(
                'text="登录后查看搜索结果", text="登录后推荐更懂你的笔记"'
            )
            if login_el is None:
                # Also check if the web_session cookie exists
                cookies = await self._context.cookies() if self._context else []
                has_session = any(c["name"] == "web_session" for c in cookies)
                if has_session:
                    return True
                # No login wall text found and no session — might still be OK
                return True
        except Exception:
            return True

        if self._headless:
            logger.error(
                "Login required. Run with REDNOTE_HEADLESS=false to log in interactively."
            )
            return False

        # Non-headless: wait for user to log in
        logger.info("Login required. Please log in to your XHS account in the browser...")
        logger.info("Waiting up to 120 seconds for login...")

        for _ in range(60):
            await page.wait_for_timeout(2000)
            cookies = await self._context.cookies() if self._context else []
            has_session = any(c["name"] == "web_session" for c in cookies)
            if has_session:
                logger.info("Login successful! Saving cookies...")
                await self._save_cookies()
                return True

        logger.error("Login timeout. Please try again.")
        return False

    async def _save_cookies(self) -> None:
        """Save browser cookies to disk for future sessions."""
        if self._context is None:
            return
        try:
            self._cookie_path.parent.mkdir(parents=True, exist_ok=True)
            cookies = await self._context.cookies()
            self._cookie_path.write_text(
                json.dumps(cookies, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info("Cookies saved to %s", self._cookie_path)
        except Exception as e:
            logger.warning("Failed to save cookies: %s", e)

    # ------------------------------------------------------------------
    # search_notes — intercepts the JSON API response
    # ------------------------------------------------------------------

    async def search_notes(
        self,
        query: str,
        sort: str = "hot",
        limit: int = 20,
    ) -> tuple[list[RedNoteNote], int]:
        """Search RedNote notes by intercepting the internal search API."""
        await self._ensure_browser()
        await self._rate_limit()
        assert self._context is not None

        page = await self._context.new_page()
        notes: list[RedNoteNote] = []
        api_data: dict | None = None

        async def _capture_search(response):
            nonlocal api_data
            if SEARCH_API in response.url:
                try:
                    api_data = await response.json()
                except Exception:
                    pass

        page.on("response", _capture_search)

        try:
            sort_map = {
                "hot": "popularity_descending",
                "recent": "time_descending",
                "relevant": "general",
            }
            sort_param = sort_map.get(sort, "general")
            url = (
                f"{XHS_SEARCH_URL}?keyword={quote(query)}"
                f"&source=web_search_result_note&type=51&sort={sort_param}"
            )
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(CONTENT_WAIT_MS)

            if not await self._check_login(page):
                return [], 0

            # If login happened, we need to reload
            if api_data is None:
                await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
                await page.wait_for_timeout(CONTENT_WAIT_MS)

            if api_data and api_data.get("success") is not False:
                items = api_data.get("data", {}).get("items", [])
                for item in items[:limit]:
                    note = _parse_search_item(item)
                    if note:
                        notes.append(note)
                        # Cache xsec_token for later detail/comment lookups
                        xsec = item.get("xsec_token", "")
                        if xsec:
                            self._xsec_tokens[note.id] = xsec
                logger.info(
                    "Search '%s': parsed %d notes from API (%d items)",
                    query,
                    len(notes),
                    len(items),
                )
            else:
                logger.warning(
                    "Search API returned no data or failed. api_data=%s",
                    json.dumps(api_data, ensure_ascii=False)[:200] if api_data else "None",
                )

            await self._save_cookies()

        except Exception as e:
            logger.error("Search failed: %s", e)
        finally:
            page.remove_listener("response", _capture_search)
            await page.close()

        return notes, len(notes)

    # ------------------------------------------------------------------
    # get_note_detail — extracts from rendered DOM
    # ------------------------------------------------------------------

    async def get_note_detail(self, note_id: str) -> RedNoteNote | None:
        """Get full details of a note by visiting its page and extracting DOM."""
        await self._ensure_browser()
        await self._rate_limit()
        assert self._context is not None

        page = await self._context.new_page()

        try:
            # Build URL with xsec_token if available (required by XHS to load the note)
            url = f"{XHS_EXPLORE_URL}/{note_id}"
            xsec = self._xsec_tokens.get(note_id, "")
            if xsec:
                url += f"?xsec_token={quote(xsec)}&xsec_source=pc_search"
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(CONTENT_WAIT_MS)

            if not await self._check_login(page):
                return None

            # Title
            title = "Untitled"
            title_el = await page.query_selector(DETAIL_SELECTORS["title"])
            if title_el:
                title = (await title_el.inner_text()).strip()

            # Content (description)
            content = ""
            content_el = await page.query_selector(DETAIL_SELECTORS["content"])
            if content_el:
                content = (await content_el.inner_text()).strip()

            # Engagement metrics
            likes = 0
            likes_el = await page.query_selector(DETAIL_SELECTORS["likes"])
            if likes_el:
                likes = _parse_count(await likes_el.inner_text())

            collects = 0
            collects_el = await page.query_selector(DETAIL_SELECTORS["collects"])
            if collects_el:
                collects = _parse_count(await collects_el.inner_text())

            comments_count = 0
            comments_el = await page.query_selector(DETAIL_SELECTORS["comments_count"])
            if comments_el:
                comments_count = _parse_count(await comments_el.inner_text())

            # Author
            author_name = "Unknown"
            author_el = await page.query_selector(DETAIL_SELECTORS["author"])
            if author_el:
                author_name = (await author_el.inner_text()).strip()

            # Tags (from hashtags in the description)
            tags: list[str] = []
            tag_elements = await page.query_selector_all(DETAIL_SELECTORS["tags"])
            for tag_el in tag_elements:
                tag_text = (await tag_el.inner_text()).strip().lstrip("#")
                if tag_text:
                    tags.append(tag_text)

            # Also extract hashtags from the content text itself
            if content:
                for m in re.finditer(r"#(\S+?)(?:\s|$)", content):
                    tag_val = m.group(1).strip()
                    if tag_val and tag_val not in tags:
                        tags.append(tag_val)

            # Images
            images: list[str] = []
            img_elements = await page.query_selector_all(DETAIL_SELECTORS["images"])
            for img_el in img_elements:
                src = await img_el.get_attribute("src")
                if src and "xhscdn" in src:
                    images.append(src)

            # Publish time
            publish_time = datetime.now(tz=UTC)
            time_el = await page.query_selector(DETAIL_SELECTORS["time"])
            if time_el:
                time_text = (await time_el.inner_text()).strip()
                # Remove location suffix like "3天前 河北" → "3天前"
                time_part = time_text.split()[0] if time_text else ""
                if time_part:
                    publish_time = _parse_relative_time(time_part)

            # Video
            video_url = None
            note_type = "normal"
            video_el = await page.query_selector("video")
            if video_el:
                video_url = await video_el.get_attribute("src")
                note_type = "video"

            await self._save_cookies()

            return RedNoteNote(
                id=note_id,
                title=title,
                content=content,
                note_type=note_type,
                images=images,
                video_url=video_url,
                likes=likes,
                collects=collects,
                comments_count=comments_count,
                tags=tags,
                publish_time=publish_time,
                author=RedNoteAuthor(id="", nickname=author_name),
            )

        except Exception as e:
            logger.error("Failed to get note detail for %s: %s", note_id, e)
            return None
        finally:
            await page.close()

    # ------------------------------------------------------------------
    # get_note_comments — intercepts the JSON comment API
    # ------------------------------------------------------------------

    async def get_note_comments(
        self,
        note_id: str,
        limit: int = 20,
    ) -> list[RedNoteComment]:
        """Get comments for a note by intercepting the comment API."""
        await self._ensure_browser()
        await self._rate_limit()
        assert self._context is not None

        page = await self._context.new_page()
        comments: list[RedNoteComment] = []
        api_data: dict | None = None

        async def _capture_comments(response):
            nonlocal api_data
            if COMMENT_API in response.url and note_id in response.url:
                try:
                    api_data = await response.json()
                except Exception:
                    pass

        page.on("response", _capture_comments)

        try:
            # Build URL with xsec_token if available
            url = f"{XHS_EXPLORE_URL}/{note_id}"
            xsec = self._xsec_tokens.get(note_id, "")
            if xsec:
                url += f"?xsec_token={quote(xsec)}&xsec_source=pc_search"
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(CONTENT_WAIT_MS)

            if not await self._check_login(page):
                return []

            # Scroll down to trigger comment loading
            await page.evaluate("window.scrollBy(0, 800)")
            await page.wait_for_timeout(3000)

            if api_data and api_data.get("success"):
                raw_comments = api_data.get("data", {}).get("comments", [])
                for item in raw_comments[:limit]:
                    comments.append(_parse_comment_item(item))
                logger.info(
                    "Comments for %s: parsed %d from API", note_id, len(comments)
                )
            else:
                logger.warning("Comment API returned no data for %s", note_id)

        except Exception as e:
            logger.error("Failed to get comments for %s: %s", note_id, e)
        finally:
            page.remove_listener("response", _capture_comments)
            await page.close()

        return comments

    # ------------------------------------------------------------------
    # get_author_notes — extracts from profile page DOM
    # ------------------------------------------------------------------

    async def get_author_notes(
        self,
        author_id: str,
        limit: int = 20,
    ) -> list[RedNoteNote]:
        """Get notes from a specific author's profile page."""
        await self._ensure_browser()
        await self._rate_limit()
        assert self._context is not None

        page = await self._context.new_page()
        notes: list[RedNoteNote] = []

        try:
            url = f"{XHS_USER_URL}/{author_id}"
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(CONTENT_WAIT_MS)

            if not await self._check_login(page):
                return []

            # Find note cards on profile page
            cards = await page.query_selector_all(
                '[class*="note-item"] a, [class*="cover"] a'
            )

            for card in cards[:limit]:
                try:
                    href = await card.get_attribute("href") or ""
                    nid = _extract_note_id_from_url(href)
                    if not nid:
                        continue

                    title_el = await card.query_selector('[class*="title"], span')
                    title = (await title_el.inner_text()).strip() if title_el else ""

                    notes.append(
                        RedNoteNote(
                            id=nid,
                            title=title or "Untitled",
                            content="",
                            publish_time=datetime.now(tz=UTC),
                            author=RedNoteAuthor(id=author_id, nickname=""),
                        )
                    )
                except Exception as e:
                    logger.debug("Failed to parse author note: %s", e)
                    continue

        except Exception as e:
            logger.error("Failed to get author notes: %s", e)
        finally:
            await page.close()

        return notes

    async def close(self) -> None:
        """Clean up browser resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._pw:
            await self._pw.stop()
            self._pw = None
        self._initialized = False
