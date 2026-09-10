import os
import pathlib
import sys
# Ensure the ai-services root is in PYTHONPATH for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Any

# Load .env (same logic as other modules)
env_path_local = pathlib.Path(__file__).resolve().parents[2] / '.env'
env_path_root = pathlib.Path(__file__).resolve().parents[3] / '.env'
for env_path in (env_path_local, env_path_root):
    if env_path.is_file():
        with open(env_path) as env_file:
            for line in env_file:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key, value)
        break

# Ensure required env vars
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
if not PINECONE_API_KEY:
    raise RuntimeError('PINECONE_API_KEY not set')

# Load Pinecone service module to reuse configs and functions
from app.pinecone_service import (
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EXPECTED_DIMENSION,
    upsert_standards,
    query_embeddings,
)

# Initialize Pinecone client (same as in service)
from pinecone import Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

print('--- Pinecone Configuration ---')
print(f'Index name (from env or default): {PINECONE_INDEX_NAME}')
print(f'Expected dimension: {EXPECTED_DIMENSION}')
print(f'Cloud: {PINECONE_CLOUD}')
print(f'Region: {PINECONE_REGION}')

# List all indexes and their vector counts
print('\n--- Existing Indexes ---')
indexes = pc.list_indexes().names()
if not indexes:
    print('No indexes found.')
else:
    for idx_name in indexes:
        try:
            idx = pc.Index(idx_name)
            stats = idx.describe_index_stats()
            total_vectors = getattr(stats, 'total_vector_count', stats.get('total_vector_count'))
        except Exception as e:
            total_vectors = f'Error: {e}'
        print(f'- {idx_name}: {total_vectors} vectors')

# Check record counts for specific indexes
for target in ['ai', 'standards-index']:
    try:
        idx = pc.Index(target)
        stats = idx.describe_index_stats()
        count = getattr(stats, 'total_vector_count', stats.get('total_vector_count'))
        print(f'Index "{target}" vector count: {count}')
    except Exception as e:
        print(f'Could not get stats for index "{target}": {e}')

# Determine which index pinecone_service uses (already printed above as PINECONE_INDEX_NAME)
# Verify standards upserted
from app.mongodb import standards_col
standards_in_db = list(standards_col.find())
print(f'\nStandards in MongoDB: {len(standards_in_db)} documents')

# Get vector count for the service index
service_idx = pc.Index(PINECONE_INDEX_NAME)
service_stats = service_idx.describe_index_stats()
service_vector_count = getattr(service_stats, 'total_vector_count', service_stats.get('total_vector_count'))
print(f'Vector count in service index "{PINECONE_INDEX_NAME}": {service_vector_count}')

# If the service index exists but has 0 vectors, perform ingestion once
if service_vector_count == 0:
    print('\n--- Performing one‑time ingestion of standards into Pinecone ---')
    upsert_standards(standards_in_db)
    # Re‑fetch stats
    service_idx = pc.Index(PINECONE_INDEX_NAME)
    service_stats = service_idx.describe_index_stats()
    service_vector_count = getattr(service_stats, 'total_vector_count', service_stats.get('total_vector_count'))
    print(f'Post‑ingestion vector count: {service_vector_count}')
else:
    print('\nNo ingestion needed; index already has vectors.')

# Helper to run a query and print top matches


# Execute required queries
queries = [
    "I need Ordinary Portland Cement Grade 43 for a government construction project.",
    "I need an industrial safety helmet for electrical work."
]
for q in queries:
    run_query(q)

print('\n--- Script completed ---')
