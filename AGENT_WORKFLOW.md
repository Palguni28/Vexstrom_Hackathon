# DataVex Intelligence Engine: Technical Summary

This document provides a complete summary of the technology stack, AI models, autonomous agents, and the end-to-end workflow powering the DataVex Intelligence Engine.

## 🛠️ Frameworks & Tech Stack
*   **Frontend**: Built with **React** using **Vite** for incredibly fast compilation. The UI uses **Tailwind CSS** for modern glassmorphic styling and **Framer Motion** for smooth, dynamic terminal and card animations.
*   **Backend**: Powered by **FastAPI** (Python) and **Uvicorn**, providing a high-performance, asynchronous REST API to handle the AI processing without blocking the main server threads.

## 🧠 AI Models Used
*   **Cerebras (`llama3.1-8b`)**: We are using the LLaMA 3.1 8B parameter model hosted on Cerebras's ultra-fast API infrastructure. This model was chosen because it provides near-instantaneous inference speeds, which is critical for making the web app feel responsive while generating complex JSON and emails.
*   **LangChain**: Used to orchestrate the prompt templates, parsers, and chains that interact with the LLM.

## 🤖 The Autonomous Agents
The system orchestrates a team of specialized agents to find and convert leads:

1.  **Lead Scout (Search Agent)**: Uses **SerpAPI** to execute advanced Google Dork boolean queries. It intentionally searches for startups talking about their tech stack or hiring challenges while strictly filtering out (negating) giant job boards like Indeed, Greenhouse, or Glassdoor.
2.  **Size Guard (Deterministic Filter)**: A hard-coded logic guard that cross-references all found domains against an `ENTERPRISE_BLOCKLIST`. It instantly kills leads belonging to Fortune 500 companies or massive tech giants to save API costs and ensure only SMBs make it through.
3.  **Lead Analyst (LLM Synthesizer)**: The primary LangChain agent. It feeds all surviving candidates to the Cerebras LLaMA model and instructs it to evaluate the startup, verify it matches DataVex's ICP (Ideal Customer Profile), and write a customized 1-2 sentence pitch strategy describing *why* DataVex should help them.
4.  **Sales Development Rep (SDR Agent)**: A secondary LLM agent triggered by the "Draft Email" button. It takes the context gathered by the Lead Analyst and writes a highly professional, 150-word cold outreach email directed at the company's Founder or Head of Engineering.

## 🔄 End-to-End Workflow

1.  **Trigger**: The user selects a target campaign category (e.g., "Cloud & DevOps") on the React frontend and hits "Find SMB Leads".
2.  **Scouting**: The FastAPI backend receives the request and the **Lead Scout** runs Google searches for startups explicitly mentioning cloud infra challenges.
3.  **Filtering**: The results are cleaned, URLs are normalized, and the **Size Guard** removes any unqualified or massive enterprise domains.
4.  **Synthesis**: The top surviving candidates are sent to the **Lead Analyst** (Cerebras LLM), which formats the messy search data into clean JSON containing the startup name, domain, and a tailored pitch strategy.
5.  **Display**: The React UI renders these qualified leads as interactive glass cards.
6.  **Action**: The user clicks "Draft Email" on a specific card, triggering the **SDR Agent** to instantly generate a ready-to-send cold email. The user clicks "Copy" and sends it!
