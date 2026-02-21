from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from agents import run_intelligence
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

class AnalysisRequest(BaseModel):
    domain: str

class AnalysisResponse(BaseModel):
    company_dossier: Dict[str, Any]
    strategic_analysis: Dict[str, Any]
    verdict: Dict[str, Any]
    outreach_strategy: Dict[str, Any]
    agent_trace: List[str]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: AnalysisRequest):
    try:
        # Run the intelligence engine
        # Since run_intelligence might take time, we run it in a thread/executor
        # to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_intelligence, request.domain.strip())
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
