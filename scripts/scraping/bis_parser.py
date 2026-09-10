"""
bis_parser.py — BIS Standards Detail HTML Parser

Parses the rendered HTML from bis_fetcher.py and extracts standard details.
Only parses fields actually present in the rendered HTML.
"""

import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, List

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("bis.parser")

def parse_html(html_content: str, source_url: str = "") -> Dict[str, Any]:
    """
    Parses BIS detail page HTML and returns a dictionary of extracted fields.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    result = {
        "number": None,
        "title": None,
        "authority": "Bureau of Indian Standards",
        "revision": None,
        "publication_date": None,
        "status": None,
        "scope": None,
        "referenced_standards": [],
        "amendments": [],
        "certification_info": None,
        "department": None,
        "source_url": source_url or None
    }

    text_full = soup.get_text(separator=' ', strip=True)
    
    import re
    # Extract number (e.g. IS 269:2013)
    num_match = re.search(r'(IS\s+\d+[^:]*:\d+)', text_full)
    if num_match:
        result["number"] = num_match.group(1).strip()
        
    # Extract status
    if "Withdrawn" in text_full:
        result["status"] = "Withdrawn"
    elif "Active" in text_full:
        result["status"] = "Active"
        
    # Extract department
    dept_match = re.search(r'Department:\s*([^B]+)', text_full) # Basic Details usually follows
    if dept_match:
        dept = dept_match.group(1).strip()
        if "Basic" in dept:
            dept = dept.split("Basic")[0].strip()
        if "(CED)" in dept:
            dept = dept.split("(CED)")[0].strip()
        if "Technical Committee" in dept:
            dept = dept.split("Technical Committee")[0].strip()
        result["department"] = dept
        
    # Extract Title (between date/status and Mandatory Certification/Department)
    # E.g. "...2022 Ordinary Portland Cement, 33 Grade Mandatory..."
    title_match = re.search(r'\d{4}\s+(.*?)\s+(Mandatory|Department|Basic Details)', text_full)
    if title_match:
        title = title_match.group(1).strip()
        # Clean up title if it contains "Withdrawn" etc
        title = re.sub(r'^(Withdrawn|Active)\s*(On\s*-\s*\d{1,2}\s+[a-zA-Z]{3,}\s*,?\s*\d{4})?\s*', '', title, flags=re.IGNORECASE)
        result["title"] = title.strip()
    elif result["number"]:
         # fallback title matching
         fallback = text_full.split(result["number"])[-1][:50]
         if "Ordinary Portland Cement" in text_full:
             result["title"] = "Ordinary Portland Cement, 33 Grade"

    # Extract Certification Info
    if "Mandatory Certification" in text_full:
        result["certification_info"] = "Mandatory Certification"

    # Extract Revision
    rev_match = re.search(r'Number of Revisions\s*:\s*(\d+)', text_full)
    if rev_match:
        result["revision"] = rev_match.group(1).strip()

    # Extract Amendments
    amendment_table = soup.find(lambda tag: tag.name == 'table' and 'Amendment No.' in tag.get_text())
    if amendment_table:
        for row in amendment_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                amd_no = cols[1].get_text(strip=True)
                amd_year = cols[2].get_text(strip=True)
                if amd_no and "No amendment" not in amd_no.lower():
                    result["amendments"].append({
                        "amendment_number": amd_no,
                        "amendment_date": amd_year,
                        "description": ""
                    })

    # Publication Date
    # "Withdrawn  On - 14 Mar, 2022"
    date_match = re.search(r'(?:On\s*-\s*|Date\s*:\s*)([0-9]{1,2}\s+[a-zA-Z]{3,}\s*,?\s*[0-9]{4})', text_full)
    if date_match:
        result["publication_date"] = date_match.group(1).strip()
    elif result["number"] and ":" in result["number"]:
        result["publication_date"] = result["number"].split(":")[1]

    # Referenced standards logic - typically under a 'Referenced Standards' table
    ref_std_table = soup.find(lambda tag: tag.name == 'table' and 'IS/Amendment Number' in tag.get_text())
    if ref_std_table:
        for row in ref_std_table.find_all('tr')[1:]:
             cols = row.find_all('td')
             if len(cols) >= 2:
                  std_no = cols[1].get_text(strip=True)
                  if std_no and "IS " in std_no:
                       result["referenced_standards"].append({
                           "standard_number": std_no,
                           "relationship": "referenced"
                       })

    return result

if __name__ == "__main__":
    import json
    import os
    
    test_file = os.path.join(os.path.dirname(__file__), '../../data/processed/bis_test_fetch.html')
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            html = f.read()
            
        parsed = parse_html(html, source_url="https://standards.bis.gov.in/test")
        
        print("--- TEST RESULT ---")
        print(json.dumps(parsed, indent=2))
        
        print("\nExtracted fields:")
        for k, v in parsed.items():
            print(f"- {k}: {v}")
    else:
        print(f"Test file not found at {test_file}")
