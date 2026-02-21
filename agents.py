# agents.py — DataVex Enterprise Intelligence Engine
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from serpapi import GoogleSearch
from typing import Dict, Any

# -----------------------------
# CONFIG
# -----------------------------
SERPAPI_KEY = ""  # Optional
HEADERS = {"User-Agent": "Mozilla/5.0"}

DATAVEX_SERVICES = {
    "cloud_cost_optimization": "Reduce cloud waste and infra leakage",
    "data_pipeline_efficiency": "Improve ETL reliability & performance",
    "infra_observability": "Detect performance bottlenecks",
    "scale_readiness_audit": "Prepare systems for growth"
}

# -----------------------------
# RECON AGENT
# -----------------------------
def recon_agent(domain: str, trace: list) -> Dict[str, Any]:
    trace.append("Recon Agent: Starting website scan")

    if not domain.startswith("http"):
        url = f"https://{domain}"
    else:
        url = domain

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        text = soup.get_text().lower()
        title = soup.title.string.strip() if soup.title else "Unknown"

        trace.append(f"Recon Agent: Status {response.status_code}")

        return {
            "status": response.status_code,
            "title": title,
            "text": text,
            "headers": str(response.headers).lower()
        }

    except Exception as e:
        trace.append(f"Recon Agent: Failed ({str(e)})")
        return {"status": 0, "title": "Unknown", "text": "", "headers": ""}


# -----------------------------
# INFRASTRUCTURE AGENT
# -----------------------------
def infra_agent(recon: Dict[str, Any], trace: list):
    trace.append("Infrastructure Agent: Detecting cloud stack")

    text = recon["text"]

    signals = []

    # Direct cloud keywords
    if any(k in text for k in ["aws", "gcp", "azure", "kubernetes", "docker"]):
        signals.append("Explicit Cloud Stack")

    # SaaS inference (hackathon logic)
    if any(k in text for k in ["api", "platform", "payment", "testing", "developer", "cloud"]):
        signals.append("Inferred Cloud-Heavy SaaS")

    trace.append(f"Infrastructure Agent: Found {signals}")
    return signals


# -----------------------------
# GROWTH AGENT
# -----------------------------
def growth_agent(recon: Dict[str, Any], trace: list):
    trace.append("Growth Agent: Checking hiring & expansion signals")

    text = recon["text"]

    hiring_mentions = len(re.findall(r"hiring|careers|jobs|join us", text))
    scale_mentions = len(re.findall(r"growing|expanding|scale|rapid growth", text))

    trace.append(f"Growth Agent: hiring={hiring_mentions}, scale={scale_mentions}")

    return {
        "hiring_mentions": hiring_mentions,
        "scale_mentions": scale_mentions
    }


# -----------------------------
# FISCAL PRESSURE AGENT
# -----------------------------
def fiscal_agent(domain: str, trace: list):
    trace.append("Fiscal Agent: Checking funding/layoff signals")

    if not SERPAPI_KEY:
        trace.append("Fiscal Agent: SerpAPI not configured")
        return {"funding": False, "layoffs": False}

    query = f"{domain} funding OR layoffs OR cost cutting"

    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        news = results.get("news_results", [])

        funding = any("funding" in n["title"].lower() for n in news)
        layoffs = any("layoff" in n["title"].lower() for n in news)

        trace.append(f"Fiscal Agent: funding={funding}, layoffs={layoffs}")

        return {"funding": funding, "layoffs": layoffs}

    except:
        trace.append("Fiscal Agent: News fetch failed")
        return {"funding": False, "layoffs": False}


# -----------------------------
# STRATEGIC SYNTHESIS AGENT
# -----------------------------
def synthesis_agent(infra, growth, fiscal, trace):
    trace.append("Synthesis Agent: Calculating strategic scores")

    score = 0

    # Infrastructure complexity
    if infra:
        score += 25

    # Growth timing
    if growth["hiring_mentions"] > 3:
        score += 25
    elif growth["hiring_mentions"] > 0:
        score += 15

    if growth["scale_mentions"] > 2:
        score += 15

    # Fiscal signals
    if fiscal["funding"]:
        score += 20
    if fiscal["layoffs"]:
        score += 10

    if "Inferred Cloud-Heavy SaaS" in infra:
        score += 10

    score = min(score, 100)

    recommendation = "YES" if score >= 50 else "NO"
    
    trace.append(f"Synthesis Agent: Score={score}, Verdict={recommendation}")

    why_now = []

    if growth["hiring_mentions"] > 0:
        why_now.append("active hiring surge")
    if infra:
        why_now.append("cloud-heavy architecture")
    if fiscal["funding"]:
        why_now.append("recent funding event")

    return {
        "score": score,
        "recommendation": recommendation,
        "why_now": ", ".join(why_now) if why_now else "limited timing signals"
    }


# -----------------------------
# OUTREACH AGENT
# -----------------------------
def outreach_agent(domain, synthesis, trace):
    if synthesis["recommendation"] == "NO":
        trace.append("Outreach Agent: Skipped")
        return None

    trace.append("Outreach Agent: Generating CTO-focused pitch")

    email = f"""
Subject: Supporting {domain}'s Infrastructure at Scale

Hi CTO,

We noticed signs of {synthesis['why_now']} at {domain}.

As engineering teams scale, cloud costs and data complexity grow rapidly.
DataVex helps teams optimize infrastructure efficiency, reduce cloud waste,
and improve data pipeline reliability without slowing innovation.

Would you be open to a 20-minute discussion this week?

Best,
DataVex Team
"""

    return {
        "target_role": "CTO",
        "angle": "Infrastructure Scale Optimization",
        "draft_email": email.strip()
    }


# -----------------------------
# MAIN EXECUTION
# -----------------------------
def run_intelligence(domain: str):
    trace = []

    recon = recon_agent(domain, trace)
    infra = infra_agent(recon, trace)
    growth = growth_agent(recon, trace)
    fiscal = fiscal_agent(domain, trace)
    synthesis = synthesis_agent(infra, growth, fiscal, trace)
    outreach = outreach_agent(domain, synthesis, trace)

    return {
        "company_dossier": {
            "domain": domain,
            "title": recon["title"],
            "infrastructure": infra,
            "growth_signals": growth,
            "fiscal_signals": fiscal,
            "analysis_timestamp": datetime.now().isoformat()
        },
        "strategic_analysis": {
            "why_now": synthesis["why_now"],
            "lead_score": synthesis["score"]
        },
        "verdict": {
            "recommendation": synthesis["recommendation"],
            "confidence": round(synthesis["score"] / 100, 2)
        },
        "outreach_strategy": outreach,
        "agent_trace": trace
    }


if __name__ == "__main__":
    print("🚀 DataVex Enterprise Intelligence Engine")
    print("=" * 60)

    domain = input("Enter company domain: ").strip()
    result = run_intelligence(domain)

    from pprint import pprint
    pprint(result)