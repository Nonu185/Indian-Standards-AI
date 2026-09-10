"""
bis_discovery.py — BIS Standards Discovery Layer

Searches the BIS "Know Your Standards" Angular SPA and extracts:
  - standard number
  - title
  - detail URL

Selectors are isolated in BIS_SELECTORS so a CSS class change on
the BIS website only requires editing that one dict, not the logic.

Usage:
    python -m scripts.scraping.bis_discovery "Portland Cement"
    python -m scripts.scraping.bis_discovery "Safety Helmet" --max-pages 3
"""

import asyncio
import logging
import os
import re
import sys
import urllib.parse
from dataclasses import dataclass, field
from typing import List, Optional

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bis.discovery")

# ---------------------------------------------------------------------------
# BIS Portal configuration — edit these if the site structure changes
# ---------------------------------------------------------------------------
BIS_SELECTORS = {
    # URL of the search page
    "search_url": "https://standards.bis.gov.in/website/know-your-standards",
    # Search input field
    "search_input": "#isSearch",
    # Search submit button
    "search_button": "button[aria-label='Search']",
    # Anchor tags that link to a standard detail page
    "result_link": "a.text-decoration-underline[href*='/website/standard-details']",
    # Angular host element that signals the results list has rendered
    "results_host": "app-know-your-standard-card, app-know-your-standards",
    # "Next page" button — try common Angular Material paginator patterns
    "next_page_button": "button.mat-mdc-paginator-navigation-next:not([disabled])",
    # Total-results indicator text (optional — for logging)
    "result_count_label": ".mat-mdc-paginator-range-label",
}

# ---------------------------------------------------------------------------
# Configurable scraper settings
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "headless": True,
    "timeout_ms": 30_000,      # Playwright navigation / wait timeout
    "render_wait_ms": 4_000,   # Extra wait after search for Angular to render
    "request_delay_ms": 1_500, # Polite delay between page navigations
    "retry_count": 2,
    "max_pages": 10,           # Safety cap on pagination
}


@dataclass
class DiscoveredStandard:
    number: str
    title: str
    detail_url: str
    source_query: str = ""


# ---------------------------------------------------------------------------
# Core discovery logic
# ---------------------------------------------------------------------------

async def _extract_results_from_page(page, base_url: str = "https://standards.bis.gov.in") -> List[DiscoveredStandard]:
    """Extract all result links visible on the current page."""
    results: List[DiscoveredStandard] = []

    links = await page.query_selector_all(BIS_SELECTORS["result_link"])
    log.info(f"  Found {len(links)} result link(s) on page.")

    for link in links:
        href = await link.get_attribute("href") or ""
        title_attr = await link.get_attribute("title") or ""
        link_text = (await link.inner_text()).strip()

        # Build absolute URL
        if href.startswith("/"):
            href = base_url + href

        # Extract standard number from the `title` attribute first, then link text
        number = title_attr.strip() if title_attr.strip() else link_text

        # Extract the human-readable title from the `standardNumber` query param
        # which is URL-encoded e.g. "IS%20269%3A2013"
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        std_number_param = qs.get("standardNumber", [""])[0]
        if std_number_param:
            number = urllib.parse.unquote(std_number_param).strip()

        # The title is the full anchor text (may include number + description)
        title = link_text if link_text else number

        if href and number:
            results.append(DiscoveredStandard(
                number=number,
                title=title,
                detail_url=href,
            ))

    return results


async def discover(
    search_term: str,
    config: Optional[dict] = None,
) -> List[DiscoveredStandard]:
    """
    Search the BIS portal for `search_term` and return discovered standards.

    Args:
        search_term: Natural-language or IS-number search string.
        config:      Override any DEFAULT_CONFIG keys.

    Returns:
        Deduplicated list of DiscoveredStandard objects.
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    all_results: List[DiscoveredStandard] = []
    seen_numbers: set = set()

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
            log.info(f"Navigating to BIS search portal for: '{search_term}'")
            await page.goto(BIS_SELECTORS["search_url"])
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(cfg["render_wait_ms"])

            # ----------------------------------------------------------------
            # Type search term and submit
            # ----------------------------------------------------------------
            log.info("Typing search term...")
            search_input = await page.wait_for_selector(
                BIS_SELECTORS["search_input"],
                timeout=cfg["timeout_ms"],
            )
            await search_input.fill("")
            await search_input.type(search_term, delay=50)

            log.info("Submitting search...")
            search_btn = await page.wait_for_selector(
                BIS_SELECTORS["search_button"],
                timeout=cfg["timeout_ms"],
            )
            await search_btn.click()

            # Wait for Angular to render results
            await page.wait_for_timeout(cfg["render_wait_ms"])

            # ----------------------------------------------------------------
            # Paginate through results
            # ----------------------------------------------------------------
            for page_num in range(1, cfg["max_pages"] + 1):
                log.info(f"--- Scraping page {page_num} ---")

                # Optional: log total-results label if present
                try:
                    count_el = await page.query_selector(BIS_SELECTORS["result_count_label"])
                    if count_el:
                        count_text = (await count_el.inner_text()).strip()
                        log.info(f"  Pagination label: {count_text}")
                except Exception:
                    pass

                page_results = await _extract_results_from_page(page)

                # Deduplicate by standard number
                for r in page_results:
                    if r.number not in seen_numbers:
                        seen_numbers.add(r.number)
                        r.source_query = search_term
                        all_results.append(r)

                # Try to navigate to next page
                next_btn = await page.query_selector(BIS_SELECTORS["next_page_button"])
                if not next_btn:
                    log.info("No next-page button found — end of results.")
                    break

                log.info("Navigating to next page...")
                await next_btn.click()
                await page.wait_for_timeout(cfg["request_delay_ms"])
                await page.wait_for_timeout(cfg["render_wait_ms"])

        except PWTimeout as e:
            log.warning(f"Timeout during discovery: {e}")
        except Exception as e:
            log.error(f"Unexpected error during discovery: {e}", exc_info=True)
        finally:
            await browser.close()

    log.info(f"Discovery complete. Found {len(all_results)} unique standard(s).")
    return all_results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BIS Standards Discovery")
    parser.add_argument("query", help="Search term, e.g. 'Portland Cement'")
    parser.add_argument("--headless", action="store_true", default=True,
                        help="Run browser in headless mode (default: True)")
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=30_000)
    parser.add_argument("--delay", type=int, default=1_500,
                        help="Delay between pages in ms")
    args = parser.parse_args()

    config = {
        "headless": args.headless,
        "max_pages": args.max_pages,
        "timeout_ms": args.timeout,
        "request_delay_ms": args.delay,
    }

    results = asyncio.run(discover(args.query, config))

    print(f"\n{'='*55}")
    print(f"Results for: '{args.query}'")
    print(f"{'='*55}")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r.number}")
        print(f"       Title : {r.title}")
        print(f"       URL   : {r.detail_url}")
        print()
