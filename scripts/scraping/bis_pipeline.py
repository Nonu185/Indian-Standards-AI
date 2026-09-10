"""
bis_pipeline.py — BIS End-to-End Ingestion Pipeline

Chains:
  1. bis_discovery  — find standard detail URLs via Playwright
  2. bis_fetcher    — render each detail page and return HTML
  3. bis_parser     — extract structured fields from HTML
  4. bis_normalizer — map to the `standards` table schema
  5. ingest         — upsert into PostgreSQL (no embeddings)

Usage:
    python -m scripts.scraping.bis_pipeline --query "Portland Cement" --max 5
    python -m scripts.scraping.bis_pipeline --query "Safety Helmet" --max 10 --dry-run
"""

import asyncio
import logging
import os
import sys
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ai-services"))

from scripts.scraping.bis_discovery import discover
from scripts.scraping.bis_fetcher import fetch_detail
from scripts.scraping.bis_parser import parse_html
from scripts.scraping.bis_normalizer import normalize, ValidationError
from app.database import SessionLocal, Standard, init_db
from sqlalchemy.dialects.postgresql import insert as pg_insert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bis.pipeline")


def db_upsert(session, record: dict) -> str:
    """Upsert a normalized record. Returns 'inserted' or 'updated'."""
    existing = (
        session.query(Standard)
        .filter(Standard.standard_id == record["standard_id"])
        .first()
    )
    action = "updated" if existing else "inserted"

    stmt = pg_insert(Standard).values(
        standard_id=record["standard_id"],
        number=record.get("number") or "",
        title=record.get("title") or "",
        authority=record.get("authority") or "",
        revision=record.get("revision") or "",
        publication_date=record.get("publication_date") or "",
        status=record.get("status") or "",
        scope=record.get("scope") or "",
        details=record.get("details") or {},
        embedding=None,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["standard_id"],
        set_={
            "number": stmt.excluded.number,
            "title": stmt.excluded.title,
            "authority": stmt.excluded.authority,
            "revision": stmt.excluded.revision,
            "publication_date": stmt.excluded.publication_date,
            "status": stmt.excluded.status,
            "scope": stmt.excluded.scope,
            "details": stmt.excluded.details,
            # embedding intentionally omitted — preserve existing
        },
    )
    session.execute(stmt)
    return action


async def run_pipeline(query: str, max_standards: int, dry_run: bool = False):
    counters = {
        "discovered": 0, "fetched_ok": 0, "parsed_ok": 0,
        "inserted": 0, "updated": 0, "skipped": 0, "errors": 0,
    }
    errors = []

    log.info(f"[1/5] Discovering standards for: '{query}' (max={max_standards})")
    discovered = await discover(query, config={"max_pages": 2, "headless": True})
    discovered = discovered[:max_standards]
    counters["discovered"] = len(discovered)
    log.info(f"      Discovered {len(discovered)} standard(s).")

    if not discovered:
        log.warning("No standards discovered. Exiting.")
        return counters, errors, None, []

    if not dry_run:
        init_db()
        session = SessionLocal()

    results = []

    for i, std_ref in enumerate(discovered, 1):
        log.info(f"[{i}/{len(discovered)}] Processing: {std_ref.number}")

        try:
            fetch_result = await fetch_detail(std_ref.detail_url, config={"headless": True})
        except Exception as e:
            msg = f"Fetch error for {std_ref.number}: {e}"
            log.error(msg); errors.append(msg); counters["errors"] += 1
            continue

        if not fetch_result["success"] or not fetch_result["html"]:
            msg = f"Fetch failed for {std_ref.number}: {fetch_result.get('error')}"
            log.warning(msg); errors.append(msg); counters["errors"] += 1
            continue

        counters["fetched_ok"] += 1

        try:
            parsed = parse_html(fetch_result["html"], source_url=fetch_result["final_url"])
        except Exception as e:
            msg = f"Parse error for {std_ref.number}: {e}"
            log.error(msg); errors.append(msg); counters["errors"] += 1
            continue

        if not parsed.get("number"):
            parsed["number"] = std_ref.number
        if not parsed.get("title"):
            parsed["title"] = std_ref.title

        counters["parsed_ok"] += 1

        try:
            normalized = normalize(parsed)
        except ValidationError as e:
            msg = f"Validation error for {std_ref.number}: {e}"
            log.warning(msg); errors.append(msg); counters["skipped"] += 1
            continue

        results.append(normalized)
        log.info(f"      Normalized → {normalized['standard_id']}")

        if dry_run:
            log.info(f"      [DRY-RUN] Would upsert: {normalized['standard_id']}")
            counters["inserted"] += 1
        else:
            try:
                action = db_upsert(session, normalized)
                session.commit()
                counters[action] += 1
                log.info(f"      DB {action}: {normalized['standard_id']}")
            except Exception as e:
                msg = f"DB error for {std_ref.number}: {e}"
                log.error(msg); errors.append(msg)
                session.rollback(); counters["errors"] += 1

    if not dry_run:
        total_in_db = session.query(Standard).count()
        session.close()
    else:
        total_in_db = None

    return counters, errors, total_in_db, results


def main():
    parser = argparse.ArgumentParser(description="BIS End-to-End Ingestion Pipeline")
    parser.add_argument("--query", default="Portland Cement")
    parser.add_argument("--max", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    counters, errors, total_in_db, results = asyncio.run(
        run_pipeline(args.query, args.max, dry_run=args.dry_run)
    )

    print("\n" + "=" * 60)
    print("BIS PIPELINE RUN SUMMARY")
    print("=" * 60)
    print(f"  Query            : {args.query}")
    print(f"  Discovered       : {counters['discovered']}")
    print(f"  Fetched OK       : {counters['fetched_ok']}")
    print(f"  Parsed OK        : {counters['parsed_ok']}")
    print(f"  Inserted (new)   : {counters['inserted']}")
    print(f"  Updated (dupes)  : {counters['updated']}")
    print(f"  Skipped/invalid  : {counters['skipped']}")
    print(f"  Errors           : {counters['errors']}")
    if total_in_db is not None:
        print(f"  Total in DB now  : {total_in_db}")
    if errors:
        print("\nErrors/warnings:")
        for e in errors:
            print(f"  * {e}")
    if results:
        print("\nNormalized records:")
        for r in results:
            print(f"  [{r['standard_id']}] {r['title']} | status={r['status']} | pub={r['publication_date']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
