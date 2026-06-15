import anthropic
import os
from dotenv import load_dotenv
from tools.search import search_web
from tools.scraper import scrape_pages

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_claude(prompt: str, system: str = None) -> str:
    """Send a prompt to Claude and return the response."""
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text


def reasoning_agent(query: str) -> dict:
    """
    Multi-step agent:
    1. Plan the research approach
    2. Search the web
    3. Scrape all pages simultaneously (async)
    4. Synthesize a final answer with sources
    """

    # Step 1: Plan
    print(f"[Agent] Planning research for: {query}")
    plan = ask_claude(
        f"Break this research task into 2-3 clear steps: {query}",
        system="You are a research planning assistant. Be concise."
    )
    print(f"[Agent] Plan:\n{plan}\n")

    # Step 2: Search
    print("[Agent] Searching the web...")
    sources = search_web(query)
    print(f"[Agent] Found {len(sources)} sources")

    # Step 3: Scrape all pages simultaneously
    print("[Agent] Scraping all pages in parallel...")
    urls = [s["url"] for s in sources]
    contents = scrape_pages(urls)  # all at once

    all_content = ""
    for source, content in zip(sources, contents):
        print(f"[Agent] ✓ Scraped: {source['url']}")
        all_content += f"\n\n--- Source: {source['title']} ({source['url']}) ---\n{content}"

    # Step 4: Synthesize
    print("[Agent] Synthesizing answer...")
    final_prompt = f"""
You are a research assistant. Use the information below to answer the question.
Include citations referencing the source titles when you use information from them.

Research Plan:
{plan}

Gathered Information:
{all_content}

Question: {query}

Provide a well-structured answer with source citations.
"""

    answer = ask_claude(final_prompt, system="You are an expert research synthesizer.")

    return {
        "answer": answer,
        "sources": sources,
        "plan": plan
    }