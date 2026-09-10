"""
bis_fetcher.py — BIS Standards Detail Page Fetcher

Accepts a detail URL discovered by bis_discovery.py, opens it with
Playwright, waits for Angular to render, and returns the HTML.

The rendered HTML is saved to an output file for the future parser stage.
No PostgreSQL writes are performed here.

Usage:
    python -m scripts.scraping.bis_fetcher "https://standards.bis.gov.in/website/standard-details?..."
    python -m scripts.scraping.bis_fetcher <url> --output /tmp/out.html
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bis.fetcher")

# ---------------------------------------------------------------------------
# BIS detail page selectors — isolate here so only this block needs
# updating if BIS changes their Angular component names
# ---------------------------------------------------------------------------
BIS_DETAIL_SELECTORS = {
    # Angular component host element that signals the detail page is rendered
    "detail_host": "app-standard-details, app-root[ng-version]",
    # Main content wrapper — try in order, use first match
    "content_candidates": [
        "app-standard-details",
        ".standard-detail-container",
        "mat-tab-group",
        ".detail-wrapper",
        "main",
    ],
    # Loading spinner — wait for it to disappear
    "spinner": "mat-progress-spinner, .loading-spinner, .mat-progress-bar",
}

DEFAULT_CONFIG = {
    "headless": True,
    "timeout_ms": 30_000,
    "render_wait_ms": 5_000,   # Wait after navigation for Angular to finish
    "retry_count": 2,
    "retry_delay_ms": 3_000,
}


async def _wait_for_content(page, timeout_ms: int, render_wait_ms: int) -> str:
    """
    Wait for Angular to finish rendering and return the full page HTML.
    Tries content_candidates in order; falls back to full page HTML.
    """
    # Wait for load state
    await page.wait_for_load_state("networkidle")

    # Wait for spinner to disappear (if present)
    try:
        spinner = await page.query_selector(BIS_DETAIL_SELECTORS["spinner"])
        if spinner:
            log.info("  Waiting for loading spinner to disappear...")
            await page.wait_for_selector(
                BIS_DETAIL_SELECTORS["spinner"],
                state="hidden",
                timeout=timeout_ms,
            )
    except PWTimeout:
        log.warning("  Spinner did not disappear within timeout — continuing anyway.")
    except Exception:
        pass  # Spinner selector not found — fine

    # Extra wait for Angular rendering
    await page.wait_for_timeout(render_wait_ms)

    # Try to grab the specific Angular host component first
    for selector in BIS_DETAIL_SELECTORS["content_candidates"]:
        try:
            el = await page.query_selector(selector)
            if el:
                log.info(f"  Content element found with selector: '{selector}'")
                return await page.content()
        except Exception:
            continue

    log.warning("  No specific content selector matched — returning full page HTML.")
    return await page.content()


async def fetch_detail(
    url: str,
    config: Optional[dict] = None,
) -> dict:
    """
    Fetch a BIS standard detail page.

    Args:
        url:    Canonical detail URL from bis_discovery.py.
        config: Override any DEFAULT_CONFIG keys.

    Returns:
        dict with keys:
            success     (bool)
            final_url   (str)
            html        (str)
            html_length (int)
            error       (str | None)
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    result = {
        "success": False,
        "final_url": url,
        "html": "",
        "html_length": 0,
        "error": None,
    }

    for attempt in range(1, cfg["retry_count"] + 2):
        log.info(f"Fetch attempt {attempt}/{cfg['retry_count'] + 1}: {url}")
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=cfg["headless"])
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            page.set_default_timeout(cfg["timeout_ms"])

            try:
                await page.goto(url, wait_until="domcontentloaded")

                html = await _wait_for_content(
                    page, cfg["timeout_ms"], cfg["render_wait_ms"]
                )

                final_url = page.url
                result.update({
                    "success": True,
                    "final_url": final_url,
                    "html": html,
                    "html_length": len(html),
                    "error": None,
                })
                log.info(f"  Fetch successful. Final URL: {final_url}")
                log.info(f"  HTML length: {len(html):,} characters")
                await browser.close()
                return result

            except PWTimeout as e:
                log.warning(f"  Timeout on attempt {attempt}: {e}")
                result["error"] = f"Timeout: {e}"
            except Exception as e:
                log.error(f"  Error on attempt {attempt}: {e}", exc_info=True)
                result["error"] = str(e)
            finally:
                try:
                    await browser.close()
                except Exception:
                    pass

        if attempt <= cfg["retry_count"]:
            wait_s = cfg["retry_delay_ms"] / 1000
            log.info(f"  Retrying in {wait_s}s...")
            await asyncio.sleep(wait_s)

    log.error(f"All {cfg['retry_count'] + 1} fetch attempts failed for: {url}")
    return result


def save_html(html: str, output_path: str) -> None:
    """Save rendered HTML to a file for the downstream parser stage."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    log.info(f"HTML saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BIS Standards Page Fetcher")
    parser.add_argument("url", help="Detail page URL from bis_discovery.py")
    parser.add_argument("--output", default=None,
                        help="Save rendered HTML to this file path")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--timeout", type=int, default=30_000)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    config = {
        "headless": args.headless,
        "timeout_ms": args.timeout,
        "retry_count": args.retries,
    }

    result = asyncio.run(fetch_detail(args.url, config))

    print(f"\n{'='*55}")
    print(f"Fetch Result")
    print(f"{'='*55}")
    print(f"  Success    : {result['success']}")
    print(f"  Final URL  : {result['final_url']}")
    print(f"  HTML length: {result['html_length']:,} chars")
    if result["error"]:
        print(f"  Error      : {result['error']}")

    if args.output and result["success"]:
        save_html(result["html"], args.output)
