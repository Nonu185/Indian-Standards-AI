from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.llm import extract_requirements
from app.engine import rank_and_format_standards
from app.mongodb import standards_col

app = FastAPI(title="Indian Standards AI - AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractRequest(BaseModel):
    text: str

@app.get("/health")
def health_check():
    # Count standards in MongoDB collection
    try:
        count = standards_col.count_documents({})
    except Exception:
        count = 0

    return {
        "status": "ok",
        "service": "indian-standards-ai",
        "standards_in_db": count
    }

@app.post("/extract-requirements")
def extract_reqs(request: ExtractRequest):
    try:
        requirements = extract_requirements(request.text)
        return {
            "success": True,
            "requirements": requirements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend")
def recommend_standards(request: ExtractRequest):
    try:
        # Step 1: Extract requirements using qwen3:8b
        requirements = extract_requirements(request.text)
        
        # Step 2: Retrieve from DB and Rank
        recommendations = rank_and_format_standards(request.text, requirements)
        
        return {
            "success": True,
            "query": request.text,
            "extracted_requirements": requirements,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
