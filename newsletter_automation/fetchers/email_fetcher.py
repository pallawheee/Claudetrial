"""Fetch newsletter emails from an IMAP inbox."""

import imaplib
import email
import os
from datetime import datetime, timedelta
from email.header import decode_header
from typing import Optional


def _decode_str(value: str | bytes, charset: Optional[str] = None) -> str:
    if isinstance(value, bytes):
        return value.decode(charset or "utf-8", errors="replace")
    return value


def _extract_body(msg: email.message.Message) -> str:
    """Extract plain text or HTML body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="replace")
                break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="replace")
    return body


def fetch_newsletter_emails(config: dict) -> list[dict]:
    """
    Connect to IMAP inbox and fetch newsletter emails from the last 24 hours.

    Args:
        config: The 'email.newsletter_inbox' section of config.yaml

    Returns:
        List of dicts with keys: source, title, content, url, published_at
    """
    if not config.get("enabled", False):
        return []

    inbox_password = os.getenv("NEWSLETTER_INBOX_PASSWORD", "")
    if not inbox_password:
        print("[email_fetcher] NEWSLETTER_INBOX_PASSWORD not set — skipping email fetch.")
        return []

    imap_host = config["imap_host"]
    imap_port = config.get("imap_port", 993)
    inbox_email = config["email"]
    filter_senders = config.get("filter_senders", [])
    filter_keywords = config.get("filter_subject_keywords", [])

    results = []
    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(inbox_email, inbox_password)
        mail.select("INBOX")

        # Search for emails from the last 24 hours
        since_date = (datetime.utcnow() - timedelta(days=1)).strftime("%d-%b-%Y")
        _, message_ids = mail.search(None, f'(SINCE "{since_date}")')

        ids = message_ids[0].split() if message_ids[0] else []
        print(f"[email_fetcher] Found {len(ids)} emails since {since_date}.")

        for msg_id in ids:
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            # Decode subject and sender
            subject_parts = decode_header(msg.get("Subject", ""))
            subject = " ".join(_decode_str(p, enc) for p, enc in subject_parts)
            sender = msg.get("From", "")

            # Apply sender filter
            if filter_senders and not any(s.lower() in sender.lower() for s in filter_senders):
                continue

            # Apply subject keyword filter
            if filter_keywords and not any(kw.lower() in subject.lower() for kw in filter_keywords):
                continue

            body = _extract_body(msg)
            if not body.strip():
                continue

            results.append({
                "source": f"Email: {sender}",
                "title": subject,
                "content": body[:8000],  # Truncate to keep token usage manageable
                "url": None,
                "published_at": msg.get("Date", ""),
            })

        mail.logout()
        print(f"[email_fetcher] Fetched {len(results)} newsletters from inbox.")
    except Exception as exc:
        print(f"[email_fetcher] Error: {exc}")

    return results
