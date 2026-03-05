"""Extract a short meta description from newsletter content."""


def generate_insights(items: list[dict], focus: str, max_items: int = 10) -> list[dict]:
    """
    Process each newsletter item through Claude and attach an 'insights' field.

    Args:
        items: List of newsletter dicts (source, title, content, url, published_at)
        focus: Instructions for what kind of insights to extract
        max_items: Maximum number of items to process (to manage API costs)

    Returns:
        The same list with an 'insights' key added to each processed item.
    """
    for item in items:
        content = item.get("content", "").strip()
        # Use first 200 chars of content as meta description
        item["insights"] = content[:200].rsplit(" ", 1)[0] + "…" if len(content) > 200 else content

    return items
