import os
import json
from typing import List, Dict

# Cache loaded tenders to avoid re-reading files on each request
_TENDERS_CACHE: List[Dict] = []

def _load_tenders() -> List[Dict]:
    """Load all tenders from raw JSON files in the repository.
    Returns a list of tender dicts with relevant fields flattened.
    """
    global _TENDERS_CACHE
    if _TENDERS_CACHE:
        return _TENDERS_CACHE
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
    tenders: List[Dict] = []
    for fname in os.listdir(raw_dir):
        if not fname.lower().endswith('.json'):
            continue
        fpath = os.path.join(raw_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        # Expect a top-level "tenders" array
        for t in data.get('tenders', []):
            tender_entry = {
                'title': t.get('title', ''),
                'organization': t.get('buyer', {}).get('organization', ''),
                'location': t.get('location', ''),
                'closing_date': t.get('publication_date', ''),
                'tender_url': t.get('source', {}).get('document_name', ''),
                'referenced_standards': [ref.get('standard_number') for ref in t.get('referenced_standards', [])]
            }
            tenders.append(tender_entry)
    _TENDERS_CACHE = tenders
    return tenders

def get_tenders_for_standard(standard_number: str) -> List[Dict]:
    """Return a list of tenders that reference the given standard number.
    The standard_number should match the "number" field of a Standard (e.g., "IS 2925:1984").
    """
    all_tenders = _load_tenders()
    matched = []
    for t in all_tenders:
        if standard_number in t.get('referenced_standards', []):
            t_copy = {k: v for k, v in t.items() if k != 'referenced_standards'}
            matched.append(t_copy)
    return matched
