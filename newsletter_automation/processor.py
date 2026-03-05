"""Extract a short meta description from newsletter content."""

import re


def _strip_html(text: str) -> str:
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    # Filter out CSS-looking lines line by line
    clean = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Skip CSS at-rules (@media, @keyframes, etc.), selectors, declarations, braces
        if re.match(r'^[@.#\*]|^\}|^\{', s):
            continue
        # Skip CSS property declarations (e.g. "font-size: 14px") — no uppercase in first 20 chars
        if re.match(r'^[a-z][\w-]+\s*:', s) and not re.search(r'[A-Z]', s[:20]):
            continue
        clean.append(s)
    text = " ".join(clean)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_insights(items: list[dict], focus: str, max_items: int = 10) -> list[dict]:
    for item in items:
        content = _strip_html(item.get("content", "")).strip()
        item["insights"] = content[:200].rsplit(" ", 1)[0] + "…" if len(content) > 200 else content

    return items
