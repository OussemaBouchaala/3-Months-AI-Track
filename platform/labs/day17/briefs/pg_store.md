# Vector search in SQL
**Topic:** `<=>` is cosine distance; `1 - distance` is the similarity you computed by hand.

## Real example
A shop stores product vectors in SQLite-like plain Python and searches them the way pgvector does: distance = 1 - cosine, ascending. The SQL shape is the same idea:

```python
import numpy as np

products = {"p1": [1, 0], "p2": [0.7, 0.7], "p3": [0, 1]}
q = np.array([1.0, 0.1])

def cos_distance(a, b):
    a, b = np.array(a, float), np.array(b, float)
    return 1 - a @ b / (np.linalg.norm(a) * np.linalg.norm(b))

# SELECT id, 1 - (embedding <=> q) AS score FROM products ORDER BY embedding <=> q LIMIT 2
for pid in sorted(products, key=lambda p: cos_distance(products[p], q))[:2]:
    print(pid, round(1 - cos_distance(products[pid], q), 3))
print("[" + ",".join(str(float(x)) for x in q) + "]")   # how a vector is written for pgvector
```

## Your mission
Write the SQL to create the table, upsert chunks, index and search them.

## Steps
1. `to_vector_literal`: `"[" + ",".join(...) + "]"`.
2. `create_table_sql`: extension, then table with `vector(dim)`.
3. `insert_sql`: `INSERT ... VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE ...`.
4. `search_sql` and `index_sql` as in the docstrings.
5. With the database up, **Run**: the stored vector finds itself first, and the order matches NumPy.

## Done when
**Check** passes and the pgvector ranking equals your NumPy ranking.
