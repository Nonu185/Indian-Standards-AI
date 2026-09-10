import json
import os
import ollama
from pydantic import BaseModel, Field
from typing import List

LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:4b")

class ProcurementRequirement(BaseModel):
    product: str = Field(default="")
    category: str = Field(default="")
    application: str = Field(default="")
    grade: str = Field(default="")
    material: str = Field(default="")
    technical_requirements: List[str] = Field(default_factory=list)
    certification_requirements: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

def extract_requirements(text: str) -> dict:
    prompt = f"""
Extract procurement requirements from the following user query and output the result strictly in JSON format matching the schema below.
If a piece of information is not present in the query, use an empty string or empty array.

Schema:
{{
  "product": "string",
  "category": "string",
  "application": "string",
  "grade": "string",
  "material": "string",
  "technical_requirements": ["string"],
  "certification_requirements": ["string"],
  "keywords": ["string"]
}}

Query: {text}
"""
    try:
        response = ollama.chat(model=LLM_MODEL, messages=[
            {
                'role': 'system',
                'content': 'You are an AI assistant that extracts procurement requirements. Output strictly raw JSON, with no markdown code blocks or additional text.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ], options={"temperature": 0.1})
        
        content = response.get('message', {}).get('content', '').strip()
        
        # Strip markdown formatting if any
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        parsed = json.loads(content)
        validated = ProcurementRequirement(**parsed)
        return validated.model_dump()
    except Exception as e:
        print(f"Extraction error: {e}")
        # Return empty schema if parsing fails
        return ProcurementRequirement().model_dump()
