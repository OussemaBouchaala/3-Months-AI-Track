"""The agency adds 3 contracts a week. Re-embedding 120 documents every time is slow and costs money.

Index **incrementally**: a manifest (`{file name: hash of its bytes}`) remembers what
was indexed last time. Comparing it with today's folder says what is new, changed
or gone, and only those files are touched.

1. `file_hash` and `build_manifest`: today's fingerprint of the folder.
2. `plan`: old manifest vs new manifest -> add / update / delete / unchanged.
3. `batched`: items in groups (embedding APIs like batches).
4. `apply_plan`: run the plan with your own delete and index functions.
5. `load_manifest` / `save_manifest`: keep the manifest between runs.
"""
import hashlib
import json
from pathlib import Path


def file_hash(path):
    """The SHA-256 of the file's bytes, as 64 hex characters.

    Any change to the file, even one comma, gives a different hash. Renaming
    the file doesn't change it (the name isn't part of the bytes).

    Example:
        >>> import tempfile
        >>> f = Path(tempfile.mkdtemp()) / "a.txt"
        >>> _ = f.write_bytes(b"deux")
        >>> file_hash(f) == hashlib.sha256(b"deux").hexdigest(), len(file_hash(f))
        (True, 64)
    """
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_manifest(folder, patterns=("*.pdf", "*.docx", "*.html", "*.htm", "*.txt", "*.md")):
    """`{file name: file_hash}` for the documents of a folder (not its subfolders).

    Only the patterns you can parse are listed, so a stray .xlsx never
    reaches the indexer.

    Example:
        >>> import tempfile
        >>> d = Path(tempfile.mkdtemp())
        >>> _ = (d / "a.pdf").write_bytes(b"%PDF one")
        >>> _ = (d / "c.xlsx").write_bytes(b"skip me")
        >>> list(build_manifest(d))
        ['a.pdf']
    """
    folder = Path(folder)
    return {p.name: file_hash(p) for pat in patterns for p in folder.glob(pat) if p.is_file()}


def plan(old, new):
    """Compare two manifests and say what to do.

    With sets of names:

    - `add`: in new, not in old (`new - old`).
    - `delete`: in old, not in new.
    - `update`: in both (`&`), but the hash changed.
    - `unchanged`: in both with the same hash; only counted.

    Lists are sorted so the plan is the same on every machine.

    Example:
        >>> old = {"a.pdf": "h1", "b.txt": "h2", "gone.pdf": "h3"}
        >>> new = {"a.pdf": "h1x", "b.txt": "h2", "new.docx": "h5"}
        >>> plan(old, new)
        {'add': ['new.docx'], 'update': ['a.pdf'], 'delete': ['gone.pdf'], 'unchanged': 1}
    """
    return {
        "add": sorted(set(new) - set(old)),
        "update": sorted(n for n in set(new) & set(old) if new[n] != old[n]),
        "delete": sorted(set(old) - set(new)),
        "unchanged": sum(1 for n in set(new) & set(old) if new[n] == old[n]),
    }


def batched(items, size):
    """Yield lists of at most `size` items, in order.

    Sending 500 chunks to an embedding API in one call can hit its limit;
    one call per chunk is slow. Groups of 32 are a good middle. This is a
    generator (`yield`): it produces one batch at a time.

    Example:
        >>> list(batched(range(7), 3))
        [[0, 1, 2], [3, 4, 5], [6]]
        >>> list(batched([], 3))
        []
    """
    items = list(items)
    for i in range(0, len(items), size):
        yield items[i:i + size]


def apply_plan(p, delete_doc, index_doc):
    """Run a plan with your own functions.

    1. `delete_doc(name)` for every deleted **and updated** file: an updated
       file's old chunks must go before the new ones arrive, or the index
       holds both versions.
    2. `index_doc(name)` for every added and updated file; it returns how
       many chunks it stored.

    Passing the two functions in keeps this testable without a database.

    Example:
        >>> log = []
        >>> p = {"add": ["n1"], "update": ["u1"], "delete": ["d1"], "unchanged": 5}
        >>> apply_plan(p, lambda n: log.append("del " + n), lambda n: (log.append("idx " + n), 4)[1])
        {'deleted': 2, 'indexed': 2, 'chunks': 8}
        >>> log
        ['del d1', 'del u1', 'idx n1', 'idx u1']
    """
    for name in p["delete"] + p["update"]:
        delete_doc(name)
    chunks = 0
    for name in p["add"] + p["update"]:
        chunks += index_doc(name)
    return {"deleted": len(p["delete"]) + len(p["update"]), "indexed": len(p["add"]) + len(p["update"]), "chunks": chunks}


def load_manifest(path):
    """The saved manifest, or `{}` on the first run (so everything is "add").

    Example:
        >>> load_manifest("no_such_manifest.json")
        {}
    """
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else {}


def save_manifest(manifest, path):
    """Write the manifest as readable JSON. Call it only **after** the plan
    succeeded: if indexing crashed halfway, the next run retries those files.

    Example:
        >>> import tempfile
        >>> f = Path(tempfile.mkdtemp()) / "m.json"
        >>> save_manifest({"b.txt": "h2", "a.pdf": "h1"}, f)
        >>> load_manifest(f)
        {'a.pdf': 'h1', 'b.txt': 'h2'}
    """
    Path(path).write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")


def run_on_my_index(docs="../docs", manifest="manifest.json"):
    """The real run: parse, scrub PII, chunk, embed and store in Postgres.

    Needs the day17 Postgres container running (`docker compose up -d` in
    ../day17) and Ollama with bge-m3, plus days 16, 17, 39, 40, 45, 50, 52.

    Example (note): needs Postgres and Ollama.
        >>> run_on_my_index()  # doctest: +SKIP
    """
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

    DOCS = Path(docs)
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
    p = plan(load_manifest(manifest), new)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in p.items()})
    print(apply_plan(p, delete_doc, index_doc))
    save_manifest(new, manifest)                                   # only after success


if __name__ == "__main__":
    import os
    import sys
    import tempfile
    if len(sys.argv) > 1 and sys.argv[1] == "--real":
        run_on_my_index()
    else:
        # Three runs over a temp folder, with a fake "index" (a dict) instead of Postgres.
        folder, index = Path(tempfile.mkdtemp()), {}
        mpath = folder / "manifest.json"
        delete_doc = lambda name: index.pop(name, None)
        def index_doc(name):
            index[name] = len((folder / name).read_text(encoding="utf-8").split(".")) - 1   # 1 chunk per sentence
            return index[name]
        def run(label):
            new = build_manifest(folder)
            p = plan(load_manifest(mpath), new)
            print(f"{label:28} plan {p} -> {apply_plan(p, delete_doc, index_doc)}")
            save_manifest(new, mpath)

        for i in range(1, 4):
            (folder / f"bail{i}.txt").write_text(f"Bail {i}. Loyer {800 + 100 * i} TND. Caution deux mois.", encoding="utf-8")
        run("first run (empty manifest)")
        run("second run (nothing new)")
        (folder / "bail2.txt").write_text("Bail 2. Loyer 950 TND.", encoding="utf-8")
        (folder / "bail4.txt").write_text("Bail 4. Loyer 700 TND. Meublé. Caution un mois.", encoding="utf-8")
        os.remove(folder / "bail3.txt")
        run("third run (edit, add, remove)")
        print("index now:", dict(sorted(index.items())))
