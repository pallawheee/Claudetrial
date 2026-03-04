# Newsletter Automation

Fetches newsletters from your inbox, RSS feeds, and websites — then sends a daily digest of AI-generated insights to `pallavi@unicornivc.com` at **10 AM IST**.

---

## Quick Start

### 1. Install dependencies

```bash
cd newsletter_automation
pip install -r requirements.txt
```

### 2. Set up credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | What it is |
|---|---|
| `GMAIL_APP_PASSWORD` | App password for `pallavi@unicornivc.com` — generate at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA) |
| `NEWSLETTER_INBOX_PASSWORD` | App password for the inbox where your newsletters arrive |
| `ANTHROPIC_API_KEY` | Your Claude API key from [console.anthropic.com](https://console.anthropic.com) |

### 3. Configure your sources

Edit `config.yaml` to add:
- **RSS feeds** under `rss_feeds.feeds`
- **Website URLs** to scrape under `websites.urls`
- **Newsletter inbox** details under `email.newsletter_inbox`

### 4. Test it immediately

```bash
python main.py --run-now
```

### 5. Start the daily scheduler

```bash
python main.py
```

This runs indefinitely, sending the digest every day at **10:00 AM IST**.

---

## Running as a background service (Linux)

### Using systemd

Create `/etc/systemd/system/newsletter-automation.service`:

```ini
[Unit]
Description=Newsletter Automation
After=network.target

[Service]
WorkingDirectory=/path/to/Claudetrial/newsletter_automation
ExecStart=/usr/bin/python3 main.py
Restart=always
EnvironmentFile=/path/to/Claudetrial/newsletter_automation/.env

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable newsletter-automation
sudo systemctl start newsletter-automation
```

### Using cron (alternative)

```bash
# Edit crontab
crontab -e

# Add this line to run at 10 AM IST (UTC+5:30 = 04:30 UTC)
30 4 * * * cd /path/to/Claudetrial/newsletter_automation && python3 main.py --run-now
```

---

## Project Structure

```
newsletter_automation/
├── main.py              # Main orchestrator & scheduler
├── processor.py         # Claude AI insight generation
├── sender.py            # Gmail SMTP email sender
├── config.yaml          # Your configuration (RSS feeds, URLs, settings)
├── .env                 # Credentials (never commit this)
├── .env.example         # Template for credentials
├── requirements.txt     # Python dependencies
└── fetchers/
    ├── email_fetcher.py # Fetch newsletters from IMAP inbox
    ├── rss_fetcher.py   # Fetch from RSS feeds
    └── web_fetcher.py   # Scrape specific websites
```

---

## Sample RSS Feeds to Get Started

```yaml
rss_feeds:
  enabled: true
  feeds:
    - name: "TechCrunch"
      url: "https://techcrunch.com/feed/"
    - name: "Harvard Business Review"
      url: "https://feeds.hbr.org/harvardbusiness"
    - name: "CB Insights Newsletter"
      url: "https://www.cbinsights.com/research/feed/"
    - name: "Axios Pro Rata"
      url: "https://www.axios.com/feeds/feed.rss"
    - name: "StrictlyVC"
      url: "https://strictlyvc.com/feed/"
```
