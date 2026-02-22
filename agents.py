# agents.py — DataVex SMB Intelligence Engine
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from serpapi.google_search import GoogleSearch
from typing import Dict, Any, List, Tuple
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

# LLM is initialized lazily inside synthesis_agent to avoid
# crashing at startup when the API key is missing or invalid.

# Load Service Catalog
def load_services():
    try:
        with open("services.json", "r") as f:
            return json.load(f)
    except:
        return {}

SERVICES_CATALOG = load_services()

# -----------------------------
# KNOWN ENTERPRISE BLOCKLIST
# Domains of companies that clearly don't need DataVex
# -----------------------------
ENTERPRISE_BLOCKLIST = {
    # Big Tech
    "amazon.com", "aws.amazon.com", "google.com", "apple.com", "microsoft.com",
    "meta.com", "facebook.com", "instagram.com", "whatsapp.com", "linkedin.com",
    "twitter.com", "x.com", "netflix.com", "spotify.com", "adobe.com",
    "salesforce.com", "oracle.com", "ibm.com", "sap.com", "intel.com",
    "qualcomm.com", "nvidia.com", "amd.com", "cisco.com", "vmware.com",
    "servicenow.com", "workday.com", "zendesk.com", "atlassian.com",
    "slack.com", "zoom.us", "dropbox.com", "box.com", "hubspot.com",
    "shopify.com", "stripe.com", "twilio.com", "datadog.com", "snowflake.com",
    "mongodb.com", "elastic.co", "palantir.com", "cloudflare.com",
    # Banks & Finance giants
    "jpmorgan.com", "goldman.com", "bankofamerica.com", "wellsfargo.com",
    "citibank.com", "hsbc.com", "barclays.com", "ubs.com", "morgan stanley.com",
    "visa.com", "mastercard.com", "paypal.com", "americanexpress.com",
    # Retail giants
    "walmart.com", "target.com", "ebay.com", "alibaba.com", "flipkart.com",
    # Consulting & Enterprise Services
    "mckinsey.com", "deloitte.com", "pwc.com", "kpmg.com", "accenture.com",
    "infosys.com", "wipro.com", "tcs.com", "cognizant.com", "hcltech.com",
    # Telecom
    "att.com", "verizon.com", "tmobile.com", "comcast.com", "vodafone.com",
    "airtel.com", "jio.com",
    # Other massive ones
    "tesla.com", "ford.com", "toyota.com", "boeing.com", "siemens.com",
    "ge.com", "3m.com", "samsung.com", "lg.com", "sony.com",
    "youtube.com", "reddit.com", "wikipedia.org", "github.com",
}

# Keywords in scraped website text that strongly indicate a large enterprise
LARGE_ENTERPRISE_SIGNALS = [
    r"\b(fortune\s*500|fortune\s*1000)\b",
    r"\b(nasdaq|nyse|bse|nse)\s*[:]\s*[A-Z]+\b",  # stock ticker
    r"\b(publicly\s*traded|public\s*company|publicly\s*listed)\b",
    r"\b(\d{1,3}[,\s]\d{3}[,\s]\d{3})\s*(employees|staff|workforce)\b",  # 100,000+ employees
    r"\b([5-9]\d{4}|\d{6,})\s*\+?\s*(employees|staff|people|workforce)\b",  # 50000+ employees
    r"\$\s*\d+\s*(billion|bn)\b.*?(revenue|valuation|market\s*cap)",
    r"\b(global\s*headquarters|worldwide\s*operations|offices\s*in\s*\d+\s*countries)\b",
    r"\b(we\s*(serve|have)\s*\d+\s*million\s*(customers|users))\b",
]

# Keywords that signal a SMALL company — good lead indicators
SMB_POSITIVE_SIGNALS = [
    r"\b(seed|series[\s-]?[ab]|bootstrapped|self[\s-]?funded|early[\s-]?stage)\b",
    r"\bstarting\s*(from)?\s+\$\d+\b",  # pricing starting from small amounts
    r"\bteam\s*of\s*\d{1,2}\b",  # "team of 5", "team of 12"
    r"\bfounded\s*in\s*20(1[5-9]|2[0-9])\b",  # recently founded
    r"\b(small\s*team|lean\s*team|growing\s*team|startup)\b",
    r"\b\d{1,3}\s*(employees|people|team\s*members)\b",  # under 999 employees mentioned explicitly
]

