import json
import os
import subprocess
import sys
import ollama
from typing import List, Dict, Any
from app.tenders import get_tenders_for_standard
from app.matcher import find_similar_standards
from app.mongodb import standards_col

LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:4b")
MIN_RELEVANCE_SCORE = int(os.getenv("MIN_RELEVANCE_SCORE", "40"))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def _distance_to_score(distance: float) -> int:
    """Convert cosine distance [0, 2] to an applicability score [0, 100].

    cosine_distance = 0  → identical      → score 100
    cosine_distance = 1  → orthogonal     → score  0
    cosine_distance ≥ 1  → anti-correlated → score  0
    """
    if distance is None:
        return 0
    similarity = max(0.0, 1.0 - distance)   # cosine similarity in [0, 1]
    return int(round(similarity * 100))


def _extract_certification(std) -> str:
    """Pull certification info from the standard's details JSON, if present."""
    details = std.get('details') or {}
    # Check several keys the BIS parser may have stored
    for key in ("certification", "certification_info", "Certification",
                "certification_type", "cert_info"):
        val = details.get(key)
        if val:
            return val if isinstance(val, str) else json.dumps(val)

    # Sometimes embedded in title or scope text
    for text in (std.get('title') or "", std.get('scope') or ""):
        lower = text.lower()
        if "voluntary certification" in lower:
            return "Voluntary Certification"
        if "mandatory certification" in lower:
            return "Mandatory Certification"
        if "certification : n/a" in lower or "certification: n/a" in lower:
            return "N/A"

    return "Not specified"


def _trigger_bis_fallback(query: str) -> bool:
    """Triggers the bis pipeline to discover and upsert standards if DB misses."""
    print(f"Triggering BIS Live Discovery fallback for query: {query}")
    try:
        subprocess.run(
            [sys.executable, "-m", "scripts.scraping.bis_pipeline", "--query", query, "--max", "5"],
            cwd=PROJECT_ROOT,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Fallback failed: {e}")
        return False


def rank_and_format_standards(query: str, extracted_reqs: dict) -> List[Dict[str, Any]]:
    """
    Takes the user query and extracted requirements, retrieves candidate standards,
    and uses the LLM to rank and provide reasoning for the top recommendations.
    """
    # Create a dense search query string
    search_text = f"{query} " + " ".join(
        [v for k, v in extracted_reqs.items() if isinstance(v, str)]
    )

    # 1. Retrieve Candidate Standards (now includes distance)
    candidates = find_similar_standards(search_text, limit=6)

    # 2. Build distance-based baseline scores and find max score
    max_score = 0
    if candidates:
        for c in candidates:
            c["base_score"] = _distance_to_score(c["distance"])
            if c["base_score"] > max_score:
                max_score = c["base_score"]

    # 2a. Fallback if no candidates or max score is below threshold
    if not candidates:
        print(f"Max score {max_score} < threshold {MIN_RELEVANCE_SCORE}. Running fallback...")
        # Count documents before fallback
        count_before = standards_col.count_documents({})

        success = _trigger_bis_fallback(query)
        if success:
            count_after = standards_col.count_documents({})

            if count_after > count_before:
                candidates = find_similar_standards(search_text, limit=6)
                for c in candidates:
                    c["base_score"] = _distance_to_score(c["distance"])
            else:
                return [{
                    "standardNumber": "None",
                    "title": "No relevant Indian Standards found",
                    "applicabilityScore": 0,
                    "reasons": ["The database and BIS search returned no relevant results for your query."],
                    "certification": "N/A",
                    "scope": "N/A",
                    "evidence": {}
                }]
        else:
            return [{
                "standardNumber": "None",
                "title": "No relevant Indian Standards found",
                "applicabilityScore": 0,
                "reasons": ["The database and BIS search returned no relevant results for your query."],
                "certification": "N/A",
                "scope": "N/A",
                "evidence": {}
            }]

    if not candidates:
        return []

    # Ensure no duplicates
    unique_candidates = []
    seen = set()
    for c in candidates:
        std_id = c["standard"].get("standard_id")
        if std_id not in seen:
            seen.add(std_id)
            unique_candidates.append(c)
    candidates = unique_candidates

    formatted_results = []

    # 3. Try LLM-based re-ranking for reasons + refined scores
    candidate_summaries = []
    for i, c in enumerate(candidates):
        std = c["standard"]
        cert = _extract_certification(std)
        candidate_summaries.append(
            f"[{i}] {std.get('number')}: {std.get('title')} "
            f"(Scope: {std.get('scope') or 'N/A'}) "
            f"(Certification: {cert})"
        )

    prompt = f"""
You are an expert procurement and Indian Standards AI.
Given the user query and extracted requirements, evaluate the relevance of the following candidate standards.
Calculate an applicability score (0-100) for each. Provide a short reason why it is recommended.
Include certification information if mentioned.

Query: {query}
Requirements: {json.dumps(extracted_reqs)}

Candidates:
{chr(10).join(candidate_summaries)}

Respond strictly with a JSON array of objects. Each object MUST contain exactly:
- index (integer, matching the candidate index)
- applicabilityScore (integer 0-100)
- reasons (list of 2-3 short strings explaining why it applies)
"""

    try:
        response = ollama.chat(model=LLM_MODEL, messages=[
            {
                'role': 'system',
                'content': 'You are a ranking engine. Output strictly raw JSON array. No markdown, no explanation.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ], options={"temperature": 0.1})

        content = response.get('message', {}).get('content', '').strip()
        # Strip markdown fences
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        ranked_scores = json.loads(content.strip())

        # Sort by LLM score descending
        ranked_scores = sorted(
            ranked_scores,
            key=lambda x: x.get('applicabilityScore', 0),
            reverse=True,
        )

        for rank_data in ranked_scores:
            idx = rank_data.get('index')
            if idx is not None and 0 <= idx < len(candidates):
                std = candidates[idx]["standard"]
                formatted_results.append({
                    "standardNumber": std.get('number'),
                    "title": std.get('title'),
                    "applicabilityScore": rank_data.get('applicabilityScore', 0),
                    "reasons": rank_data.get('reasons', ["Matches search criteria."]),
                    "certification": _extract_certification(std),
                    "scope": std.get('scope'),
                    "evidence": std.get('details'),
                    "tenders": get_tenders_for_standard(std.get('number'))
                })

    except Exception as e:
        print(f"Warning: Ranking LLM failed ({LLM_MODEL}). Error: {e}")
        print("Falling back to distance-based scoring.")
        # Fallback: use real distance-based scores, NOT a hardcoded number
        for c in sorted(candidates, key=lambda x: x["base_score"], reverse=True):
            std = c["standard"]
            formatted_results.append({
                "standardNumber": std.get('number'),
                "title": std.get('title'),
                "applicabilityScore": c["base_score"],
                "reasons": [
                    f"Cosine similarity: {c['base_score']}% (LLM unavailable for detailed reasoning)"
                ],
                "certification": _extract_certification(std),
                "scope": std.get('scope'),
                "evidence": std.get('details'),
                "tenders": get_tenders_for_standard(std.get('number'))
            })

    return formatted_results
