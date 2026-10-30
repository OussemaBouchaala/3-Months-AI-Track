"""Thumbs up / down on every answer. Cheap to collect, and the thumbs-down list is next
week's error analysis.

SQLite stores it: one file, no server, in Python's standard library.

1. `SCHEMA` and `init_db`: the table, with rules the database itself enforces.
2. `record`: save a rating (safely: `?` placeholders).
3. `stats` and `by_day`: the numbers for your weekly check.
4. `export_negatives`: every thumbs-down with its question and answer, for error analysis.
"""
import json
import sqlite3
from datetime import datetime

# One row per answer (request_id is the X-Request-ID from day 55). CHECK makes the
# database itself refuse a rating that isn't -1 or 1, whatever the code does.
SCHEMA = """CREATE TABLE IF NOT EXISTS feedback (
    request_id TEXT PRIMARY KEY,
    rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
    comment TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
)"""


def init_db(conn):
    """Create the table if it doesn't exist yet, and commit.

    `sqlite3.connect("feedback.db")` creates the file; `":memory:"` gives a
    throw-away database in RAM, perfect for tests.

    Example:
        >>> conn = sqlite3.connect(":memory:")
        >>> init_db(conn)
        >>> conn.execute("SELECT count(*) FROM feedback").fetchone()
        (0,)
    """
    conn.execute(SCHEMA)
    conn.commit()


def record(conn, request_id, rating, comment="", now=None):
    """Save one rating.

    - Validate first: rating 1 or -1, comment at most 500 characters,
      else `ValueError` (the endpoint turns it into a 422).
    - `INSERT OR REPLACE`: rating the same answer again replaces the old
      row (the agent changed their mind). `request_id` is the primary key.
    - `?` placeholders: SQLite inserts the values as **data**. With an
      f-string, a request_id like `x'); DROP TABLE feedback; --` would be
      run as SQL (SQL injection).

    Example:
        >>> conn = sqlite3.connect(":memory:"); init_db(conn)
        >>> record(conn, "r1", -1, "  mauvais contrat ", now=datetime(2026, 12, 1, 10))
        >>> record(conn, "x'); DROP TABLE feedback; --", 1, now=datetime(2026, 12, 1, 11))
        >>> conn.execute("SELECT * FROM feedback").fetchall()
        [('r1', -1, 'mauvais contrat', '2026-12-01T10:00:00'), ("x'); DROP TABLE feedback; --", 1, '', '2026-12-01T11:00:00')]
        >>> record(conn, "r1", 5)
        Traceback (most recent call last):
        ValueError: rating must be 1 or -1
    """
    if rating not in (1, -1):
        raise ValueError("rating must be 1 or -1")
    if len(comment) > 500:
        raise ValueError("comment too long")
    at = (now or datetime.now()).isoformat(timespec="seconds")
    conn.execute("INSERT OR REPLACE INTO feedback (request_id, rating, comment, created_at) VALUES (?, ?, ?, ?)",
                 (request_id, rating, comment.strip(), at))
    conn.commit()


def stats(conn, since=None):
    """Thumbs up, thumbs down and the satisfaction rate.

    In SQLite `rating = 1` is 1 or 0, so `SUM(rating = 1)` counts the ups.
    `COALESCE(..., 0)` turns the `NULL` of an empty table into 0. ISO dates
    sort like text, so `created_at >= "2026-12-02"` works as a date filter.

    Example:
        >>> conn = sqlite3.connect(":memory:"); init_db(conn)
        >>> stats(conn)
        {'up': 0, 'down': 0, 'rate': None}
        >>> for rid, r, day in [("a", 1, 1), ("b", -1, 1), ("c", 1, 2)]:
        ...     record(conn, rid, r, now=datetime(2026, 12, day, 9))
        >>> stats(conn), stats(conn, since="2026-12-02")
        ({'up': 2, 'down': 1, 'rate': 0.667}, {'up': 1, 'down': 0, 'rate': 1.0})
    """
    where, params = ("WHERE created_at >= ?", (since,)) if since else ("", ())
    up, down = conn.execute(f"SELECT COALESCE(SUM(rating = 1), 0), COALESCE(SUM(rating = -1), 0) FROM feedback {where}", params).fetchone()
    return {"up": up, "down": down, "rate": round(up / (up + down), 3) if up + down else None}


def by_day(conn):
    """`[(day, up, down), ...]` sorted by day: is it getting better after each change?

    `substr(created_at, 1, 10)` keeps "YYYY-MM-DD"; `GROUP BY` makes one
    row per day.

    Example:
        >>> conn = sqlite3.connect(":memory:"); init_db(conn)
        >>> for rid, r, day in [("a", 1, 1), ("b", -1, 1), ("c", -1, 3)]:
        ...     record(conn, rid, r, now=datetime(2026, 12, day, 9))
        >>> by_day(conn)
        [('2026-12-01', 1, 1), ('2026-12-03', 0, 1)]
    """
    return [tuple(r) for r in conn.execute(
        "SELECT substr(created_at, 1, 10) AS day, SUM(rating = 1), SUM(rating = -1) FROM feedback GROUP BY day ORDER BY day")]


def export_negatives(conn, path, lookup):
    """Write every thumbs-down, oldest first, as one JSON line, joined with
    what happened: `lookup(request_id)` returns `{"question", "answer",
    "sources"}` from your logs (or `{}`). `**` merges that dict into the line.

    Returns how many lines were written.

    Example:
        >>> import tempfile, pathlib
        >>> conn = sqlite3.connect(":memory:"); init_db(conn)
        >>> record(conn, "b", -1, "mauvais contrat", now=datetime(2026, 12, 1, 10))
        >>> path = pathlib.Path(tempfile.mkdtemp()) / "neg.jsonl"
        >>> export_negatives(conn, path, lambda rid: {"question": "Caution ?", "answer": "Trois mois"})
        1
        >>> print(path.read_text(encoding="utf-8"))
        {"request_id": "b", "comment": "mauvais contrat", "created_at": "2026-12-01T10:00:00", "question": "Caution ?", "answer": "Trois mois"}
        <BLANKLINE>
    """
    rows = conn.execute("SELECT request_id, comment, created_at FROM feedback WHERE rating = -1 ORDER BY created_at").fetchall()
    with open(path, "w", encoding="utf-8") as f:
        for rid, comment, at in rows:
            f.write(json.dumps({"request_id": rid, "comment": comment, "created_at": at, **lookup(rid)}, ensure_ascii=False) + "\n")
    return len(rows)


if __name__ == "__main__":
    # Demo on a throw-away database. For real, use sqlite3.connect("feedback.db"), and in chat_endpoint.py
    # add POST /feedback {request_id, rating, comment} -> record(...), with a 422 on ValueError.
    import tempfile
    from pathlib import Path
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    week = [("r1", 1, "", 1), ("r2", -1, "cite le mauvais contrat", 1), ("r3", 1, "", 2), ("r4", 1, "", 2),
            ("r5", -1, "répond en français à une question en arabe", 3), ("r2", 1, "", 3), ("r6", 1, "", 3)]
    for rid, rating, comment, day in week:
        record(conn, rid, rating, comment, now=datetime(2026, 12, day, 10))
    print("stats:", stats(conn))
    print("by day:", by_day(conn))
    logs = {"r5": {"question": "شنوة الضمان؟", "answer": "La caution est de deux mois [1]."}}
    out = Path(tempfile.mkdtemp()) / "negatives.jsonl"
    print(export_negatives(conn, out, lambda rid: logs.get(rid, {})), "thumbs-down exported:")
    print(out.read_text(encoding="utf-8"))
