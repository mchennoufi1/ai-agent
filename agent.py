import anthropic
import os
import json
from dotenv import load_dotenv
from tools.search import search_web
from tools.scraper import scrape_pages

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_claude(prompt: str, system: str = None) -> str:
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
    print(f"[Agent] Planning research for: {query}")
    plan = ask_claude(
        f"Break this research task into 2-3 clear steps: {query}",
        system="You are a research planning assistant. Be concise."
    )
    print(f"[Agent] Plan:\n{plan}\n")

    print("[Agent] Searching the web...")
    sources = search_web(query)
    print(f"[Agent] Found {len(sources)} sources")

    print("[Agent] Scraping all pages in parallel...")
    urls = [s["url"] for s in sources]
    contents = scrape_pages(urls)

    all_content = ""
    for source, content in zip(sources, contents):
        print(f"[Agent] ✓ Scraped: {source['url']}")
        all_content += f"\n\n--- Source: {source['title']} ({source['url']}) ---\n{content}"

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


def reasoning_agent_stream(query: str):
    """Streaming version — yields text chunks as Claude generates them."""

    # Step 1: Plan
    plan = ask_claude(
        f"Break this research task into 2-3 clear steps: {query}",
        system="You are a research planning assistant. Be concise."
    )

    # Step 2: Search
    sources = search_web(query)

    # Step 3: Scrape all pages simultaneously
    urls = [s["url"] for s in sources]
    contents = scrape_pages(urls)

    all_content = ""
    for source, content in zip(sources, contents):
        all_content += f"\n\n--- Source: {source['title']} ({source['url']}) ---\n{content}"

    # Step 4: Stream the synthesis
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

    yield f"data: {json.dumps({'type': 'plan', 'content': plan})}\n\n"
    yield f"data: {json.dumps({'type': 'sources', 'content': sources})}\n\n"

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are an expert research synthesizer.",
        messages=[{"role": "user", "content": final_prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {json.dumps({'type': 'token', 'content': text})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"