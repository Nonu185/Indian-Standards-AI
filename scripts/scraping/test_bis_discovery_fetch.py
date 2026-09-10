"""
test_bis_discovery_fetch.py — End-to-end test for BIS discovery + fetch.

Tests:
  1. Searches BIS for "Ordinary Portland Cement"
  2. Prints all discovered standards (number, title, URL)
  3. Takes the first discovered URL and fetches the rendered HTML
  4. Reports final URL and HTML length
  5. Does NOT insert anything into PostgreSQL.

Run:
    cd /path/to/Indian-Standards-AI
    source ai-services/venv/bin/activate
    python scripts/scraping/test_bis_discovery_fetch.py
"""

import asyncio
import sys
import os

# Ensure project root is on the path so relative imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.scraping.bis_discovery import discover
from scripts.scraping.bis_fetcher import fetch_detail, save_html

SEARCH_TERM = "Ordinary Portland Cement"
OUTPUT_HTML = "data/processed/bis_test_fetch.html"


async def run_test():
    print(f"\n{'='*60}")
    print(f"BIS Discovery + Fetch Test")
    print(f"Search term: '{SEARCH_TERM}'")
    print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # Step 1: Discovery
    # ------------------------------------------------------------------
    print("Step 1: Discovery")
    print("-" * 40)
    results = await discover(
        search_term=SEARCH_TERM,
        config={
            "headless": True,
            "max_pages": 2,       # Limit to 2 pages for dev testing
            "render_wait_ms": 4000,
            "request_delay_ms": 2000,
        },
    )

    if not results:
        print("  [FAIL] No standards discovered. Check selectors or network.")
        return

    print(f"\n  Found {len(results)} standard(s):\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] Number : {r.number}")
        print(f"       Title  : {r.title}")
        print(f"       URL    : {r.detail_url}")
        print()

    # ------------------------------------------------------------------
    # Step 2: Fetch first discovered detail page
    # ------------------------------------------------------------------
    first = results[0]
    print("\nStep 2: Fetching detail page")
    print("-" * 40)
    print(f"  Target URL: {first.detail_url}\n")

    fetch_result = await fetch_detail(
        url=first.detail_url,
        config={
            "headless": True,
            "render_wait_ms": 5000,
            "retry_count": 2,
        },
    )

    print(f"\n  {'='*40}")
    print(f"  Fetch Result:")
    print(f"  Success     : {fetch_result['success']}")
    print(f"  Final URL   : {fetch_result['final_url']}")
    print(f"  HTML length : {fetch_result['html_length']:,} characters")
    if fetch_result['error']:
        print(f"  Error       : {fetch_result['error']}")

    # Save HTML for manual inspection
    if fetch_result['success']:
        os.makedirs("data/processed", exist_ok=True)
        save_html(fetch_result['html'], OUTPUT_HTML)
        print(f"\n  HTML saved to: {OUTPUT_HTML}")

    print(f"\n{'='*60}")
    print("Test complete.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(run_test())