def normalize_domain(raw_input: str) -> str:
    """Strip protocol, www, paths, and query strings from any URL/domain input."""
    raw = raw_input.strip()
    raw = re.sub(r'^https?://', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'^www\.', '', raw, flags=re.IGNORECASE)
    raw = raw.split('/')[0].split('?')[0].split('#')[0]
    raw = raw.split(':')[0]
    return raw.strip().lower()

def is_valid_domain(domain: str) -> bool:
    if "." not in domain or len(domain) < 4:
        return False
    return bool(re.match(r'^[a-zA-Z0-9.-]+$', domain))

def _make_early_rejection(domain: str, reason: str, trace: List[str]) -> Dict:
    """Return a structured rejection response without calling the LLM."""
    name = domain.split('.')[0].capitalize()
    trace.append(f"Size Guard: {reason}")
    return {
        "company_dossier": {
            "domain": domain,
            "title": name,
            "official_name": name,
            "summary": f"This domain belongs to a large enterprise that already has a dedicated internal engineering team. DataVex.ai targets small and growing businesses that need an external tech partner.",
            "industry": "Large Enterprise",
            "estimated_tech_stack": [],
            "company_size": "1000+ employees",
            "company_stage": "Large Enterprise",
            "analysis_timestamp": datetime.now().isoformat()
        },
        "strategic_analysis": {
            "pain_points": [],
            "strategic_pivot": "N/A",
            "why_now": "N/A",
            "datavex_service_match": "N/A — Not a fit"
        },
        "verdict": {
            "score": 0,
            "recommendation": "NO",
            "justification": reason,
            "size_flag": "LARGE ENTERPRISE — NOT A FIT"
        },
        "outreach_strategy": {
            "target_role": "N/A",
            "custom_pitch": "N/A",
            "subject_line": "N/A"
        },
        "agent_trace": trace
    }

# -----------------------------
# PHASE 1: ENTERPRISE PRE-SCREENER (deterministic, no LLM)
# -----------------------------
def enterprise_prescreen(domain: str, recon_text: str, fiscal_news: str, trace: List[str]) -> Tuple[bool, str]:
    """
    Returns (is_enterprise, reason_string).
    Runs BEFORE the LLM to block large companies without wasting API credits.
    """
    trace.append("Size Guard: Running enterprise pre-screen...")

    # 1. Hard blocklist check
    clean = domain.lower().strip()
    # Check for exact match or subdomain match
    for blocked in ENTERPRISE_BLOCKLIST:
        if clean == blocked or clean.endswith("." + blocked):
            return True, f"{domain} is a globally recognized large enterprise. DataVex targets small/growing businesses (10–500 employees)."

    # 2. Regex signal scan on scraped text + news combined
    combined_text = (recon_text + " " + fiscal_news).lower()

    for pattern in LARGE_ENTERPRISE_SIGNALS:
        if re.search(pattern, combined_text, re.IGNORECASE):
            return True, f"Enterprise signals detected in public data for {domain}. Large companies have in-house teams and do not need DataVex's services."

    # 3. Not blocked → pass to LLM
    trace.append("Size Guard: No enterprise signals detected. Proceeding to deep analysis.")
    return False, ""


# -----------------------------
# PHASE 2: RECON AGENT
# -----------------------------
def recon_agent(domain: str, trace: List[str]) -> Dict[str, Any]:
    trace.append(f"Scout Agent: Initiating reconnaissance for {domain}")

    url = f"https://{domain}" if not domain.startswith("http") else domain
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text(separator=' ', strip=True)[:10000]
        title = soup.title.string.strip() if soup.title else "Unknown"

        trace.append(f"Scout Agent: Successfully scraped {len(text)} chars from home page")
        return {"text": text, "title": title, "status": response.status_code, "was_reachable": True}
    except Exception as e:
        if "getaddrinfo failed" in str(e) or "Name or service not known" in str(e):
            trace.append("Scout Agent: Target host resolution failed. Pivoting to external intelligence.")
            return {"text": "", "title": "Unknown", "status": 0, "was_reachable": False}
        else:
            trace.append("Scout Agent: Direct access restricted. Utilizing search-based data extraction.")
            return {"text": "", "title": "Unknown", "status": 0, "was_reachable": True}


