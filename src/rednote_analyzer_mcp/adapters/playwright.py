"""Playwright browser adapter for real RedNote data.

Uses a headless (or visible) browser to navigate xiaohongshu.com and extract
real note data. Requires authentication — on first run, set REDNOTE_HEADLESS=false
to log in interactively. Cookies are saved for subsequent headless runs.

Install: pip install rednote-analyzer-mcp[browser]
Then:    playwright install chromium
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from rednote_analyzer_mcp.adapters.base import RedNoteAdapter
from rednote_analyzer_mcp.models import RedNoteAuthor, RedNoteComment, RedNoteNote

logger = logging.getLogger(__name__)

# --- Constants ---

DEFAULT_COOKIE_PATH = Path.home() / ".rednote-mcp" / "cookies.json"
DEFAULT_TIMEOUT = 30000
XHS_BASE_URL = "https://www.xiaohongshu.com"
XHS_SEARCH_URL = f"{XHS_BASE_URL}/search_result"
XHS_EXPLORE_URL = f"{XHS_BASE_URL}/explore"
XHS_USER_URL = f"{XHS_BASE_URL}/user/profile"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# CSS selectors — centralized for easy updating when XHS changes their DOM
SELECTORS = {
    "login_wall": 'text="登录后查看搜索结果"',
    "search_note_card": 'section.note-item',
    "search_note_card_alt": '[class*="note-item"], [class*="search-result"] a[href*="/explore/"]',
    "note_container": '#noteContainer, [class*="note-detail"], [class*="note-container"]',
    "note_title": '[class*="title"], h1',
    "note_content": '#detail-desc, [class*="desc"], [class*="content"]',
    "note_likes": '[class*="like"] [class*="count"], [class*="like-wrapper"] span',
    "note_collects": '[class*="collect"] [class*="count"], [class*="collect-wrapper"] span',
    "note_comments_count": '[class*="chat"] [class*="count"], [class*="comment-wrapper"] span',
    "note_tags": '[class*="tag"] a, a[href*="/search_result?keyword="]',
    "note_author": '[class*="author"] [class*="name"], [class*="user-nickname"]',
    "note_time": '[class*="date"], [class*="time"], time',
    "note_images": '#noteContainer img[src*="xhscdn"], [class*="slide"] img',
    "comment_item": '[class*="comment-item"], [class*="comment-inner"]',
    "comment_content": '[class*="content"]',
    "comment_author": '[class*="name"]',
    "comment_likes": '[class*="like"] [class*="count"]',
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


class PlaywrightAdapter(RedNoteAdapter):
    """Browser-based adapter that scrapes real data from xiaohongshu.com.

    Authentication flow:
    1. First run: Set REDNOTE_HEADLESS=false → browser opens → log in with your XHS account
    2. Cookies are saved to ~/.rednote-mcp/cookies.json
    3. Subsequent runs: cookies are loaded automatically, headless mode works

    Environment variables:
        REDNOTE_HEADLESS: "true" (default) or "false" for visible browser
        REDNOTE_COOKIE_PATH: Custom cookie file path (default: ~/.rednote-mcp/cookies.json)
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

    async def _check_login_and_handle(self, page) -> bool:
        """Check if we hit a login wall. If not headless, wait for user to log in.

        Returns True if logged in successfully, False if login is required but headless.
        """
        try:
            login_wall = await page.query_selector(SELECTORS["login_wall"])
            if login_wall is None:
                return True  # No login wall, we're good
        except Exception:
            return True  # Selector not found, assume logged in

        if self._headless:
            logger.error(
                "Login required. Run with REDNOTE_HEADLESS=false to log in interactively."
            )
            return False

        # Non-headless: wait for user to log in
        logger.info("Login required. Please log in to your XHS account in the browser...")
        logger.info("Waiting up to 120 seconds for login...")

        try:
            # Wait for login wall to disappear (user logged in)
            await page.wait_for_selector(
                SELECTORS["login_wall"],
                state="hidden",
                timeout=120000,
            )
            logger.info("Login successful! Saving cookies...")
            await self._save_cookies()
            return True
        except Exception:
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

    async def search_notes(
        self,
        query: str,
        sort: str = "hot",
        limit: int = 20,
    ) -> tuple[list[RedNoteNote], int]:
        """Search RedNote notes using the browser."""
        await self._ensure_browser()
        assert self._context is not None

        page = await self._context.new_page()
        notes: list[RedNoteNote] = []

        try:
            sort_param = "popularity_descending" if sort == "hot" else "time_descending"
            url = (
                f"{XHS_SEARCH_URL}?keyword={quote(query)}"
                f"&source=web_search_result_note&type=51&sort={sort_param}"
            )
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(3000)  # Wait for dynamic content

            if not await self._check_login_and_handle(page):
                return [], 0

            # After login, reload the search page
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(3000)

            # Try to find note cards
            cards = await page.query_selector_all(SELECTORS["search_note_card"])
            if not cards:
                cards = await page.query_selector_all(SELECTORS["search_note_card_alt"])

            for card in cards[:limit]:
                try:
                    note = await self._parse_search_card(card, page)
                    if note:
                        notes.append(note)
                except Exception as e:
                    logger.debug("Failed to parse card: %s", e)
                    continue

            # Save cookies after successful search
            await self._save_cookies()

        except Exception as e:
            logger.error("Search failed: %s", e)
        finally:
            await page.close()

        return notes, len(notes)

    async def _parse_search_card(self, card, page) -> RedNoteNote | None:
        """Parse a search result card element into a RedNoteNote."""
        # Get the link to the note
        link = await card.query_selector("a[href*='/explore/']")
        if not link:
            link = await card.query_selector("a")
        if not link:
            return None

        href = await link.get_attribute("href") or ""
        note_id = _extract_note_id_from_url(href)
        if not note_id:
            return None

        # Title
        title_el = await card.query_selector('[class*="title"], .title, h3, span')
        title = (await title_el.inner_text()).strip() if title_el else "Untitled"

        # Author
        author_el = await card.query_selector('[class*="author"], [class*="name"]')
        author_name = (await author_el.inner_text()).strip() if author_el else "Unknown"

        # Likes
        likes_el = await card.query_selector('[class*="like"] span, [class*="count"]')
        likes_text = (await likes_el.inner_text()).strip() if likes_el else "0"
        likes = _parse_count(likes_text)

        # Cover image
        img_el = await card.query_selector("img")
        cover_url = await img_el.get_attribute("src") if img_el else None
        images = [cover_url] if cover_url else []

        return RedNoteNote(
            id=note_id,
            title=title,
            content="",  # Content requires visiting the detail page
            likes=likes,
            images=images,
            publish_time=datetime.now(tz=UTC),
            author=RedNoteAuthor(id="", nickname=author_name),
        )

    async def get_note_detail(self, note_id: str) -> RedNoteNote | None:
        """Get full details of a note by visiting its page."""
        await self._ensure_browser()
        assert self._context is not None

        page = await self._context.new_page()

        try:
            url = f"{XHS_EXPLORE_URL}/{note_id}"
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(3000)

            if not await self._check_login_and_handle(page):
                return None

            # Title
            title_el = await page.query_selector(SELECTORS["note_title"])
            title = (await title_el.inner_text()).strip() if title_el else "Untitled"

            # Content
            content_el = await page.query_selector(SELECTORS["note_content"])
            content = (await content_el.inner_text()).strip() if content_el else ""

            # Engagement
            likes = 0
            likes_el = await page.query_selector(SELECTORS["note_likes"])
            if likes_el:
                likes = _parse_count(await likes_el.inner_text())

            collects = 0
            collects_el = await page.query_selector(SELECTORS["note_collects"])
            if collects_el:
                collects = _parse_count(await collects_el.inner_text())

            comments_count = 0
            comments_el = await page.query_selector(SELECTORS["note_comments_count"])
            if comments_el:
                comments_count = _parse_count(await comments_el.inner_text())

            # Author
            author_el = await page.query_selector(SELECTORS["note_author"])
            author_name = (await author_el.inner_text()).strip() if author_el else "Unknown"

            # Tags
            tag_elements = await page.query_selector_all(SELECTORS["note_tags"])
            tags = []
            for tag_el in tag_elements:
                tag_text = (await tag_el.inner_text()).strip().lstrip("#")
                if tag_text:
                    tags.append(tag_text)

            # Images
            img_elements = await page.query_selector_all(SELECTORS["note_images"])
            images = []
            for img_el in img_elements:
                src = await img_el.get_attribute("src")
                if src and "xhscdn" in src:
                    images.append(src)

            # Publish time
            time_el = await page.query_selector(SELECTORS["note_time"])
            time_text = (await time_el.inner_text()).strip() if time_el else ""
            publish_time = datetime.now(tz=UTC)  # Fallback to now
            if time_text:
                try:
                    # Try common XHS date formats
                    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M", "%m-%d", "%Y年%m月%d日"]:
                        try:
                            publish_time = datetime.strptime(time_text, fmt).replace(tzinfo=UTC)
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

            # Check if video
            video_el = await page.query_selector("video")
            video_url = None
            note_type = "normal"
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
            logger.error("Failed to get note detail: %s", e)
            return None
        finally:
            await page.close()

    async def get_note_comments(
        self,
        note_id: str,
        limit: int = 20,
    ) -> list[RedNoteComment]:
        """Get comments for a note."""
        await self._ensure_browser()
        assert self._context is not None

        page = await self._context.new_page()
        comments: list[RedNoteComment] = []

        try:
            url = f"{XHS_EXPLORE_URL}/{note_id}"
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(3000)

            if not await self._check_login_and_handle(page):
                return []

            # Scroll to load comments
            await page.evaluate("window.scrollBy(0, 500)")
            await page.wait_for_timeout(2000)

            comment_items = await page.query_selector_all(SELECTORS["comment_item"])

            for item in comment_items[:limit]:
                try:
                    content_el = await item.query_selector(SELECTORS["comment_content"])
                    content = (await content_el.inner_text()).strip() if content_el else ""

                    author_el = await item.query_selector(SELECTORS["comment_author"])
                    author_name = (
                        (await author_el.inner_text()).strip() if author_el else "Unknown"
                    )

                    likes_el = await item.query_selector(SELECTORS["comment_likes"])
                    likes = _parse_count(await likes_el.inner_text()) if likes_el else 0

                    if content:
                        comments.append(
                            RedNoteComment(
                                id=f"comment_{len(comments)}",
                                content=content,
                                likes=likes,
                                author=RedNoteAuthor(id="", nickname=author_name),
                            )
                        )
                except Exception as e:
                    logger.debug("Failed to parse comment: %s", e)
                    continue

        except Exception as e:
            logger.error("Failed to get comments: %s", e)
        finally:
            await page.close()

        return comments

    async def get_author_notes(
        self,
        author_id: str,
        limit: int = 20,
    ) -> list[RedNoteNote]:
        """Get notes from a specific author's profile page."""
        await self._ensure_browser()
        assert self._context is not None

        page = await self._context.new_page()
        notes: list[RedNoteNote] = []

        try:
            url = f"{XHS_USER_URL}/{author_id}"
            await page.goto(url, wait_until="domcontentloaded", timeout=self._timeout)
            await page.wait_for_timeout(3000)

            if not await self._check_login_and_handle(page):
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
