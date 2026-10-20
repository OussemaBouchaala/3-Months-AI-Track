# A chunk without metadata is a sentence with no address. Give every chunk: its document, its section
# ("Article 4 - Caution"), its language, a stable id, a content hash, and a header for the embedding.
import hashlib
import re

HEADING = re.compile(r"^(?:#{1,6}\s+.+|Article\s+\d+\b.*|ARTICLE\s+\d+\b.*|الفصل\s+\S+.*|المادة\s+\S+.*)$")


def split_sections(text):
    """[(heading, body), ...]. A line matching HEADING starts a new section (heading without leading '#'
    and spaces). Text before the first heading gets heading "". Bodies stripped; sections with an empty
    body are dropped."""
    # TODO
    ...


def content_hash(text):
    """First 12 hex chars of sha1 of the text with whitespace collapsed and stripped (utf-8)."""
    # TODO
    ...


def make_chunks(doc, chunker, lang_fn):
    """doc: {"id", "title", "text"}. For each section, chunker(body) -> list of strings.
    Chunk ids are f"{doc_id}-c{n}", n counting across the whole document from 0.
    Each chunk: {"id", "doc_id", "title", "section", "lang": lang_fn(text), "text", "hash", "n_chars",
    "embed_text": f"{title} > {section}\\n{text}" (or f"{title}\\n{text}" when section is "")}."""
    # TODO
    ...


def dedupe_chunks(chunks):
    """Keep the first chunk of each hash (the same clause copied into 40 contracts). Return (kept, n_dropped)."""
    # TODO
    ...


if __name__ == "__main__":
    import json
    import sys
    sys.path += ["../day39", "../day40"]
    from arabic_index import chunk_sentences, split_sentences
    from mixed_text import detect_lang

    chunker = lambda body: chunk_sentences(split_sentences(body), max_chars=600, overlap=1)
    docs = [json.loads(l) for l in open("../day50/parsed.jsonl", encoding="utf-8")]
    chunks = [c for d in docs for c in make_chunks(dict(d, title=d.get("title", d["id"])), chunker, detect_lang)]
    chunks, dropped = dedupe_chunks(chunks)
    json.dump(chunks, open("chunks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(chunks), "chunks,", dropped, "duplicates dropped")
    print(chunks[0]["embed_text"][:200] if chunks else "no chunks")
