"""
Newsletter Automation — Main Orchestrator
Fetches newsletters, generates AI insights, and sends a daily digest at 10 AM IST.

Usage:
    python main.py               # Start the scheduler (runs daily at 10 AM IST)
    python main.py --run-now     # Run immediately (for testing)
"""

import argparse
import os
import sys
import time

import schedule
import yaml
from dotenv import load_dotenv

from fetchers.email_fetcher import fetch_newsletter_emails
from fetchers.rss_fetcher import fetch_rss_feeds
from fetchers.web_fetcher import fetch_websites
from processor import generate_insights
from sender import send_digest


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict) -> None:
    print("\n" + "=" * 60)
    print("Newsletter Automation — Starting pipeline")
    print("=" * 60)

    # ── Step 1: Fetch from all sources ───────────────────────────────
    all_items: list[dict] = []

    email_cfg = config.get("email", {}).get("newsletter_inbox", {})
    all_items += fetch_newsletter_emails(email_cfg)

    rss_cfg = config.get("rss_feeds", {})
    all_items += fetch_rss_feeds(rss_cfg)

    web_cfg = config.get("websites", {})
    all_items += fetch_websites(web_cfg)

    print(f"\n[main] Total items collected: {len(all_items)}")

    if not all_items:
        print("[main] No newsletter content found. Check your sources in config.yaml.")

    # ── Step 2: Generate AI insights ─────────────────────────────────
    insights_cfg = config.get("insights", {})
    focus = insights_cfg.get("focus", "Extract the key insights from this newsletter.")
    max_items = insights_cfg.get("max_items", 10)

    processed = generate_insights(all_items, focus=focus, max_items=max_items)

    # ── Step 3: Send the digest ───────────────────────────────────────
    email_cfg_main = config.get("email", {})
    sender = email_cfg_main.get("sender_email", "")
    recipient = email_cfg_main.get("recipient_email", "")

    if not sender or not recipient:
        print("[main] ERROR: sender_email or recipient_email not set in config.yaml")
        sys.exit(1)

    send_digest(processed, sender_email=sender, recipient_email=recipient)

    print("\n[main] Pipeline complete.")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Newsletter Automation")
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run the pipeline immediately instead of waiting for 10 AM IST",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the configuration file (default: config.yaml)",
    )
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv()

    config_path = args.config
    if not os.path.exists(config_path):
        print(f"[main] ERROR: Config file not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path)

    if args.run_now:
        run_pipeline(config)
        return

    # ── Scheduler: run daily at 10:00 AM IST ─────────────────────────
    send_time = config.get("scheduler", {}).get("send_time", "10:00")
    print(f"[main] Scheduler started. Will run daily at {send_time} IST.")
    print("[main] Press Ctrl+C to stop.\n")

    schedule.every().day.at(send_time).do(run_pipeline, config=config)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
