"""
database.py
-----------
Handles all SQLite operations: creating the table, saving a meeting
record, and retrieving meeting history.

We store the action_items and key_decisions lists as JSON strings
inside the SQLite TEXT columns, since SQLite has no native list type.
"""

import sqlite3
import json
import datetime
from config import DATABASE_PATH


def _get_connection():
    """Open a new connection to the SQLite database file."""
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    """
    Create the meetings table if it doesn't already exist.
    Should be called once when the app starts.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TEXT,
            transcript TEXT,
            summary TEXT,
            mom TEXT,
            action_items TEXT,
            key_decisions TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_meeting(title: str, transcript: str, insights: dict) -> int:
    """
    Insert a new meeting record into the database.

    Args:
        title: a short title for the meeting (e.g. auto-generated from date).
        transcript: the full raw transcript text.
        insights: dict with keys summary, mom, action_items, key_decisions
                   (as returned by summarizer.generate_meeting_insights).

    Returns:
        The id of the newly inserted row.
    """
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meetings (title, created_at, transcript, summary, mom, action_items, key_decisions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        datetime.datetime.now().isoformat(timespec="seconds"),
        transcript,
        insights.get("summary", ""),
        insights.get("mom", ""),
        json.dumps(insights.get("action_items", [])),
        json.dumps(insights.get("key_decisions", [])),
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_meetings() -> list[dict]:
    """
    Fetch all saved meetings, most recent first.

    Returns:
        A list of dicts, each representing one meeting row, with
        action_items and key_decisions decoded back into Python lists.
    """
    conn = _get_connection()
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    meetings = []
    for row in rows:
        meetings.append({
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "transcript": row["transcript"],
            "summary": row["summary"],
            "mom": row["mom"],
            "action_items": json.loads(row["action_items"]),
            "key_decisions": json.loads(row["key_decisions"]),
        })
    return meetings