# -----------------------------
# PHASE 3: SEARCH AGENT
# -----------------------------
def search_agent(domain: str, query_type: str, trace: List[str]) -> str:
    trace.append(f"Researcher Agent: Researching {query_type} indicators for {domain}")

    queries = {
        "fiscal": f'"{domain}" company funding OR employees OR revenue OR startup -site:{domain}',
        "tech": f'"{domain}" tech stack OR engineering OR software -tutorial -course -how-to',
        "size": f'"{domain}" company size OR team OR employees OR headcount OR linkedin',
    }

    params = {
        "engine": "google",
        "q": queries.get(query_type, f"{domain} company overview"),
        "api_key": SERPAPI_API_KEY,
        "num": 5
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = [r.get("snippet", "") for r in results.get("organic_results", [])]
        combined = "\n".join(snippets)
        trace.append(f"Researcher Agent: Aggregated {len(snippets)} market signals")
        return combined
    except Exception:
        trace.append("Researcher Agent: Search quota reached. Merging existing datasets.")
        return ""


# -----------------------------
# PHASE 4: SMB SYNTHESIS AGENT (LLM — only reached if pre-screen passes)
# -----------------------------
def synthesis_agent(domain: str, recon_data: Dict, fiscal_news: str, size_info: str, service_category: str, trace: List[str]):
    trace.append(f"Lead Analyst: Running SMB qualification analysis focused on '{service_category}'...")

    llm = ChatCerebras(
        model="llama3.1-8b",
        api_key=CEREBRAS_API_KEY
    )

    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_template("""
You are the Lead Qualifier at DataVex AI, a boutique tech agency from Mangaluru, India that helps SMALL and GROWING businesses.

DataVex's services: {services}

DataVex's IDEAL CUSTOMER PROFILE (ICP):
- Company size: 10 to 500 employees
- Stage: Seed, Series A, Series B, or self-funded SMB
- Needs: custom software, AI solutions, cloud setup, CI/CD, automation — things a small team can't do in-house
- Budget: SMB-level; they want a reliable external tech partner, not a full-time hire

---
TARGET COMPANY DATA:
Domain: {domain}
Target Service to Pitch: {service_category}
Website Content: {recon_text}
Fiscal / News Signals: {fiscal_news}
Size / Team Signals: {size_info}
---

YOUR JOB:
1. Estimate the company's employee count and funding stage from the data.
2. Identify their top tech pain points (specifically looking for pain related to {service_category}).
3. Find a "Why Now" window (new hire, new product, recent funding, scaling challenges).
4. Match exactly how DataVex's {service_category} service solves their pain.
5. Score the lead 0–100:
   - 0–10: Clearly a large corp (100K+ employees, Fortune 500, publicly traded giant) — NOT a fit
   - 11–35: Mid-market (500–5000 emp) with no obvious pain — weak fit
   - 36–60: Mid-market with clear tech pain — possible fit
   - 61–100: Small biz (10–500 emp) with real tech pain & budget signals — BEST leads
6. Give a YES/NO recommendation
7. Write a short, personalized outreach pitch for their Founder / CTO / Head of Engineering

IMPORTANT RULES:
- If the company is clearly world-famous (Amazon, Google, Walmart, Reliance, etc.) → score must be 0, verdict NO
- If domain is dead or unresolvable → score 0, verdict NO
- Do NOT hallucinate. If you can't identify the company, say so clearly.
- Do NOT use "N/A" for size_flag — choose: "SMALL (✓ Best Fit)", "MID-MARKET (Possible)", or "LARGE ENTERPRISE (✗ Not a Fit)"

Return STRICTLY valid JSON with these keys (no extra text before or after):
{{
  "dossier": {{
    "official_name": "string",
    "summary": "string",
    "industry": "string",
    "estimated_tech_stack": ["string"],
    "company_size": "string (e.g. '20-50 employees')",
    "company_stage": "string (e.g. 'Series A', 'Bootstrapped', 'SMB')"
  }},
  "analysis": {{
    "pain_points": ["string"],
    "strategic_pivot": "string",
    "why_now": "string",
    "datavex_service_match": "string"
  }},
  "verdict": {{
    "score": 0,
    "recommendation": "YES or NO",
    "justification": "string",
    "size_flag": "SMALL (✓ Best Fit) | MID-MARKET (Possible) | LARGE ENTERPRISE (✗ Not a Fit)"
  }},
  "outreach": {{
    "target_role": "string",
    "subject_line": "string",
    "custom_pitch": "string"
  }}
}}
""")

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "domain": domain,
            "service_category": service_category,
            "recon_text": recon_data["text"][:5000],
            "fiscal_news": fiscal_news,
            "size_info": size_info,
            "services": json.dumps(SERVICES_CATALOG, indent=2)
        })

        # Anti-self-identification guard
        dossier = result.get("dossier", {})
        current_name = dossier.get("official_name", "Unknown")
        if "data" in current_name.lower() and "vex" in current_name.lower():
            trace.append("Lead Analyst: Correcting internal name leak.")
            dossier["official_name"] = domain.split('.')[0].capitalize()

        if dossier.get("official_name", "Unknown") in ("Unknown", ""):
            dossier["official_name"] = domain.split('.')[0].capitalize()

        score = result.get("verdict", {}).get("score", 0)
        trace.append(f"Lead Analyst: Profile generated for {dossier.get('official_name')} — Score: {score}/100")
        return result

    except Exception as e:
        trace.append("Lead Analyst: Synthesis failed. Could not parse LLM response.")
        return {
            "dossier": {
                "official_name": domain.split('.')[0].capitalize(),
                "summary": "Analysis could not be completed. The domain may be too obscure or the data insufficient.",
                "industry": "Unknown",
                "estimated_tech_stack": [],
                "company_size": "Unknown",
                "company_stage": "Unknown"
            },
            "analysis": {"pain_points": [], "strategic_pivot": "N/A", "why_now": "N/A", "datavex_service_match": "N/A"},
            "verdict": {"score": 0, "recommendation": "NO", "justification": str(e), "size_flag": "Unknown"},
            "outreach": {"target_role": "N/A", "subject_line": "N/A", "custom_pitch": "N/A"}
        }


