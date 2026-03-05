"""Extract a short meta description from newsletter content."""

import re


def _strip_html(text: str) -> str:
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    # Strip CSS blocks (from plain-text emails that embed CSS)
    text = re.sub(r"@[a-zA-Z][\w-]*[^{]*\{[^{}]*(\{[^{}]*\}[^{}]*)*\}", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_insights(items: list[dict], focus: str, max_items: int = 10) -> list[dict]:
    for item in items:
        content = _strip_html(item.get("content", "")).strip()
        item["insights"] = content[:200].rsplit(" ", 1)[0] + "…" if len(content) > 200 else content

    return items
