# 🔍 AI Research Agent

A full-stack AI agent that autonomously searches the web, scrapes pages in parallel, and synthesizes research answers using Claude AI — with real-time streaming responses.

**Live demo:** https://web-production-7876f.up.railway.app

## What it does
- Takes a research question from the user
- Plans a research approach using Claude
- Searches the web via SerpAPI
- Scrapes multiple pages simultaneously (async)
- Streams a synthesized answer word-by-word with source citations

## Tech Stack
- **AI:** Anthropic Claude API (claude-sonnet-4-6)
- **Backend:** FastAPI + Python
- **Scraping:** httpx + BeautifulSoup (async/parallel)
- **Search:** SerpAPI
- **Streaming:** Server-Sent Events (SSE)
- **Deployment:** Railway

## Architecture
User → FastAPI → Search Tool → Async Scraper → Claude LLM → SSE Stream → Frontend

## Run locally
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env  # add your API keys
uvicorn main:app --reload
```

## Environment variables
ANTHROPIC_API_KEY=your_key

SERPAPI_KEY=your_key
