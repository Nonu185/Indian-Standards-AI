"""
bis_normalizer.py — BIS Standards Normalizer

Normalizes the parsed output from bis_parser.py into the 
database schema structure defined in ai-services/app/database.py.
"""

import logging
import re
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bis.normalizer")


class ValidationError(Exception):
    """Exception raised for validation errors during normalization."""
    pass


def generate_standard_id(number: str) -> str:
    """
    Generate a stable standard_id from the IS number.
    e.g., 'IS 269:2013' -> 'IS_269_2013'
    """
    if not number:
        return ""
    # Replace spaces, colons, and hyphens with underscores
    clean_id = re.sub(r'[\s:.-]+', '_', number.strip())
    # Remove any non-alphanumeric characters except underscore
    clean_id = re.sub(r'[^A-Za-z0-9_]', '', clean_id)
    return clean_id.upper()


def normalize(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize parser output into the Standard database structure.
    
    Database structure (from ai-services/app/database.py):
    - standard_id (String)
    - number (String)
    - title (Text)
    - authority (String)
    - revision (String)
    - publication_date (String)
    - status (String)
    - scope (Text)
    - details (JSON) -> contains requirements, references, amendments, etc.
    """
    # 1. Generate stable standard_id
    number = parsed_data.get("number")
    if not number:
        raise ValidationError("Required field 'number' is missing or empty.")
    
    standard_id = generate_standard_id(number)
    if not standard_id:
        raise ValidationError(f"Could not generate a valid standard_id from '{number}'.")

    title = parsed_data.get("title")
    if not title:
        raise ValidationError("Required field 'title' is missing or empty.")

    # 2. Extract top-level fields
    normalized = {
        "standard_id": standard_id,
        "number": number.strip(),
        "title": title.strip(),
        "authority": parsed_data.get("authority") or "Bureau of Indian Standards",
        "revision": parsed_data.get("revision") or None,
        "publication_date": parsed_data.get("publication_date") or None,
        "status": parsed_data.get("status") or None,
        "scope": parsed_data.get("scope") or None,
        "details": {}
    }

    # 3. Put remaining fields into `details`
    details_keys = [
        "referenced_standards", 
        "amendments", 
        "certification_info", 
        "department", 
        "source_url",
        "requirements" # Although parser doesn't currently output this, prepare for it
    ]

    for key in details_keys:
        val = parsed_data.get(key)
        # Preserve lists as empty [], but dicts/strings as None if missing/falsy
        if val is not None:
            normalized["details"][key] = val
        elif key in ["referenced_standards", "amendments", "requirements"]:
            normalized["details"][key] = []
        else:
            normalized["details"][key] = None

    return normalized


if __name__ == "__main__":
    import json
    import os
    import sys
    
    # We will test using the output of the bis_parser
    try:
        from scripts.scraping.bis_parser import parse_html
    except ImportError:
        # allow running directly if PYTHONPATH is not set
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
        from scripts.scraping.bis_parser import parse_html

    test_file = os.path.join(os.path.dirname(__file__), '../../data/processed/bis_test_fetch.html')
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            html = f.read()
            
        parsed = parse_html(html, source_url="https://standards.bis.gov.in/test")
        
        try:
            normalized_data = normalize(parsed)
            print("--- NORMALIZED OUTPUT ---")
            print(json.dumps(normalized_data, indent=2))
        except ValidationError as e:
            print(f"Validation Error: {e}")
    else:
        print(f"Test file not found at {test_file}")
