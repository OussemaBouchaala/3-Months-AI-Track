import json, sqlite3, tempfile
from datetime import datetime
from pathlib import Path
init, rec, st, bd, ex = fn("init_db"), fn("record"), fn("stats"), fn("by_day"), fn("export_negatives")
def db():
    c = sqlite3.connect(":memory:")
    init(c)
    return c
check("init_db creates the feedback table", lambda: db().execute("SELECT count(*) FROM feedback").fetchone() == (0,))
def _raises(*a, **k):
    try:
        rec(db(), *a, **k)
    except ValueError:
        return True
    return False
check("record rejects bad ratings and long comments", lambda: _raises("r", 0) and _raises("r", 5) and _raises("r", 1, "x" * 501))
def filled():
    c = db()
    rec(c, "a", 1, now=datetime(2026, 12, 1, 9))
    rec(c, "b", -1, "  mauvais contrat ", now=datetime(2026, 12, 1, 10))
    rec(c, "c", -1, now=datetime(2026, 12, 2, 11))
    rec(c, "c", 1, now=datetime(2026, 12, 2, 11, 5))                    # changed their mind
    rec(c, "d'); DROP TABLE feedback; --", -1, now=datetime(2026, 12, 3, 8))
    return c
check("same request_id twice keeps the last rating", lambda: filled().execute("SELECT rating FROM feedback WHERE request_id='c'").fetchone() == (1,))
check("placeholders: a nasty request_id is stored as text", lambda: filled().execute("SELECT count(*) FROM feedback").fetchone() == (4,))
check("stats: up, down, rate", lambda: st(filled()) == {"up": 2, "down": 2, "rate": 0.5} and st(db()) == {"up": 0, "down": 0, "rate": None})
check("stats since a date", lambda: st(filled(), since="2026-12-02") == {"up": 1, "down": 1, "rate": 0.5})
check("by_day groups per day", lambda: bd(filled()) == [("2026-12-01", 1, 1), ("2026-12-02", 1, 0), ("2026-12-03", 0, 1)])
def _export():
    p = Path(tempfile.mkdtemp()) / "neg.jsonl"
    n = ex(filled(), p, lambda rid: {"question": "Caution ?", "answer": "Trois mois"} if rid == "b" else {})
    lines = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
    return n == 2 and lines[0] == {"request_id": "b", "comment": "mauvais contrat", "created_at": "2026-12-01T10:00:00", "question": "Caution ?", "answer": "Trois mois"}
check("export_negatives writes thumbs-down with their question and answer", _export)
