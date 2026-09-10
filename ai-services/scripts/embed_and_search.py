import os
import sys
import json
import ollama
from sqlalchemy import select

# Add ai-services to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, Standard

def get_embedding(text):
    text = text[:4000]
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response.get('embedding')

def embed_null_records(session):
    records = session.query(Standard).filter(Standard.embedding == None).all()
    count = 0
    for record in records:
        text_parts = []
        if record.title:
            text_parts.append(record.title)
        if record.scope:
            text_parts.append(record.scope)
        if record.details:
            text_parts.append(json.dumps(record.details))
            
        text = " ".join(text_parts)
        if not text.strip():
            continue
            
        try:
            emb = get_embedding(text)
            if emb:
                record.embedding = emb
                count += 1
        except Exception as e:
            print(f"Failed to embed record {record.standard_id}: {e}")
            
    session.commit()
    return count

def semantic_search(session, query, limit=5):
    query_emb = get_embedding(query)
    if not query_emb:
        print("Failed to get query embedding.")
        return []
        
    print(f"\nQuery: '{query}'")
    
    results = session.query(Standard, Standard.embedding.l2_distance(query_emb).label('distance')).order_by('distance').limit(limit).all()
    
    print("\n--- Top 5 Results ---")
    for i, res in enumerate(results):
        record, distance = res
        print(f"{i+1}. [{record.standard_id}] {record.title} | L2 Distance: {distance:.4f}")
    
    return results

if __name__ == "__main__":
    session = SessionLocal()
    try:
        embedded_count = embed_null_records(session)
        print(f"Embedded count: {embedded_count}")
        query = "Which Indian Standard applies to Ordinary Portland Cement Grade 43?"
        semantic_search(session, query)
    except Exception as e:
        print(f"Error/Blockers: {e}")
    finally:
        session.close()
