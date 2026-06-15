import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str, num_results: int = 3) -> list[dict]:
    """Search the web and return top URLs with titles."""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY"),
        "num": num_results
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    results = response.json()

    links = [
        {"url": r["link"], "title": r.get("title", "")}
        for r in results.get("organic_results", [])[:num_results]
    ]
    return links
