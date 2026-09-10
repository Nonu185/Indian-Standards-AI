import os
import pathlib
import sys
from typing import List, Dict, Any

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env (reuse logic from other modules)
env_path_local = pathlib.Path(__file__).resolve().parents[2] / '.env'
env_path_root = pathlib.Path(__file__).resolve().parents[3] / '.env'
for env_path in (env_path_local, env_path_root):
    if env_path.is_file():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, _, v = line.partition('=')
                    os.environ.setdefault(k, v)
        break

from app.pinecone_service import (
    PINECONE_INDEX_NAME,
    PINECONE_API_KEY,
    EXPECTED_DIMENSION,
    upsert_standards,
    query_embeddings,
    _embed_text,
    build_enriched_text  # will be added to service
)
from app.mongodb import standards_col
from pinecone import Pinecone

def fetch_standards() -> List[Dict[str, Any]]:
    return list(standards_col.find())

def enrich_and_upsert():
    standards = fetch_standards()
    print(f"Found {len(standards)} standards in MongoDB.")
    # Use the service's upsert function which now builds enriched text internally.
    upsert_standards(standards)
    print("Upsert completed.")

def verify_queries():
    queries = [
        "I need Ordinary Portland Cement Grade 43 for a government construction project.",
        "I need an industrial safety helmet for electrical work."
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        results = query_embeddings(q, top_k=20)
        for i, res in enumerate(results[:10], start=1):
            meta = res.get('metadata', {})
            std_num = meta.get('number') or meta.get('standard_id')
            title = meta.get('title')
            score = res.get('score')
            print(f"{i}. {std_num} | {title} | score={score:.4f}")
        # Check presence of expected standards
        expected = "IS 269:2015" if "Cement" in q else "IS 2925:1984"
        found = any(expected in (r.get('metadata', {}).get('number') or "") for r in results[:20])
        print(f"Expected {expected} {'FOUND' if found else 'NOT FOUND'} in top 20.")
        if not found:
            # Detailed diagnostics
            print("--- Diagnostics ---")
            # Show enriched text for the missing standard
            missing_std = next((s for s in fetch_standards() if s.get('number') == expected), None)
            if missing_std:
                enriched = build_enriched_text(missing_std)
                print("Enriched text for missing standard:\n", enriched)
            # Show dimensions
            query_vec = _embed_text(q)
            print(f"Query vector dimension: {len(query_vec)}")
            print(f"Pinecone index dimension (expected): {EXPECTED_DIMENSION}")
            # List all IDs returned
            ids = [r.get('id') for r in results]
            print("Returned IDs:", ids)

def main():
    enrich_and_upsert()
    verify_queries()

if __name__ == "__main__":
    main()
