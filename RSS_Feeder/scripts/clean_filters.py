import re
from bs4 import BeautifulSoup
from config.keywords import KEYWORDS

def clean_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def is_relevant(text):
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def clean_and_filter(entries):
    cleaned = []

    for e in entries:
        title = clean_html(e["title"])
        summary = clean_html(e["summary"])

        full_text = f"{title} {summary}"

        if is_relevant(full_text):
            cleaned.append({
                "title": title.strip(),
                "summary": summary.strip(),
                "link": e["link"],
                "published": e["published"]
            })

    return cleaned
