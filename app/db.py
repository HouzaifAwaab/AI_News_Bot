from dotenv import load_dotenv
import sqlite3
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join("keys", "keys.env"))

DB_PATH = os.getenv("DB_URL", "database/news.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT,
    weight INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS news_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    source_id TEXT REFERENCES sources(id),
    published TIMESTAMP,
    score REAL,
    impact INTEGER,
    summary TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent BOOLEAN DEFAULT 0,
    message_id INTEGER NULL,
    summary_lang TEXT
);
"""

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_source(source_id, name, weight=1, active=True):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sources (id, name, weight, active) VALUES (?, ?, ?, ?)",
            (source_id, name, weight, int(active))
        )
        conn.commit()

def is_source_active(source_id):
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT active FROM sources WHERE id = ?", (source_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else False
    except:
        return False

def is_duplicate_url(url, days=3):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM news_items WHERE url = ? AND processed_at > datetime('now', '-' || ? || ' days')",
            (url, days)
        )
        return cursor.fetchone() is not None

def add_news_item(url, title, source_id, published, score, impact, summary, summary_lang=None):
    if is_duplicate_url(url):
        return False
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO news_items (url, title, source_id, published, score, impact, summary, summary_lang) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (url, title, source_id, published, score, impact, summary, summary_lang)
        )
        conn.commit()
    return True

def mark_as_sent(news_id, message_id=None):
    with get_connection() as conn:
        if message_id:
            conn.execute("UPDATE news_items SET sent = 1, message_id = ? WHERE id = ?", (message_id, news_id))
        else:
            conn.execute("UPDATE news_items SET sent = 1 WHERE id = ?", (news_id,))
        conn.commit()

def get_news_reactions(news_id):
    try:
        with get_connection() as conn:
            cursor = conn.execute("SELECT reaction_type, COUNT(*) FROM news_reactions WHERE news_id = ? GROUP BY reaction_type", (news_id,))
            return cursor.fetchall()
    except:
        return []
