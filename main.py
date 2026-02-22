from fastapi import FastAPI
from agents import run_intelligence

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/analyze")
def analyze(domain: str):
    return run_intelligence(domain)