# Store the chunks and their vectors in Postgres, then search with SQL.
# Before Run: `docker compose up -d` in this folder, and `pip install "psycopg[binary]"`.
# Check only tests the SQL text and the helpers, so it works without a database.
import json

import numpy as np

DSN = "postgresql://postgres:bench@localhost:5432/rag"
DIM = 1024   # bge-m3 vectors have 1024 numbers


def to_vector_literal(vec):
    """pgvector reads vectors written as text: [0.1,0.2,0.3]. Return that string (no spaces).
    Use repr-free formatting: ",".join(f"{x:.6f}" ...) or str(float(x))."""
    # TODO
    ...


def create_table_sql(dim=DIM):
    """Return SQL that (1) enables the extension: CREATE EXTENSION IF NOT EXISTS vector;
    (2) creates the table IF NOT EXISTS chunks (id text PRIMARY KEY, heading text, content text, embedding vector(<dim>))."""
    # TODO
    ...


def insert_sql():
    """INSERT one chunk with 4 placeholders (%s) for id, heading, content, embedding.
    Make it an upsert: ON CONFLICT (id) DO UPDATE SET heading = EXCLUDED.heading, ... so re-running doesn't fail."""
    # TODO
    ...


def search_sql():
    """Top-k by cosine distance. pgvector's cosine distance operator is <=> (0 = same direction).
    Return: SELECT id, heading, 1 - (embedding <=> %s::vector) AS score FROM chunks
            ORDER BY embedding <=> %s::vector LIMIT %s
    (the query vector is passed twice, then k)."""
    # TODO
    ...


def index_sql():
    """An approximate-nearest-neighbour index for cosine distance:
    CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops)"""
    # TODO
    ...


if __name__ == "__main__":
    import psycopg

    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    matrix = np.load("../day16/embeddings.npy")

    with psycopg.connect(DSN) as conn:
        conn.execute(create_table_sql(matrix.shape[1]))
        for c, v in zip(chunks, matrix):
            conn.execute(insert_sql(), (c["id"], c["heading"], c["text"], to_vector_literal(v)))
        conn.execute(index_sql())
        print("stored", conn.execute("SELECT count(*) FROM chunks").fetchone()[0], "chunks")

        # Same query as yesterday: compare with the NumPy ranking
        q = matrix[2]   # use a stored vector as the query: it must find itself first
        lit = to_vector_literal(q)
        for row in conn.execute(search_sql(), (lit, lit, 3)).fetchall():
            print(row)
        print("numpy:", [(chunks[i]["id"], round(float(s), 4)) for i, s in
                         sorted(enumerate(matrix @ q), key=lambda t: -t[1])[:3]])
