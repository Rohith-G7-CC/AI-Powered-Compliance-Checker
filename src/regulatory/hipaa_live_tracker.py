# src/regulatory/hipaa_live_tracker.py
 
import feedparser
import json
import hashlib
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# CONFIG
HIPAA_RSS_URL = "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164"
HIPAA_FALLBACK_URL = "https://www.hhs.gov/hipaa/for-professionals/security/index.html"

LOCAL_FEED_FILE = Path("data/regulations/hipaa_feed_snapshot.json")
LOCAL_FEED_FILE.parent.mkdir(parents=True, exist_ok=True)


# FETCHERS
def fetch_from_rss():
    feed = feedparser.parse(HIPAA_RSS_URL)
    updates = []

    for entry in feed.entries:
        updates.append({
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", "")
        })

    return updates


def fetch_by_scraping():
    try:
        response = requests.get(HIPAA_FALLBACK_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(separator=" ", strip=True)[:800]

        return [{
            "title": "HIPAA Security Rule Update",
            "summary": text,
            "link": HIPAA_FALLBACK_URL,
            "published": "Refer official website"
        }]

    except Exception as e:
        print("HIPAA scraping failed:", e)
        return []


# SNAPSHOT HELPERS
def hash_updates(updates):
    payload = json.dumps(updates, sort_keys=True).encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def load_previous_snapshot():
    if not LOCAL_FEED_FILE.exists():
        return None, None

    with open(LOCAL_FEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("updates"), data.get("hash")


def save_snapshot(updates, hash_value):
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "updates": updates,
        "hash": hash_value
    }

    with open(LOCAL_FEED_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    return snapshot


# CORE DETECTOR
def detect_hipaa_changes():
    updates = fetch_from_rss()
    source = "rss"

    if not updates:
        print("RSS empty → switching to scraping")
        updates = fetch_by_scraping()
        source = "scraping"

    latest_hash = hash_updates(updates)
    prev_updates, prev_hash = load_previous_snapshot()

    if prev_hash is None:
        save_snapshot(updates, latest_hash)
        return {
            "has_new_updates": True,
            "new_entries": updates,
            "message": "Initial HIPAA dataset stored."
        }

    if prev_hash == latest_hash:
        return {
            "has_new_updates": False,
            "new_entries": [],
            "message": "No new HIPAA regulatory updates."
        }

    prev_titles = {u["title"] for u in prev_updates}
    new_entries = [u for u in updates if u["title"] not in prev_titles]

    save_snapshot(updates, latest_hash)

    return {
        "has_new_updates": len(new_entries) > 0,
        "new_entries": new_entries,
        "message": f"{len(new_entries)} new HIPAA updates detected."
    }


if __name__ == "__main__":
    print(json.dumps(detect_hipaa_changes(), indent=2))
