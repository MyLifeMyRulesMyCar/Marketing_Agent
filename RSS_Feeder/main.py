from scripts.fetch_rss import fetch_all
from scripts.clean_filters import clean_and_filter
from scripts.deduplicate import remove_duplicates
from scripts.store import init_db, save_news

def run_pipeline():
    raw = fetch_all()
    cleaned = clean_and_filter(raw)
    unique = remove_duplicates(cleaned)

    init_db()
    save_news(unique)

    print(f"Saved {len(unique)} filtered articles")

if __name__ == "__main__":
    run_pipeline()
