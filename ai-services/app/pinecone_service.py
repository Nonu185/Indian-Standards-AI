import os
from typing import List, Dict, Any
import ollama
import pathlib

# Load .env if present (similar to mongodb)
env_path_local = pathlib.Path(__file__).resolve().parent.parent / '.env'
env_path_root = pathlib.Path(__file__).resolve().parents[2] / '.env'
for env_path in (env_path_local, env_path_root):
    if env_path.is_file():
        with open(env_path) as env_file:
            for line in env_file:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key, value)
        break

# Pinecone client initialization
from pinecone import Pinecone, ServerlessSpec

# Fixed cloud and region per user request
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_CLOUD = 'aws'
PINECONE_REGION = 'us-east-1'
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'standards-index')

if not PINECONE_API_KEY:
    raise RuntimeError('PINECONE_API_KEY not set in environment')

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Ensure index exists (creation is idempotent)
EXPECTED_DIMENSION = int(os.getenv('PINECONE_DIMENSION', '768'))

if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EXPECTED_DIMENSION,
        metric='cosine',
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
    )

index = pc.Index(PINECONE_INDEX_NAME)

def _embed_text(text: str) -> List[float]:
    """Generate a nomic-embed-text embedding using Ollama.
    Returns a list of floats of length EXPECTED_DIMENSION.
    """
    model_name = os.getenv('EMBEDDING_MODEL', 'nomic-embed-text')
    try:
        resp = ollama.embeddings(model=model_name, prompt=text)
        embedding = resp.get('embedding')
        if not embedding:
            raise ValueError('No embedding returned')
        return embedding
    except Exception as e:
        raise RuntimeError(f"Embedding failed: {e}")


def build_enriched_text(std: dict) -> str:
    """Construct a rich multi‑line text for a standard.
    Includes standard number, title, product/category, scope, details, requirements,
    grade/material/application, and referenced/test standards when available.
    """
    parts = []
    number = std.get('number') or std.get('standard_id') or ''
    title = std.get('title') or ''
    parts.append(f"Standard Number: {number}")
    parts.append(f"Title: {title}")
    # Product/category if present
    product = std.get('product') or {}
    product_name = product.get('product_name') or product.get('product_category') or ''
    if product_name:
        parts.append(f"Product/Category: {product_name}")
    # Scope
    scope = std.get('scope') or ''
    if scope:
        parts.append(f"Scope: {scope}")
    # Details / description
    details = std.get('details') or std.get('description') or ''
    if details:
        parts.append(f"Details: {details}")
    # Requirements list
    reqs = std.get('requirements') or []
    if reqs:
        req_strs = []
        for r in reqs:
            param = r.get('parameter', '')
            value = r.get('value', '')
            unit = r.get('unit', '')
            req_strs.append(f"{param} {value}{unit}".strip())
        parts.append("Requirements: " + ", ".join(req_strs))
    # References / test standards
    refs = std.get('references') or []
    if refs:
        ref_nums = [ref.get('standard_number') for ref in refs if ref.get('standard_number')]
        if ref_nums:
            parts.append("Referenced/Test Standards: " + ", ".join(ref_nums))
    return "\n".join(parts)
def upsert_standards(standards: List[Dict[str, Any]]) -> None:
    """Upsert a batch of standards into Pinecone.
    Each standard dict must contain a unique identifier under the key 'standard_id' (or 'number').
    The whole document is stored as metadata (filtered to JSON‑serializable values).
    """
    vectors = []
    for std in standards:
        # Use MongoDB _id if present, otherwise fallback to standard number
        std_id = str(std.get('_id') or std.get('number'))
        # Prepare a textual representation for embedding – title + scope + description
        text = build_enriched_text(std)
        embedding = _embed_text(text)
        # Pinecone metadata must be JSON‑serializable and limited in size
        metadata = {
            'standard_id': std_id,
            'number': std.get('number'),
            'title': std.get('title'),
            'scope': std.get('scope')
        }
        vectors.append((std_id, embedding, metadata))
    if vectors:
        index.upsert(vectors=vectors)

def query_embeddings(query: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """Query Pinecone with a text query and return the top_k matches.
    Returns a list of dicts containing 'id' and 'score' (cosine similarity).
    """
    query_emb = _embed_text(query)
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    matches = []
    for match in results.matches:
        matches.append({
            'id': match.id,
            'score': match.score,
            'metadata': match.metadata
        })
    return matches

def fetch_standards_by_ids(ids: List[str]) -> List[Dict[str, Any]]:
    """Retrieve full standard documents from MongoDB given a list of ids.
    This function expects the MongoDB client defined in app.mongodb.
    """
    from app.mongodb import standards_col
    from bson import ObjectId
    object_ids = []
    for i in ids:
        try:
            object_ids.append(ObjectId(i))
        except Exception:
            object_ids.append(i)
    cursor = standards_col.find({"_id": {"$in": object_ids}})
    return list(cursor)
