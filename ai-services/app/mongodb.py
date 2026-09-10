# MongoDB client shared across the app
import os
import json
from pymongo import MongoClient

# Load .env if present (same logic as mongo_ingest)
import pathlib
# First, try to load .env located in the ai-services directory
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

MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    raise RuntimeError('MONGO_URI not set in environment')
DB_NAME = os.getenv('MONGO_DB_NAME', 'indian_standards_ai')

client = MongoClient(MONGO_URI)
# Verify connection
client.admin.command('ping')

db = client[DB_NAME]

# Collections used throughout the app
standards_col = db['standards']
