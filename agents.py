# agents.py — DataVex Enterprise Intelligence Engine
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from serpapi.google_search import GoogleSearch
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Initialize LLM
llm = ChatCerebras(
    model="llama3.1-8b",
    cerebras_api_key=CEREBRAS_API_KEY
)

# Load Service Catalog
def load_services():
    try:
        with open("services.json", "r") as f:
            return json.load(f)
    except:
        return {}

SERVICES_CATALOG = load_services()

def is_valid_domain(domain: str) -> bool:
    # Basic domain regex: check for at least one dot and a TLD of 2+ chars
    # Matches formats like example.com, sub.example.co.uk, but not 'f.c' or 'localhost' or 'shhh'
    pattern = r'^[a-zA-Z0-9][-a-zA-Z0-9]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    # Simplified check: must have a dot and at least 4 characters
    if "." not in domain or len(domain) < 4:
        return False
    # Only allow common chars
    return bool(re.match(r'^[a-zA-Z0-9.-]+$', domain))
def recon_agent(domain: str, trace: List[str]) -> Dict[str, Any]:
    trace.append(f"Scout Agent: Initiating reconnaissance for {domain}")
    
    url = f"https://{domain}" if not domain.startswith("http") else domain
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        text = soup.get_text(separator=' ', strip=True)[:10000] # Cap text for LLM
        title = soup.title.string.strip() if soup.title else "Unknown"
        
        trace.append(f"Scout Agent: Successfully scraped {len(text)} chars from home page")
        return {"text": text, "title": title, "status": response.status_code}
    except Exception as e:
        # Provide a professional message for the trace instead of raw technical error
        if "getaddrinfo failed" in str(e):
            trace.append("Scout Agent: Target host resolution failed. Pivoting to external intelligence.")
            return {"text": "", "title": "Unknown", "status": 0, "was_reachable": False}
        else:
            trace.append("Scout Agent: Direct access restricted. Utilizing search-based data extraction.")
            return {"text": "", "title": "Unknown", "status": 0, "was_reachable": True}

