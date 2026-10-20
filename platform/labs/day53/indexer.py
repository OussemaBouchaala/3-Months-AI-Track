# The agency adds 3 contracts a week. Re-embedding 120 documents every time is slow and costs money.
# Index incrementally: a manifest of file hashes says what is new, changed or gone.
import hashlib
import json
from pathlib import Path


def file_hash(path):
    """sha256 hex digest of the file's bytes."""
    # TODO
    ...


def build_manifest(folder, patterns=("*.pdf", "*.docx", "*.html", "*.htm", "*.txt", "*.md")):
    """{file name: file_hash} for the files of folder matching any pattern (not recursive)."""
    # TODO
    ...


def plan(old, new):
    """Compare two manifests. {"add": names only in new, "update": names in both with a different hash,
    "delete": names only in old, "unchanged": count}. Lists sorted."""
    # TODO
    ...


def batched(items, size):
    """Yield lists of at most size items, in order (embedding APIs and executemany like batches)."""
    # TODO
    ...


def apply_plan(p, delete_doc, index_doc):
    """Run a plan: delete_doc(name) for every deleted AND updated file (old chunks must go first),
    then index_doc(name) for every added and updated file, which returns its number of chunks.
    Return {"deleted": n files, "indexed": n files, "chunks": total chunks}."""
    # TODO
    ...


def load_manifest(path):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else {}


def save_manifest(manifest, path):
    Path(path).write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    # Needs the day17 Postgres container running (docker compose up -d in ../day17) and Ollama with bge-m3.
    import sys
    sys.path += ["../day16", "../day17", "../day39", "../day40", "../day45", "../day50", "../day52"]
    import psycopg
    from arabic_index import chunk_sentences, split_sentences
    from chunk_meta import dedupe_chunks, make_chunks
    from embed import embed
    from mixed_text import detect_lang
    from parse_docs import parse_file
    from pg_store import DSN, to_vector_literal
    from pii_scrub import scrub

    DOCS, MANIFEST = Path(sys.argv[1] if len(sys.argv) > 1 else "../docs"), Path("manifest.json")
    chunker = lambda body: chunk_sentences(split_sentences(body), max_chars=600, overlap=1)
    conn = psycopg.connect(DSN, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.execute("""CREATE TABLE IF NOT EXISTS project_chunks (id text PRIMARY KEY, doc_id text, section text, lang text,
                    text text, hash text, embedding vector(1024))""")

    def delete_doc(name):
        conn.execute("DELETE FROM project_chunks WHERE doc_id = %s", (Path(name).stem,))

    def index_doc(name):
        doc = parse_file(DOCS / name)
        doc["text"] = scrub(doc["text"])[0]                         # PII never reaches the index
        chunks, _ = dedupe_chunks(make_chunks(dict(doc, title=doc["id"]), chunker, detect_lang))
        for batch in batched(chunks, 32):
            vecs = embed([c["embed_text"] for c in batch])
            with conn.cursor() as cur:
                cur.executemany("INSERT INTO project_chunks VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                                [(c["id"], c["doc_id"], c["section"], c["lang"], c["text"], c["hash"], to_vector_literal(v)) for c, v in zip(batch, vecs)])
        return len(chunks)

    new = build_manifest(DOCS)
    p = plan(load_manifest(MANIFEST), new)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in p.items()})
    print(apply_plan(p, delete_doc, index_doc))
    save_manifest(new, MANIFEST)                                   # only after success
