"""Use Claude AI to extract insights from newsletter content."""

import os
import anthropic


def _build_prompt(item: dict, focus: str) -> str:
    source = item.get("source", "Unknown")
    title = item.get("title", "Untitled")
    content = item.get("content", "")
    url = item.get("url", "")

    return f"""You are a research analyst extracting insights from newsletters for a venture capital investor.

Source: {source}
Title: {title}
URL: {url if url else "N/A"}

Content:
{content}

---

{focus}

Respond with a concise structured summary using these sections (skip any section if not applicable):
**Key Insights** – 3–5 bullet points of the most important takeaways
**Market Trends** – Notable trends or shifts mentioned
**Companies / Deals** – Any funding rounds, acquisitions, or notable company news
**Action Items** – Anything worth following up on

Keep the total response under 300 words. Be direct and specific."""


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
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[processor] ANTHROPIC_API_KEY not set — insights will be skipped.")
        for item in items:
            item["insights"] = "(AI insights unavailable — set ANTHROPIC_API_KEY)"
        return items

    client = anthropic.Anthropic(api_key=api_key)
    processed = items[:max_items]

    for i, item in enumerate(processed, 1):
        print(f"[processor] Generating insights for item {i}/{len(processed)}: {item['title'][:60]}")
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=600,
                messages=[
                    {"role": "user", "content": _build_prompt(item, focus)}
                ],
            )
            item["insights"] = message.content[0].text
        except Exception as exc:
            print(f"[processor] Error on item {i}: {exc}")
            item["insights"] = f"(Error generating insights: {exc})"

    # Items beyond max_items get a note
    for item in items[max_items:]:
        item["insights"] = "(Skipped — exceeded max_items limit)"

    return items