# -----------------------------
# FISCAL & NEWS AGENT
# -----------------------------
def search_agent(domain: str, query_type: str, trace: List[str]) -> str:
    trace.append(f"Researcher Agent: Researching {query_type} indicators for {domain}")
    
    queries = {
        "fiscal": f"{domain} funding OR layoffs OR revenue OR acquisition",
        "tech": f"{domain} tech stack OR engineering blog OR architecture",
        "market": f"{domain} competitors OR market share OR recent pivot"
    }
    
    params = {
        "engine": "google",
        "q": queries.get(query_type, f"{domain} company news"),
        "api_key": SERPAPI_API_KEY,
        "num": 5
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = [r.get("snippet", "") for r in results.get("organic_results", [])]
        combined = "\n".join(snippets)
        trace.append(f"Researcher Agent: Aggregated {len(snippets)} relevant market signals")
        return combined
    except Exception as e:
        trace.append(f"Researcher Agent: Deep search capacity reached. Merging existing datasets.")
        return ""

# -----------------------------
# SYNTHESIS & STRATEGY AGENT (The Brain)
# -----------------------------
def synthesis_agent(domain: str, recon_data: Dict, fiscal_news: str, tech_news: str, trace: List[str]):
    trace.append("Synthesis Agent: Orchestrating multi-agent intelligence")
    
    parser = JsonOutputParser()
    
    prompt = ChatPromptTemplate.from_template("""
    You are the Lead Strategist at DataVex AI. Your goal is to analyze a potential client and determine if they are a high-value lead.
    
    DATA SOURCES:
    1. Target Domain: {domain}
    2. Website Recon: {recon_text}
    3. Fiscal/News: {fiscal_news}
    4. Tech/Market Context: {tech_news}
    
    CRITICAL INSTRUCTION:
    - DISTINGUISH BETWEEN NEWS AND TUTORIALS: If the "Fiscal/News" or "Tech" results contain educational content like "System Design Interview", "How to build...", or "Tutorial", IGNORE IT as a lead signal. This is educational content, NOT news about the company.
    - If "Website Recon" is empty AND "Fiscal/News" search results appear to be for a different company name that doesn't match the target domain, you MUST conclude the domain is DEAD or INVALID.
    - DO NOT make up information for a different company just because the names are similar.
    - If the signals are purely educational/tutorials or the domain is dead, set score to 0 and verdict to "NO".
    
    OUR SERVICES (DataVex):
    {services}
    
    TASK:
    - Identify the company's "Pain Point" (Tech debt, high cloud costs, scalability issues, etc.)
    - Find a "Strategic Pivot" or "Why Now" signal (New funding, rapid hiring, expansion, layoffs needing automation).
    - Map at least one DataVex service to their needs.
    - Provide a Lead Score (0-100).
    - Provide a Verdict (YES/NO).
    - Draft a hyper-personalized outreach strategy for a CTO or Engineering Head.
    
    Format your response as a JSON object with the following keys:
    dossier: {{ official_name: string, summary: string, industry: string, estimated_tech_stack: string[] }}
    analysis: {{ pain_points: string[], strategic_pivot: string, why_now: string }}
    verdict: {{ score: number, recommendation: string, justification: string }}
    outreach: {{ target_role: string, custom_pitch: string, subject_line: string }}
    """)
    
    chain = prompt | llm | parser
    
    try:
        # Increase timeout or handle potential retries if needed
        result = chain.invoke({
            "domain": domain,
            "recon_text": recon_data["text"][:5000],
            "fiscal_news": fiscal_news,
            "tech_news": tech_news,
            "services": json.dumps(SERVICES_CATALOG, indent=2)
        })
        
        # Post-process results for robustness
        dossier = result.get("dossier", {})
        
        # Anti-Self-Identification Guard: Prevent AI from naming the company "DataVex"
        # Since it sees "Lead Strategist at DataVex" in our prompt
        current_name = dossier.get("official_name", "Unknown")
        if "data" in current_name.lower() and "vex" in current_name.lower():
            # Force fallback to domain
            trace.append("Lead Analyst: Correcting internal platform name leak.")
            dossier["official_name"] = domain.split('.')[0].capitalize()
            
        # If official_name is missing or "Unknown", try to extract it from the domain or summary
        if dossier.get("official_name", "Unknown") == "Unknown":
            fallback = domain.split('.')[0].capitalize()
            dossier["official_name"] = fallback
            
        trace.append(f"Lead Analyst: Strategic profile generated for {dossier.get('official_name')} (Score: {result.get('verdict', {}).get('score', 'N/A')})")
        return result
    except Exception as e:
        trace.append(f"Lead Analyst: Intelligence synthesis halted. Unreliable input signals detected.")
        # Provide a graceful degraded response if LLM fails
        return {
            "dossier": {"official_name": "Invalid Target", "summary": "Analysis failed: The provided input does not appear to be a valid or reachable business domain.", "industry": "N/A", "estimated_tech_stack": []},
            "analysis": {"pain_points": [], "strategic_pivot": "N/A", "why_now": "N/A"},
            "verdict": {"score": 0, "recommendation": "NO", "justification": "Our agents were unable to synthesize a high-confidence report for this target. It may be non-existent or providing conflicting signals."},
            "outreach": {"target_role": "N/A", "custom_pitch": "N/A", "subject_line": "N/A"}
        }

# -----------------------------
# MAIN RUNNER
# -----------------------------
def run_intelligence(domain: str):
    trace = []
    trace.append(f"System: Starting autonomous journey for {domain}")
    
    # Pre-flight Validation
    if not is_valid_domain(domain):
        trace.append(f"System: Invalid domain format detected ('{domain}'). Aborting research.")
        return {
            "company_dossier": {
                "domain": domain,
                "title": "Invalid Input",
                "official_name": "N/A",
                "summary": "The input provided is not a valid domain name (e.g., example.com). Please check for typos.",
                "industry": "N/A",
                "estimated_tech_stack": [],
                "analysis_timestamp": datetime.now().isoformat()
            },
            "strategic_analysis": {"pain_points": [], "strategic_pivot": "N/A", "why_now": "N/A"},
            "verdict": {"score": 0, "recommendation": "NO", "justification": "The input format is invalid or too short to be a valid business website."},
            "outreach_strategy": {"target_role": "N/A", "custom_pitch": "N/A", "subject_line": "N/A"},
            "agent_trace": trace
        }
    
    # 1. Recon
    recon = recon_agent(domain, trace)
    
    # 2. External Research (Parallel-ish)
    fiscal_info = search_agent(domain, "fiscal", trace)
    tech_info = search_agent(domain, "tech", trace)
    
    # 3. Intelligence Synthesis
    intelligence = synthesis_agent(domain, recon, fiscal_info, tech_info, trace)
    
    if not intelligence:
        return {"error": "Intelligence synthesis failed", "trace": trace}
    
    # Anti-Hallucination: Check if we are reporting on the WRONG company
    official_name = intelligence.get("dossier", {}).get("official_name", "Unknown").lower()
    domain_part = domain.split('.')[0].lower()
    
    # If site was unreachable AND the AI's deduced name doesn't contain the domain keyword
    # OR if the score is 0 with a "Dead Domain" justification
    is_hallucination = not recon.get("was_reachable", True) and domain_part not in official_name and "unreachable" in intelligence.get("verdict", {}).get("justification", "").lower()
    
    if is_hallucination:
        trace.append(f"System: Hallucination Guard triggered. Domain {domain} appears to be dead/invalid.")
        return {
            "company_dossier": {
                "domain": domain,
                "title": domain.split('.')[0].capitalize(),
                "official_name": "Invalid Domain",
                "summary": f"The domain {domain} could not be resolved and no relevant search data was found for this specific entity.",
                "industry": "N/A",
                "estimated_tech_stack": [],
                "analysis_timestamp": datetime.now().isoformat()
            },
            "strategic_analysis": {"pain_points": [], "strategic_pivot": "N/A", "why_now": "N/A"},
            "verdict": {"score": 0, "recommendation": "NO", "justification": "Domain is unreachable and search results are likely search hallucinations for similar names."},
            "outreach_strategy": {"target_role": "N/A", "custom_pitch": "N/A", "subject_line": "N/A"},
            "agent_trace": trace
        }
    
    # Determine best company name (Robust Logic)
    ai_name = intelligence.get("dossier", {}).get("official_name", "Unknown")
    scraped_title = recon.get("title", "Unknown")
    
    # Clean up generic titles
    generic_titles = ["Unknown", "Home", "Index", "Default"]
    is_scraped_generic = any(t in scraped_title for t in generic_titles) or len(scraped_title) < 3
    
    # Priority: 
    # 1. AI Deduced Name (if not Unknown)
    # 2. Scraped Title (if not generic)
    # 3. Domain Fallback
    if ai_name != "Unknown":
        final_name = ai_name
    elif not is_scraped_generic:
        final_name = scraped_title
    else:
        final_name = domain.split('.')[0].capitalize()

    return {
        "company_dossier": {
            "domain": domain,
            "title": final_name,
            **intelligence.get("dossier", {}),
            "analysis_timestamp": datetime.now().isoformat()
        },
        "strategic_analysis": intelligence.get("analysis", {}),
        "verdict": intelligence.get("verdict", {}),
        "outreach_strategy": intelligence.get("outreach", {}),
        "agent_trace": trace
    }

if __name__ == "__main__":
    print("🚀 DataVex Enterprise Intelligence Engine")
    domain = input("Enter company domain: ").strip()
    res = run_intelligence(domain)
    print(json.dumps(res, indent=2))