"""Login script for RedNote Analyzer MCP.

This script opens a browser window for the user to log in to xiaohongshu.com.
Cookies are saved for subsequent headless use by the MCP server.
"""

from __future__ import annotations

import asyncio
import subprocess
import sys


def ensure_chromium_installed() -> None:
    """Check if Chromium is installed, install if not."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Try to get executable path - will fail if not installed
            p.chromium.executable_path
    except Exception:
        print("Chromium not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            print("Chromium installed successfully.")
        except subprocess.CalledProcessError:
            print("Failed to install Chromium. Please run manually:")
            print(f"  {sys.executable} -m playwright install chromium")
            sys.exit(1)


async def login() -> None:
    """Open browser for interactive login to xiaohongshu.com."""
    try:
        from rednote_analyzer_mcp.adapters.playwright import PlaywrightAdapter
    except ImportError:
        print("Error: Playwright not installed.")
        print("Run: pipx install rednote-analyzer-mcp")
        sys.exit(1)

    # Ensure Chromium is installed
    ensure_chromium_installed()

    print("Opening browser for login...")
    print("Please log in to xiaohongshu.com (scan QR code or use phone number)")
    print()

    adapter = PlaywrightAdapter(headless=False)

    # Trigger browser launch and navigate to XHS
    await adapter._ensure_browser()
    assert adapter._context is not None

    page = await adapter._context.new_page()
    await page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded")

    print("Waiting for login...")
    print("After logging in, press Ctrl+C to save cookies and exit.")
    print()

    try:
        # Wait indefinitely for user to log in
        while True:
            await asyncio.sleep(2)
            cookies = await adapter._context.cookies()
            has_session = any(c["name"] == "web_session" for c in cookies)
            if has_session:
                print("Login detected! Saving cookies...")
                await adapter._save_cookies()
                print(f"Cookies saved to ~/.rednote-mcp/cookies.json")
                print()
                print("You can now close this window and use the MCP server.")
                # Keep browser open for a bit so user can see the message
                await asyncio.sleep(3)
                break
    except KeyboardInterrupt:
        print()
        print("Saving cookies...")
        await adapter._save_cookies()
        print("Done!")
    finally:
        await adapter.close()


def main() -> None:
    """Entry point for login command."""
    asyncio.run(login())


if __name__ == "__main__":
    main()
