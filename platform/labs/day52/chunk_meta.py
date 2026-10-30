"""A chunk without metadata is a sentence with no address.

Give every chunk its document, its section ("Article 4 - Caution"), its language, a
stable id, a content hash, and a header for the embedding. Then an answer can cite
"Bail type, Article 4" and a filter can say "French chunks only".

1. `HEADING`: the lines that start a section (Article, Markdown `#`, الفصل, المادة).
2. `split_sections`: a document into `(heading, body)` pairs.
3. `content_hash`: a short fingerprint of a chunk's text.
4. `make_chunks`: sections into chunks with all their metadata.
5. `dedupe_chunks`: the same clause copied into 40 contracts is indexed once.
"""
import hashlib
import re

HEADING = re.compile(r"^(?:#{1,6}\s+.+|Article\s+\d+\b.*|ARTICLE\s+\d+\b.*|الفصل\s+\S+.*|المادة\s+\S+.*)$")


def split_sections(text):
    """Cut a document into `[(heading, body), ...]`.

    Walk the lines. A line matching `HEADING` closes the current section
    and opens a new one (its `#` signs are removed). Text before the first
    heading gets the heading `""`. Sections with an empty body (a heading
    followed directly by another heading) are dropped.

    Example:
        >>> doc = "Contrat de location\\nArticle 1 - Loyer\\n900 TND.\\n## Annexe\\nالمادة 3 الضمان\\nشهرين."
        >>> for h, b in split_sections(doc):
        ...     print(repr(h), "->", b)
        '' -> Contrat de location
        'Article 1 - Loyer' -> 900 TND.
        'المادة 3 الضمان' -> شهرين.
    """
    sections, heading, lines = [], "", []
    for line in text.splitlines():
        if HEADING.match(line.strip()):
            sections.append((heading, "\n".join(lines).strip()))
            heading, lines = line.strip().lstrip("#").strip(), []
        else:
            lines.append(line)
    sections.append((heading, "\n".join(lines).strip()))
    return [(h, b) for h, b in sections if b]


def content_hash(text):
    """The first 12 hex characters of the SHA-1 of the text.

    Whitespace is collapsed first, so "Deux  mois.\\n" and "Deux mois." get
    the same hash: same words, same chunk. 12 hex characters (48 bits) are
    plenty to tell thousands of chunks apart.

    Example:
        >>> content_hash("Deux  mois.\\n") == content_hash("Deux mois.")
        True
        >>> len(content_hash("a")), content_hash("a") != content_hash("b")
        (12, True)
    """
    return hashlib.sha1(re.sub(r"\s+", " ", text).strip().encode("utf-8")).hexdigest()[:12]


def make_chunks(doc, chunker, lang_fn):
    """All the chunks of one document, each with its metadata.

    For each section, `chunker(body)` cuts the body into pieces (day 40's
    sentence chunker in the real run). Every piece becomes a dict:

    - `id`: `"<doc_id>-c<n>"`, `n` counting across the whole document, so
      ids are stable as long as the document doesn't change.
    - `section`, `lang` (from `lang_fn`), `hash`, `n_chars`.
    - `embed_text`: `"title > section"` on top of the text. The embedding
      then knows that "deux mois" is about the *caution*, not the rent.

    Example:
        >>> doc = {"id": "bail7", "title": "Bail type", "text": "Article 1 - Loyer\\n900 TND.\\nArticle 2 - Caution\\nDeux mois."}
        >>> chunks = make_chunks(doc, lambda body: [body], lambda t: "fr")
        >>> [c["id"] for c in chunks]
        ['bail7-c0', 'bail7-c1']
        >>> print(chunks[1]["embed_text"])
        Bail type > Article 2 - Caution
        Deux mois.
    """
    out = []
    for section, body in split_sections(doc["text"]):
        for piece in chunker(body):
            head = f"{doc['title']} > {section}" if section else doc["title"]
            out.append({"id": f"{doc['id']}-c{len(out)}", "doc_id": doc["id"], "title": doc["title"], "section": section,
                        "lang": lang_fn(piece), "text": piece, "hash": content_hash(piece), "n_chars": len(piece),
                        "embed_text": f"{head}\n{piece}"})
    return out


def dedupe_chunks(chunks):
    """Keep the first chunk of each hash. Returns `(kept, n_dropped)`.

    Agencies copy the same clauses into every contract. Indexing them 40
    times wastes money and fills the top-k results with copies.

    Example:
        >>> kept, dropped = dedupe_chunks([{"id": "a", "hash": "h1"}, {"id": "b", "hash": "h1"}, {"id": "c", "hash": "h2"}])
        >>> [c["id"] for c in kept], dropped
        (['a', 'c'], 1)
    """
    seen, kept = set(), []
    for c in chunks:
        if c["hash"] not in seen:
            seen.add(c["hash"])
            kept.append(c)
    return kept, len(chunks) - len(kept)


def run_on_my_docs(parsed="../day50/parsed.jsonl", out="chunks.json"):
    """The real run: day 50's parsed documents, day 40's chunker and day 39's
    language detector, deduped and saved to `chunks.json`.

    Example (note): needs day 50's parsed.jsonl.
        >>> run_on_my_docs()  # doctest: +SKIP
    """
    import json
    import sys
    sys.path += ["../day39", "../day40"]
    from arabic_index import chunk_sentences, split_sentences
    from mixed_text import detect_lang

    chunker = lambda body: chunk_sentences(split_sentences(body), max_chars=600, overlap=1)
    docs = [json.loads(l) for l in open(parsed, encoding="utf-8")]
    chunks = [c for d in docs for c in make_chunks(dict(d, title=d.get("title", d["id"])), chunker, detect_lang)]
    chunks, dropped = dedupe_chunks(chunks)
    json.dump(chunks, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(chunks), "chunks,", dropped, "duplicates dropped")
    print(chunks[0]["embed_text"][:200] if chunks else "no chunks")


if __name__ == "__main__":
    from pathlib import Path
    parsed = Path("../day50/parsed.jsonl")
    if parsed.exists() and parsed.stat().st_size > 0:
        run_on_my_docs()
    else:
        # No parsed.jsonl yet: two contracts that share a clause.
        clause = "La caution de deux mois est remboursée sous trente jours."
        docs = [{"id": "bail1", "title": "Bail Lac 2", "text": f"Article 1 - Loyer\nLe loyer est de 900 TND.\nArticle 2 - Caution\n{clause}"},
                {"id": "bail2", "title": "Bail Menzah", "text": f"Article 1 - Loyer\nLe loyer est de 1200 TND.\nArticle 2 - Caution\n{clause}\n"
                                                                "المادة 3 الصيانة\nالمكتري يتكفل بالإصلاحات الصغيرة."}]
        lang = lambda t: "ar" if re.search(r"[؀-ۿ]", t) else "fr"
        chunks = [c for d in docs for c in make_chunks(d, lambda body: [body], lang)]
        kept, dropped = dedupe_chunks(chunks)
        print(len(chunks), "chunks,", dropped, "duplicate dropped ->", len(kept), "kept")
        for c in kept:
            print(f"{c['id']:9} {c['lang']} {c['hash']}  {c['embed_text']!r}")
