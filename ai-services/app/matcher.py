import os
import ollama
from app.mongodb import standards_col

LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:8b")

def find_similar_standards(text_query: str, limit: int = 6) -> list:
    """Find similar standards using Pinecone semantic search.
    Returns a list of dicts with keys:
        - standard: full MongoDB document
        - distance: converted from Pinecone cosine similarity to a distance metric (1 - score)
    """
    from app.pinecone_service import query_embeddings, fetch_standards_by_ids

    print(f"[DEBUG] Querying Pinecone for: {text_query}")
    # Retrieve matches from Pinecone (includes id and score)
    matches = query_embeddings(text_query, top_k=limit)
    print(f"[DEBUG] Pinecone returned {len(matches)} candidates")
    if not matches:
        return []
    ids = [m['id'] for m in matches]
    # Fetch full standard docs from MongoDB
    standards = fetch_standards_by_ids(ids)
    # Combine results, converting score to distance (distance = 1 - score)
    candidates = []
    for match, std in zip(matches, standards):
        score = match.get('score', 0.0)
        distance = 1.0 - score  # convert cosine similarity to distance
        candidates.append({
            'standard': std,
            'distance': distance,
            'pinecone_score': score,
        })
    print(f"[DEBUG] Prepared {len(candidates)} candidate standards with distances")
    return candidates
