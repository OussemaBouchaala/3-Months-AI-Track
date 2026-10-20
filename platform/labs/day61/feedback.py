# Thumbs up / down on every answer. Cheap to collect, and the thumbs-down list is next week's error analysis.
# SQLite: one file, no server, in the standard library.
import json
import sqlite3
from datetime import datetime

SCHEMA = """CREATE TABLE IF NOT EXISTS feedback (
    request_id TEXT PRIMARY KEY,
    rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
    comment TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
)"""


def init_db(conn):
    """Create the table (SCHEMA) and commit."""
    # TODO
    ...


def record(conn, request_id, rating, comment="", now=None):
    """Validate: rating must be 1 or -1, comment at most 500 chars (else ValueError). Insert, or replace an earlier
    rating for the same request_id (the agent changed their mind). created_at = (now or datetime.now()) in ISO
    format, seconds precision. Use ? placeholders, never f-strings in SQL. Commit."""
    # TODO
    ...


def stats(conn, since=None):
    """{"up": n, "down": n, "rate": up / (up + down) rounded to 3, or None if no feedback}.
    since: an ISO date string "2026-12-01"; count only rows with created_at >= since."""
    # TODO
    ...


def by_day(conn):
    """[(day "YYYY-MM-DD", up, down), ...] sorted by day."""
    # TODO
    ...


def export_negatives(conn, path, lookup):
    """Write one JSON line per thumbs-down, oldest first: {"request_id", "comment", "created_at", **lookup(request_id)}
    (lookup returns {"question", "answer", "sources"} from your logs, or {} if unknown). ensure_ascii=False.
    Return the number of lines written."""
    # TODO
    ...


if __name__ == "__main__":
    conn = sqlite3.connect("feedback.db")
    init_db(conn)
    record(conn, "demo-1", 1)
    record(conn, "demo-2", -1, "cite le mauvais contrat")
    print(stats(conn), by_day(conn))
    print(export_negatives(conn, "negatives.jsonl", lambda rid: {}), "negatives exported")
    # In chat_endpoint.py: POST /feedback {request_id, rating, comment} -> record(...); 422 on ValueError.
