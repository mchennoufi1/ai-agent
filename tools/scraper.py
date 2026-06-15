import httpx
import asyncio
from bs4 import BeautifulSoup

async def scrape_page_async(url: str, char_limit: int = 3000) -> str:
    """Scrape a single page asynchronously."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)

        return text[:char_limit]

    except Exception as e:
        return f"[Could not scrape {url}: {e}]"


async def scrape_all_async(urls: list[str]) -> list[str]:
    """Scrape all URLs simultaneously."""
    tasks = [scrape_page_async(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return list(results)


def scrape_pages(urls: list[str]) -> list[str]:
    """Sync wrapper — call this from non-async code."""
    return asyncio.run(scrape_all_async(urls))