import sqlite3

def init_db():
    conn = sqlite3.connect("db/news.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        summary TEXT,
        link TEXT,
        published TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_news(entries):
    conn = sqlite3.connect("db/news.db")
    c = conn.cursor()

    for e in entries:
        try:
            c.execute("""
            INSERT INTO news (title, summary, link, published)
            VALUES (?, ?, ?, ?)
            """, (e["title"], e["summary"], e["link"], e["published"]))
        except:
            pass  # ignore duplicates

    conn.commit()
    conn.close()