# -----------------------------
# MAIN RUNNER
# -----------------------------
def run_intelligence(domain: str, service_category: str = "Application Development"):
    domain = normalize_domain(domain)
    trace = []
    trace.append(f"System: Starting SMB intelligence scan for [{domain}] targeting '{service_category}'")

    # ── Step 0: Validate domain format ──
    if not is_valid_domain(domain):
        trace.append(f"System: Invalid domain format ('{domain}'). Aborting.")
        return {
            "company_dossier": {
                "domain": domain, "title": "Invalid Input", "official_name": "N/A",
                "summary": "Not a valid domain name (e.g. acme.com). Please re-enter.",
                "industry": "N/A", "estimated_tech_stack": [],
                "company_size": "N/A", "company_stage": "N/A",
                "analysis_timestamp": datetime.now().isoformat()
            },
            "strategic_analysis": {"pain_points": [], "strategic_pivot": "N/A", "why_now": "N/A", "datavex_service_match": "N/A"},
            "verdict": {"score": 0, "recommendation": "NO", "justification": "Invalid domain format.", "size_flag": "N/A"},
            "outreach_strategy": {"target_role": "N/A", "custom_pitch": "N/A", "subject_line": "N/A"},
            "agent_trace": trace
        }

    # ── Step 1: Recon (always run first to feed into pre-screener) ──
    recon = recon_agent(domain, trace)

    # ── Step 2: Quick size search (cheap, feeds pre-screener) ──
    size_info = search_agent(domain, "size", trace)

    # ── Step 3: Enterprise Pre-Screen (deterministic, no LLM cost) ──
    is_enterprise, rejection_reason = enterprise_prescreen(
        domain, recon["text"], size_info, trace
    )
    if is_enterprise:
        result = _make_early_rejection(domain, rejection_reason, trace)
        # Override title with scraped title if we have one
        if recon.get("title") and recon["title"] != "Unknown":
            result["company_dossier"]["title"] = recon["title"]
        return result

    # ── Step 4: Full Research (only for SMB candidates) ──
    fiscal_info = search_agent(domain, "fiscal", trace)

    # ── Step 5: LLM Synthesis ──
    intelligence = synthesis_agent(domain, recon, fiscal_info, size_info, service_category, trace)

    if not intelligence:
        return {"error": "Intelligence synthesis failed", "trace": trace}

    # ── Step 6: Anti-Hallucination guard ──
    official_name = intelligence.get("dossier", {}).get("official_name", "Unknown").lower()
    domain_part = domain.split('.')[0].lower()
    was_reachable = recon.get("was_reachable", True)
    justification = intelligence.get("verdict", {}).get("justification", "").lower()

    is_hallucination = (
        not was_reachable
        and domain_part not in official_name
        and ("unreachable" in justification or "dead" in justification or "invalid" in justification)
    )

    if is_hallucination:
        trace.append(f"System: Hallucination Guard triggered. Domain {domain} appears dead/invalid.")
        return {
            "company_dossier": {
                "domain": domain, "title": domain.split('.')[0].capitalize(),
                "official_name": "Invalid Domain",
                "summary": f"The domain {domain} could not be resolved and no matching business data was found.",
                "industry": "N/A", "estimated_tech_stack": [],
                "company_size": "N/A", "company_stage": "N/A",
                "analysis_timestamp": datetime.now().isoformat()
            },
            "strategic_analysis": {"pain_points": [], "strategic_pivot": "N/A", "why_now": "N/A", "datavex_service_match": "N/A"},
            "verdict": {"score": 0, "recommendation": "NO", "justification": "Domain appears dead or invalid.", "size_flag": "N/A"},
            "outreach_strategy": {"target_role": "N/A", "custom_pitch": "N/A", "subject_line": "N/A"},
            "agent_trace": trace
        }

    # ── Step 7: Build final response ──
    ai_name = intelligence.get("dossier", {}).get("official_name", "Unknown")
    scraped_title = recon.get("title", "Unknown")
    generic_titles = ["Unknown", "Home", "Index", "Default", "Welcome"]
    is_generic = any(t.lower() in scraped_title.lower() for t in generic_titles) or len(scraped_title) < 3

    if ai_name and ai_name != "Unknown":
        final_name = ai_name
    elif not is_generic:
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


