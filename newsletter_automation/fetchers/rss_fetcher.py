"""Fetch articles from RSS feeds."""

from datetime import datetime, timedelta, timezone

import feedparser


def fetch_rss_feeds(config: dict) -> list[dict]:
    """
    Fetch recent entries from configured RSS feeds.

    Args:
        config: The 'rss_feeds' section of config.yaml

    Returns:
        List of dicts with keys: source, title, content, url, published_at
    """
    if not config.get("enabled", False):
        return []

    feeds = config.get("feeds") or []
    if not feeds:
        print("[rss_fetcher] No RSS feeds configured.")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    results = []

    for feed_cfg in feeds:
        name = feed_cfg.get("name", feed_cfg.get("url", "Unknown"))
        url = feed_cfg.get("url")
        if not url:
            continue

        try:
            parsed = feedparser.parse(url)
            entries_added = 0
            for entry in parsed.entries:
                # Parse published date
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue

                content = ""
                if hasattr(entry, "content"):
                    content = entry.content[0].value
                elif hasattr(entry, "summary"):
                    content = entry.summary

                results.append({
                    "source": f"RSS: {name}",
                    "title": entry.get("title", "No title"),
                    "content": content[:8000],
                    "url": entry.get("link"),
                    "published_at": entry.get("published", ""),
                })
                entries_added += 1

            print(f"[rss_fetcher] {name}: {entries_added} new entries.")
        except Exception as exc:
            print(f"[rss_fetcher] Error fetching '{name}' ({url}): {exc}")

    return results
