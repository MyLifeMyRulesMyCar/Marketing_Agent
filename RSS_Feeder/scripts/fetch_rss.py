import feedparser
from datetime import datetime
import json
import os

FEEDS = [
    "https://www.tomshardware.com/feeds.xml",
    "https://www.cnx-software.com/feed/"
]

def fetch_all():
    all_entries = []

    for url in FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            all_entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", "")
            })

    # Save raw data
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("data/raw", exist_ok=True)

    with open(f"data/raw/rss_{today}.json", "w") as f:
        json.dump(all_entries, f, indent=2)

    return all_entries
