# DataVex Autonomous Intelligence Engine

DataVex is an autonomous, agentic lead generation and intelligence engine designed specifically for boutique tech agencies and consulting firms. Instead of relying on manual prospecting, DataVex autonomously hunts for high-quality Small and Medium Business (SMB) leads based on the specific services you want to pitch.

## 🚀 Key Features

*   **Autonomous Lead Scouting**: Select a service category (e.g., *Cloud & DevOps*, *AI & Data Analytics*), and the engine actively searches the open web and job markets for startups actively signaling a need for that service.
*   **Deterministic Enterprise Filtering**: Built-in hard-coded and Regex-based blockers instantly filter out Fortune 500 companies, massive tech giants, and publicly traded enterprises, saving API costs and focusing solely on true SMBs and startups.
*   **AI-Powered Qualification**: Uses Cerebras infrastructure (`llama3.1-8b`) to parse search snippets, correctly identify the startup, and generate a customized, 1-2 sentence compelling pitch justifying exactly *why* DataVex should reach out to them.
*   **Modern React UI**: A sleek, futuristic glassmorphism interface built with Vite, React, and Tailwind CSS.
*   **Real-time Agent Tracing**: See the actual thought process and steps the AI agents are taking in real-time within the UI.

## 🏗️ Architecture

The project is split into a Python backend and a React frontend.

### Backend (`fast_app.py` & `agents.py`)
*   **FastAPI**: Provides a high-performance asynchronous API for the frontend.
*   **Agentic Pipeline**:
    *   **Lead Scout (SerpAPI)**: Executes highly specific Google Dork queries designed to find startups and explicitly exclude noisy job boards (like Indeed, Greenhouse, etc.).
    *   **Size Guard**: A deterministic filter to drop large companies.
    *   **Lead Analyst (Langchain + Cerebras)**: A high-speed LLM that extracts valid leads, formats them into strict JSON, and writes personalized strategy pitches.

### Frontend (`frontend/`)
*   **Vite + React**: Lightning-fast local development and optimized production builds.
*   **Tailwind CSS**: Utility-first styling with custom glassmorphic and glow effects.
*   **Framer Motion**: Smooth, dynamic animations for the UI state transitions and the tracing terminal.

## ⚙️ Setup & Installation

### Prerequisites
*   Python 3.10+
*   Node.js 18+

### 1. Environment Variables
Create a `.env` file in the root directory (where `fast_app.py` is located) and add your API keys:

```env
SERPAPI_API_KEY=your_serpapi_key_here
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

### 2. Backend Setup
Navigate to the project root and create a virtual environment:

```bash
# Create and activate virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn requests beautifulsoup4 python-dotenv langchain-cerebras google-search-results
```

Run the backend server:
```bash
python -m uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
Open a new terminal and navigate to the `frontend` folder:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:5173`.

## 🧠 How the AI Agents Work

1.  **Query Generation**: Based on your selection (e.g., "AI & Data Analytics"), the backend constructs a specific boolean search query like: 
    *`startup 'looking for data science consultant' OR 'we need machine learning' 'small team' -jobs -job -site:linkedin.com -site:indeed.com`*
2.  **Scraping**: Fetches the top 20 Google results.
3.  **Parsing & Normalization**: Strips URLs down to their root domains.
4.  **Prescreening**: Checks the domain against `ENTERPRISE_BLOCKLIST`.
5.  **LLM Synthesis**: Passes the top ~5 surviving candidates to the Cerebras LLM. The LLM is strictly instructed via a Langchain Prompt Template to generate a JSON response containing the company name, domain, and a custom pitch strategy.
6.  **Delivery**: The frontend receives the JSON and renders it into the target campaign focus grid.

## 🛠️ Tech Stack
*   **Frontend**: React, Vite, Tailwind CSS, Lucide React, Framer Motion, Axios.
*   **Backend**: Python, FastAPI, Uvicorn, LangChain, SerpAPI ecosystem.
*   **Models**: Cerebras (`llama3.1-8b` for extreme speed and low latency inference).