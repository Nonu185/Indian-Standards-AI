import os
import json
from typing import List, Dict
from pymongo import MongoClient

# Load .env file from project root (if present)
import pathlib
# Try loading .env from ai-services directory first
env_path_local = pathlib.Path(__file__).resolve().parent.parent / '.env'
# Fallback to project root .env (two levels up from this file)
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


# MongoDB connection settings (environment variables or defaults)
MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    raise RuntimeError('MONGO_URI environment variable not set. Provide MongoDB Atlas connection string in .env')
DB_NAME = os.getenv('MONGO_DB_NAME', 'indian_standards_ai')

client = MongoClient(MONGO_URI)

# Verify connection (ping)
try:
    client.admin.command('ping')
    print('MongoDB Atlas connection successful.')
except Exception as e:
    print('MongoDB Atlas connection failed:', e)
    raise

db = client[DB_NAME]

# Collections
products_col = db['products']
components_col = db['components']
standards_col = db['standards']
requirements_col = db['requirements']
references_col = db['references']
amendments_col = db['amendments']
tenders_col = db['tenders']
tender_refs_col = db['tender_referenced_standards']
compliance_col = db['compliance_metadata']

def ingest_json_file(filepath: str):
    """Ingest a single JSON file into MongoDB, preserving structure.
    The file is expected to contain top‑level keys: product, components, standards, tenders.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Insert product document (excluding nested arrays that will be stored separately)
    product_doc = data.get('product', {})
    product_id = products_col.insert_one(product_doc).inserted_id

    # Components – store with reference to product
    components = data.get('components', [])
    for comp in components:
        comp_doc = comp.copy()
        comp_doc['product_id'] = product_id
        components_col.insert_one(comp_doc)

    # Standards – each may contain requirements, references, amendments
    standards = data.get('standards', [])
    for std in standards:
        std_doc = std.copy()
        std_doc['product_id'] = product_id
        # Remove nested arrays before inserting into standards collection
        reqs = std_doc.pop('requirements', [])
        refs = std_doc.pop('references', [])
        amends = std_doc.pop('amendments', [])
        std_id = standards_col.insert_one(std_doc).inserted_id

        # Insert nested requirements, referencing the standard
        for req in reqs:
            req_doc = req.copy()
            req_doc['standard_id'] = std_id
            requirements_col.insert_one(req_doc)

        # Insert references
        for ref in refs:
            ref_doc = ref.copy()
            ref_doc['standard_id'] = std_id
            references_col.insert_one(ref_doc)

        # Insert amendments
        for amend in amends:
            amend_doc = amend.copy()
            amend_doc['standard_id'] = std_id
            amendments_col.insert_one(amend_doc)

    # Tenders – store and also create a linking collection for referenced standards
    tenders = data.get('tenders', [])
    for tender in tenders:
        tender_doc = tender.copy()
        # Extract referenced standard numbers for linking
        ref_stds = tender_doc.pop('referenced_standards', [])
        tender_id = tenders_col.insert_one(tender_doc).inserted_id
        for rs in ref_stds:
            tender_refs_col.insert_one({
                'tender_id': tender_id,
                'standard_number': rs.get('standard_number')
            })

    # Compliance metadata – any top‑level key that is not covered (e.g., 'compliance')
    for key in data.keys():
        if key not in {'product', 'components', 'standards', 'tenders'}:
            meta_doc = {'product_id': product_id, 'key': key, 'value': data[key]}
            compliance_col.insert_one(meta_doc)

def ingest_all_raw_json():
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/raw'))
    for fname in os.listdir(raw_dir):
        if fname.lower().endswith('.json') and fname in {
            'Ordinary_Portland_Cement_With_Compliance.json',
            'Industrial_Safety_Helmet_Updated_Complete.json'
        }:
            fpath = os.path.join(raw_dir, fname)
            print(f'Ingesting {fname}...')
            ingest_json_file(fpath)

if __name__ == '__main__':
    ingest_all_raw_json()
    print('MongoDB ingestion completed.')
