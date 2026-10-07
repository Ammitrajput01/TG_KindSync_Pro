import sys
import pytest
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from devi.operator.telegram_bot import DeviTelegramBot
from devi.operator.group_scanner import init_tables, get_topic_icon

def test_clean_topics_indexing_and_phantom_exclusion(tmp_path):
    # Setup test DB
    test_db = tmp_path / "test_history.sqlite"
    conn = sqlite3.connect(test_db)
    init_tables(conn)
    
    chat_id = -100999888777
    
    # Insert legitimate topics
    conn.execute("INSERT INTO telegram_group_topics (chat_id, topic_id, topic_title) VALUES (?, ?, ?)", (chat_id, 10, "Pharmacology Basics"))
    conn.execute("INSERT INTO telegram_group_topics (chat_id, topic_id, topic_title) VALUES (?, ?, ?)", (chat_id, 20, "Pathology Notes"))
    
    # Insert phantom topics
    conn.execute("INSERT INTO telegram_group_topics (chat_id, topic_id, topic_title) VALUES (?, ?, ?)", (chat_id, 22885, "Topic #22885"))
    conn.execute("INSERT INTO telegram_group_topics (chat_id, topic_id, topic_title) VALUES (?, ?, ?)", (chat_id, 24036, "Topic #24036"))
    conn.commit()
    
    # Run init_tables cleanup
    init_tables(conn)
    
    rows = conn.execute("SELECT topic_id, topic_title FROM telegram_group_topics WHERE chat_id = ?", (chat_id,)).fetchall()
    topic_titles = [r[1] for r in rows]
    
    assert "Topic #22885" not in topic_titles
    assert "Topic #24036" not in topic_titles
    assert "Pharmacology Basics" in topic_titles
    assert "Pathology Notes" in topic_titles
    conn.close()

def test_bot_get_topics_filters_phantom_topics():
    bot = DeviTelegramBot()
    topics = bot._get_topics(-1003912970546)
    for t in topics:
        assert not t["topic_title"].startswith("Topic #"), f"Phantom topic found: {t['topic_title']}"
