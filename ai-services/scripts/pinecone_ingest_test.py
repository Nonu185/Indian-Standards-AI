import os
import sys

# Ensure project root is in PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from app import pinecone_service
from app.mongodb import standards_col

def main():
    # Fetch standards from MongoDB
    standards = list(standards_col.find())
    print(f"MongoDB standards read = {len(standards)}")
    if not standards:
        print("No standards found, exiting.")
        return
    # Test embedding dimension
    try:
        sample_emb = pinecone_service._embed_text("sample text for dimension test")
        print(f"Embedding dimension = {len(sample_emb)}")
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return
    # Upsert standards into Pinecone
    try:
        pinecone_service.upsert_standards(standards)
        print("Upsert into Pinecone completed.")
    except Exception as e:
        print(f"Upsert failed: {e}")
        return
    # Perform semantic searches
    queries = [
        "Ordinary Portland Cement Grade 43",
        "Industrial safety helmet for electrical work"
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        try:
            results = pinecone_service.query_embeddings(q, top_k=5)
            for r in results:
                meta = r.get('metadata', {})
                print(f"- {meta.get('number')} | {meta.get('title')} | score: {r.get('score'):.4f}")
        except Exception as e:
            print(f"Search failed: {e}")

if __name__ == "__main__":
    main()
