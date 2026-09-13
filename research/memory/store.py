import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/raseen_memory.db")


def connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source_url TEXT,
            status TEXT DEFAULT 'new',
            decision TEXT,
            decision_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    return connection


def remember(memory_type, title, content, source_url=None, status="new", decision=None, decision_reason=None):
    connection = connect()
    connection.execute(
        """
        INSERT INTO memories
        (memory_type, title, content, source_url, status, decision, decision_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (memory_type, title, content, source_url, status, decision, decision_reason)
    )
    connection.commit()
    connection.close()


def recall(limit=10):
    connection = connect()
    cursor = connection.execute(
        """
        SELECT id, memory_type, title, content, source_url, status, decision, decision_reason, created_at
        FROM memories
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )
    memories = cursor.fetchall()
    connection.close()
    return memories


def search_memory(query, limit=10):
    connection = connect()
    cursor = connection.execute(
        """
        SELECT id, memory_type, title, content, source_url, status, decision, decision_reason, created_at
        FROM memories
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (f"%{query}%", f"%{query}%", limit)
    )
    memories = cursor.fetchall()
    connection.close()
    return memories


def memory_exists(title):
    connection = connect()
    cursor = connection.execute(
        "SELECT id FROM memories WHERE title = ?",
        (title,)
    )
    row = cursor.fetchone()
    connection.close()
    return row is not None