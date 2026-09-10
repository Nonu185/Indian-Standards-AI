import sys
import os
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.llm import extract_requirements

def test_queries():
    queries = [
        "I need Ordinary Portland Cement Grade 43 for construction of a government building.",
        "I need industrial safety helmets for workers with impact and penetration protection.",
        "I need M5 stainless steel hex screws, 20 mm long."
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n--- Test {i} ---")
        print(f"Input: {q}")
        try:
            result = extract_requirements(q)
            print(f"Extracted JSON:\n{json.dumps(result, indent=2)}")
            print("Validation status: OK")
        except Exception as e:
            print(f"Extracted JSON: Error")
            print(f"Validation status: Failed - {e}")

if __name__ == "__main__":
    test_queries()
