"""Scrape newsletter content from specific website URLs."""

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; NewsletterBot/1.0; "
        "+https://github.com/pallawheee/Claudetrial)"
    )
}

# Tags whose content we discard during scraping
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form"}


def _scrape_url(url: str) -> str:
    """Fetch a URL and return the main visible text content."""
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise elements
    for tag in soup(SKIP_TAGS):
        tag.decompose()

    # Prefer <article> or <main>, fall back to <body>
    container = soup.find("article") or soup.find("main") or soup.body
    if not container:
        return ""

    text = container.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines)[:8000]


def fetch_websites(config: dict) -> list[dict]:
    """
    Scrape content from configured website URLs.

    Args:
        config: The 'websites' section of config.yaml

    Returns:
        List of dicts with keys: source, title, content, url, published_at
    """
    if not config.get("enabled", False):
        return []

    urls = config.get("urls") or []
    if not urls:
        print("[web_fetcher] No website URLs configured.")
        return []

    results = []
    for entry in urls:
        name = entry.get("name", entry.get("url", "Unknown"))
        url = entry.get("url")
        if not url:
            continue

        try:
            content = _scrape_url(url)
            if not content:
                print(f"[web_fetcher] No content scraped from '{name}'.")
                continue

            results.append({
                "source": f"Web: {name}",
                "title": name,
                "content": content,
                "url": url,
                "published_at": "",
            })
            print(f"[web_fetcher] Scraped {len(content)} chars from '{name}'.")
        except Exception as exc:
            print(f"[web_fetcher] Error scraping '{name}' ({url}): {exc}")

    return results
