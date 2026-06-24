import json
import os
import re
import requests
from bs4 import BeautifulSoup

CHANNEL_URL = "https://vkvideo.ru/@theprankvideo"

KEYWORDS = [
    "трей",
    "трэй",
    "лана"
]

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

SEEN_FILE = "seen.json"


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False
        },
        timeout=30
    )


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f)["videos"])


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"videos": sorted(list(seen))},
            f,
            ensure_ascii=False,
            indent=2
        )


def get_titles():
    headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
    }

    html = requests.get(
        CHANNEL_URL,
        headers=headers,
        timeout=30
    ).text

    soup = BeautifulSoup(html, "html.parser")

    titles = set()

    for tag in soup.find_all(attrs={"aria-label": True}):
        title = tag["aria-label"].strip()

        if len(title) < 10:
            continue

        titles.add(title)

    return titles


def keyword_match(title):
    title = title.lower()
    return any(word in title for word in KEYWORDS)


def main():
    seen = load_seen()

    titles = get_titles()

    new_titles = titles - seen

    for title in sorted(new_titles):
        if keyword_match(title):
            send_message(
                "Найден новый выпуск:\n\n"
                f"{title}\n\n"
                f"{CHANNEL_URL}"
            )

    seen.update(titles)
    save_seen(seen)


if __name__ == "__main__":
    main()
