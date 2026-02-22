from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from agents import find_smb_leads
import uvicorn
import asyncio

app = FastAPI(title="DataVex Enterprise Intelligence API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    service_category: str = "Application Development"

class DeepAnalysisRequest(BaseModel):
    domain: str
    service_category: str = "Application Development"

class Lead(BaseModel):
    name: str
    domain: str
    why_we_help: str

class EmailRequest(BaseModel):
    company_name: str
    domain: str
    why_we_help: str
    service_category: str

class EmailResponse(BaseModel):
    email_body: str

class AnalysisResponse(BaseModel):
    leads: List[Lead]
    agent_trace: List[str]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: RecommendationRequest):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, find_smb_leads,
            request.service_category
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deep_analyze")
async def deep_analyze_company(request: DeepAnalysisRequest):
    try:
        from agents import run_intelligence
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, run_intelligence,
            request.domain,
            request.service_category
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_email", response_model=EmailResponse)
async def generate_email(request: EmailRequest):
    try:
        from agents import draft_cold_email
        loop = asyncio.get_event_loop()
        email_body = await loop.run_in_executor(
            None, 
            draft_cold_email,
            request.company_name,
            request.domain,
            request.why_we_help,
            request.service_category
        )
        return {"email_body": email_body}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