# -----------------------------
# PHASE 4: SMB LEAD FINDER (New Category-based Flow)
# -----------------------------
def find_smb_leads(service_category: str) -> Dict[str, Any]:
    trace = []
    trace.append(f"Lead Scout: Hunting for SMB companies that need '{service_category}'")

    queries = {
        "Application Development": "startup 'looking for tech partner' OR 'we are a small team' 'react' 'python' -jobs -job",
        "AI & Data Analytics": "startup 'looking for data science consultant' OR 'we need machine learning' 'small team' -jobs -job",
        "Cloud & DevOps": "startup 'need aws expert' OR 'cloud infrastructure' 'fractional devops' -jobs -job",
        "Digital Transformation": "'digital transformation' 'legacy modernization' 'small business' OR 'automate processes' -jobs -job"
    }

    q = queries.get(service_category, f"startup 'need {service_category} expert'") + " -site:linkedin.com -site:indeed.com -site:glassdoor.com -site:greenhouse.io"
    trace.append(f"Lead Scout: Searching Google for indicators ('{q}')")

    params = {
        "engine": "google",
        "q": q,
        "api_key": SERPAPI_API_KEY,
        "num": 20
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict().get("organic_results", [])
    except Exception as e:
        trace.append(f"System: Google Search API failed: {e}")
        return {"leads": [], "agent_trace": trace}

    candidates = []
    seen_domains = set()

    for r in results:
        link = r.get("link") or r.get("displayed_link", "")
        if not link:
            continue
        try:
            d = normalize_domain(link)
        except:
            continue
            
        if not d or d in seen_domains:
            continue

        # Deterministic screening
        is_blocked = False
        for blocked in ENTERPRISE_BLOCKLIST:
            if d == blocked or d.endswith("." + blocked):
                is_blocked = True
                break
        
        if is_blocked:
            continue

        seen_domains.add(d)
        candidates.append({
            "domain": d,
            "snippet": r.get("snippet", ""),
            "title": r.get("title", "")
        })

        if len(candidates) >= 5: # Cap at top 5 for LLM processing
            break

    trace.append(f"Lead Scout: Found {len(candidates)} valid SMB candidates. Passing to Lead Analyst for qualification.")

    if not candidates:
        trace.append("Lead Analyst: No valid candidates found.")
        return {"leads": [], "agent_trace": trace}

    # Pass to LLM to qualify and generate justifications
    llm = ChatCerebras(
        model="llama3.1-8b",
        api_key=CEREBRAS_API_KEY
    )
    
    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_template("""
You are the Lead Qualifier at DataVex AI, a boutique tech agency from Mangaluru.
You are helping your sales team find SMB leads specifically for: {service_category}

I have scraped Google search results matching companies that might need this service.
    
CANDIDATE DATA:
{candidates}

YOUR JOB:
For each candidate provided:
1. Extract the likely company name from the title or domain.
2. Ensure they sound like an SMB or startup (ignore if they seem like a job board, news site, or directory like Indeed, Greenhouse, TechCrunch).
3. Write a concise, compelling 1-2 sentence justification on exactly WHY DataVex should pitch {service_category} to them based on their search snippet.

Return STRICTLY a raw JSON object string with this exact structure (NO extra text, NO markdown code blocks, NO ```json wrapping):
{{
  "leads": [
    {{
      "name": "Company Name",
      "domain": "example.com",
      "why_we_help": "They are actively hiring for cloud infra but are a small team. DataVex can offer a fractional DevOps solution to get them to market faster."
    }}
  ]
}}
""")

    chain = prompt | llm | parser

    try:
        candidates_str = json.dumps(candidates, indent=2)
        llm_result = chain.invoke({
            "service_category": service_category,
            "candidates": candidates_str
        })
        
        # If the LLM still returns markdown, try to manually strip it if chain.invoke failed over to raw string
        if isinstance(llm_result, str):
            clean_str = llm_result.replace("```json", "").replace("```", "").strip()
            try:
                llm_result = json.loads(clean_str)
            except:
                pass

        qualified_leads = llm_result.get("leads", []) if isinstance(llm_result, dict) else []
        
        # Filter out junk the LLM might have kept
        valid_leads = [
            l for l in qualified_leads 
            if "indeed" not in l["domain"] and "linkedin" not in l["domain"] and "greenhouse" not in l["domain"]
        ]
        
        trace.append(f"Lead Analyst: Qualified {len(valid_leads)} high-potential leads for '{service_category}'")
        return {
            "leads": valid_leads,
            "agent_trace": trace
        }
    except Exception as e:
        trace.append(f"Lead Analyst: Synthesis failed - {e}")
        return {"leads": [], "agent_trace": trace}


# -----------------------------
# PHASE 5: OUTREACH GENERATOR
# -----------------------------
def draft_cold_email(company_name: str, domain: str, why_we_help: str, service_category: str) -> str:
    llm = ChatCerebras(
        model="llama3.1-8b",
        api_key=CEREBRAS_API_KEY
    )

    prompt = ChatPromptTemplate.from_template("""
You are a highly professional, top-performing Sales Development Rep (SDR) at DataVex.ai, a boutique tech agency from Mangaluru, India.
We specialize in {service_category}.

You need to write a short, punchy, high-converting cold email to the Founder or Head of Engineering at {company_name} ({domain}).
Here is why we identified them as a great lead: {why_we_help}

Write the email. Keep it under 150 words. Be professional, direct, and focused on solving their problem. 

CRITICAL RULES:
1. DO NOT guess or hallucinate the person's name (e.g., "Hi Rohit"). Use a professional greeting like "Hi {company_name} Team" or "Hi Founder" since we do not have their specific name.
2. Do not use placeholders like [Your Name] or [Link]. Just sign off as the "DataVex Team".

Return ONLY the email text, no subject line or extra conversational text.
""")

    chain = prompt | llm

    try:
        result = chain.invoke({
            "service_category": service_category,
            "company_name": company_name,
            "domain": domain,
            "why_we_help": why_we_help
        })
        return result.content.strip()
    except Exception as e:
        return f"Failed to generate outreach email. Error: {e}"


if __name__ == "__main__":
    print("🚀 DataVex SMB Intelligence Engine")
    domain = input("Enter company domain (e.g. acme.com): ").strip()
    res = run_intelligence(domain)
    print(json.dumps(res, indent=2))