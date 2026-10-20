# Collect feedback
**Topic:** a SQLite table for thumbs up/down, safe SQL, daily stats, and an export of the failures.

## Real example
Why `?` placeholders matter (a different table, the classic attack):

```python
import sqlite3
c = sqlite3.connect(":memory:")
c.execute("CREATE TABLE users (name TEXT)")
c.execute("INSERT INTO users VALUES ('amel'), ('sami')")
evil = "x' OR '1'='1"
print("f-string:", c.execute(f"SELECT count(*) FROM users WHERE name = '{evil}'").fetchone())
print("placeholder:", c.execute("SELECT count(*) FROM users WHERE name = ?", (evil,)).fetchone())
```

The f-string version returns every row; the placeholder version treats the input as plain text.

## Your mission
Store a rating per answer, and turn thumbs-down into a file you'll analyze in Week 10.

## Steps
1. `init_db`, `record` (validation, INSERT OR REPLACE, placeholders).
2. `stats` (with `since`) and `by_day`.
3. `export_negatives` with a `lookup` into your request logs.
4. Add `POST /feedback` to the chat service and 👍/👎 buttons under each answer in `index.html`.

## Done when
**Check** passes and a click on 👎 in the browser shows up in `negatives.jsonl`.
