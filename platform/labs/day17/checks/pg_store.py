import re

import numpy as np

lit = fn("to_vector_literal")
check("to_vector_literal([0.5, 1, -2]) looks like [0.5,1.0,-2.0]",
      lambda: [float(x) for x in lit(np.array([0.5, 1, -2])).strip("[]").split(",")] == [0.5, 1.0, -2.0]
      and lit([0.5, 1, -2]).startswith("[") and " " not in lit([0.5, 1, -2]))
norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
check("create_table_sql enables the vector extension", lambda: "create extension if not exists vector" in norm(fn("create_table_sql")(1024)))
check("create_table_sql makes a vector(dim) column", lambda: "vector(1024)" in norm(fn("create_table_sql")(1024)) and "vector(8)" in norm(fn("create_table_sql")(8)),
      "Use an f-string: embedding vector({dim})")
check("create_table_sql: id is the primary key", lambda: re.search(r"id text primary key", norm(fn("create_table_sql")(3))) is not None)
check("insert_sql has 4 placeholders", lambda: fn("insert_sql")().count("%s") == 4)
check("insert_sql is an upsert", lambda: "on conflict (id) do update" in norm(fn("insert_sql")()))
s = lambda: norm(fn("search_sql")())
check("search_sql orders by cosine distance <=>", lambda: re.search(r"order by embedding <=> %s(::vector)?", s()) is not None)
check("search_sql returns 1 - distance as score and has a LIMIT", lambda: "1 - (embedding <=>" in s() and "limit %s" in s() and s().count("%s") == 3)
check("index_sql uses hnsw with vector_cosine_ops", lambda: "hnsw" in norm(fn("index_sql")()) and "vector_cosine_ops" in norm(fn("index_sql")()))
