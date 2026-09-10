import sys
import os
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.llm import extract_requirements
from app.engine import rank_and_format_standards

def test_ranking():
    queries = [
        "I need Ordinary Portland Cement Grade 43 for construction of a government building.",
        "I need industrial safety helmets for workers with impact and penetration protection."
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n{'='*40}")
        print(f"Test {i}: {q}")
        print(f"{'='*40}")
        
        # 1. Extraction
        reqs = extract_requirements(q)
        print(f"\n[1] Extracted Requirements:\n{json.dumps(reqs, indent=2)}")
        
        # 2. Ranking
        print(f"\n[2] Executing Semantic Retrieval and Ranking...")
        results = rank_and_format_standards(q, reqs)
        
        print(f"\n[3] Top Recommendations ({len(results)} found):")
        for idx, res in enumerate(results, 1):
            print(f"\n  #{idx} {res['standardNumber']} - {res['title']}")
            print(f"      Score: {res['applicabilityScore']}")
            print(f"      Reasons: {', '.join(res['reasons'])}")
            print(f"      Scope: {res['scope'][:100]}...")

if __name__ == "__main__":
    test_ranking()
