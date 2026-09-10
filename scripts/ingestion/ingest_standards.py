import sys
import os
import json
import glob

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai-services')))

from app.database import SessionLocal, init_db, Standard
from sqlalchemy.dialects.postgresql import insert
import ollama

def get_embedding(text):
    try:
        response = ollama.embeddings(model=os.getenv("EMBEDDING_MODEL", "nomic-embed-text"), prompt=text)
        return response.get('embedding')
    except Exception as e:
        print(f"Warning: Failed to get embedding. (Ollama may not be running). Error: {e}")
        return None

def upsert_standard(session, std, generate_embeddings=True):
    # Deduplicate based on standard_id
    standard_id = std.get("standard_id")
    if not standard_id:
        return False
        
    details = std.get("details", std.copy())
    # Remove top-level fields that are stored in specific columns
    for key in ['standard_id', 'number', 'title', 'authority', 'revision', 'publication_date', 'status', 'scope', 'details']:
        if key in details and std.get('details') is None:
            details.pop(key, None)
    
    # Generate embedding
    embedding = None
    if generate_embeddings:
        text_to_embed = f"{std.get('title', '')} {std.get('scope', '')}"
        embedding = get_embedding(text_to_embed)
    
    # Upsert query
    stmt = insert(Standard).values(
        standard_id=standard_id,
        number=std.get("number", ""),
        title=std.get("title", ""),
        authority=std.get("authority", ""),
        revision=std.get("revision", ""),
        publication_date=std.get("publication_date", ""),
        status=std.get("status", ""),
        scope=std.get("scope", ""),
        details=details,
        embedding=embedding
    )
    
    update_set = {
        'number': stmt.excluded.number,
        'title': stmt.excluded.title,
        'authority': stmt.excluded.authority,
        'revision': stmt.excluded.revision,
        'publication_date': stmt.excluded.publication_date,
        'status': stmt.excluded.status,
        'scope': stmt.excluded.scope,
        'details': stmt.excluded.details,
    }
    if generate_embeddings:
        update_set['embedding'] = stmt.excluded.embedding

    stmt = stmt.on_conflict_do_update(
        index_elements=['standard_id'],
        set_=update_set
    )
    
    session.execute(stmt)
    return True

def ingest_data(data_dir):
    print(f"Initializing database and running migrations...")
    init_db()
    
    session = SessionLocal()
    files = glob.glob(os.path.join(data_dir, "*.json"))
    
    total_datasets = 0
    total_standards = 0
    total_requirements = 0
    total_references = 0
    
    for file_path in files:
        print(f"Processing {os.path.basename(file_path)}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            standards = data.get('standards', [])
            if not standards:
                print(f"  No 'standards' array found in {os.path.basename(file_path)}. Skipping.")
                continue
                
            total_datasets += 1
            added_in_file = 0
            
            for std in standards:
                reqs = std.get('requirements', [])
                refs = std.get('referenced_standards', [])
                total_requirements += len(reqs)
                total_references += len(refs)

                if upsert_standard(session, std, generate_embeddings=True):
                    added_in_file += 1
                    total_standards += 1
                
            session.commit()
            print(f"  Successfully imported {added_in_file} standards from {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")
            session.rollback()
            
    print("\n--- Ingestion Summary ---")
    print(f"Datasets processed: {total_datasets}")
    print(f"Total Unique Standards: {total_standards}")
    print(f"Total Requirements Extracted: {total_requirements}")
    print(f"Total References Extracted: {total_references}")
    
    session.close()

def test_bis_ingestion():
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from scripts.scraping.bis_parser import parse_html
    from scripts.scraping.bis_normalizer import normalize

    print(f"Initializing database and running migrations for test...")
    init_db()
    session = SessionLocal()

    test_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/processed/bis_test_fetch.html'))
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return

    with open(test_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    parsed = parse_html(html, source_url="https://standards.bis.gov.in/test")
    normalized_data = normalize(parsed)

    try:
        success = upsert_standard(session, normalized_data, generate_embeddings=False)
        session.commit()
        if success:
            print(f"Test ingestion successful for standard_id: {normalized_data['standard_id']}")
    except Exception as e:
        print(f"Error in test ingestion: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-bis":
        test_bis_ingestion()
    else:
        raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/raw'))
        ingest_data(raw_dir)
