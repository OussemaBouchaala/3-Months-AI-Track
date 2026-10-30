"""Index the Arabic corpus: chunks that respect sentences and remember their document.

Cutting text every 500 characters can split a sentence in the middle, and then neither
half makes sense to the embedding model. Here chunks are built from **whole sentences**,
with one sentence of overlap so an idea that spans two chunks isn't lost.

1. `split_sentences`: cut a paragraph into sentences (Arabic punctuation included).
2. `chunk_sentences`: pack sentences into chunks of at most `max_chars`, with overlap.
3. `build_chunks`: chunk every document, with ids like `d12-c3` that keep the document id.
4. `doc_of`: get the document back from a chunk id.

Running the file shows chunking on a sample paragraph. `index_arcd()` chunks the real
corpus (day 36) and embeds it with bge-m3 (day 16), about 10 minutes on a laptop.
"""
import json
import re

SENT_END = re.compile(r"(?<=[.!?؟؛])\s+|\n+")    # split AFTER . ! ? ؟ ؛ followed by space, or on newlines


def split_sentences(text):
    """Cut text into sentences.

    `SENT_END` matches the **space after** a sentence end, including the
    Arabic question mark ؟ and semicolon ؛, or a line break. `(?<=...)` is a
    *lookbehind*: it checks the punctuation is there without removing it,
    so each sentence keeps its full stop.

    Example:
        >>> split_sentences("تونس جميلة. هل زرت صفاقس؟ نعم!\\nسوسة؛ والمنستير")
        ['تونس جميلة.', 'هل زرت صفاقس؟', 'نعم!', 'سوسة؛', 'والمنستير']
    """
    return [s.strip() for s in SENT_END.split(text) if s.strip()]


def chunk_sentences(sentences, max_chars=500, overlap=1):
    """Pack sentences into chunks of at most `max_chars`, repeating `overlap` sentence(s).

    Greedy packing: keep adding sentences while the chunk still fits. When
    the next one doesn't fit, close the chunk and start the next with the
    last `overlap` sentence(s), so context carries over.

    - `new` counts the sentences added since the last chunk, so no chunk is
      made of overlap only.
    - A sentence longer than `max_chars` becomes its own chunk (it can't be split).

    Example (5-character sentences, 11 characters per chunk):
        >>> S = ["aaaa.", "bbbb.", "cccc.", "dddd."]
        >>> chunk_sentences(S, max_chars=11, overlap=0)
        ['aaaa. bbbb.', 'cccc. dddd.']
        >>> chunk_sentences(S, max_chars=11, overlap=1)
        ['aaaa. bbbb.', 'bbbb. cccc.', 'cccc. dddd.']
        >>> chunk_sentences(S, max_chars=500)
        ['aaaa. bbbb. cccc. dddd.']
    """
    chunks, cur, new = [], [], 0
    for s in sentences:
        if cur and new and len(" ".join(cur + [s])) > max_chars:
            chunks.append(" ".join(cur))
            cur = cur[-overlap:] if overlap else []
            new = 0
            if cur and len(" ".join(cur + [s])) > max_chars:
                cur = []
        cur.append(s)
        new += 1
    if cur and new:
        chunks.append(" ".join(cur))
    return chunks


def build_chunks(docs, max_chars=500, overlap=1):
    """Chunk every document. Each chunk keeps its document's id and title.

    The chunk id `d0-c1` means "document d0, chunk 1", so retrieval results
    can always be traced back to the source paragraph (needed for doc-level
    recall on day 41).

    Example:
        >>> docs = [{"id": "d0", "title": "تونس", "text": "aaaa. bbbb. cccc."}, {"id": "d1", "title": "صفاقس", "text": "zz."}]
        >>> [(c["id"], c["doc_id"], c["text"]) for c in build_chunks(docs, max_chars=11, overlap=0)]
        [('d0-c0', 'd0', 'aaaa. bbbb.'), ('d0-c1', 'd0', 'cccc.'), ('d1-c0', 'd1', 'zz.')]
    """
    out = []
    for d in docs:
        for i, text in enumerate(chunk_sentences(split_sentences(d["text"]), max_chars, overlap)):
            out.append({"id": f"{d['id']}-c{i}", "doc_id": d["id"], "title": d["title"], "text": text})
    return out


def doc_of(chunk_id):
    """The document id of a chunk id: everything before the last `-c`.

    `rsplit("-c", 1)` splits once, from the right, so ids with dashes
    elsewhere still work.

    Example:
        >>> doc_of("d12-c3")
        'd12'
    """
    return chunk_id.rsplit("-c", 1)[0]


def index_arcd():
    """Chunk the real ARCD corpus (day 36) and embed it with bge-m3 (day 16).
    Saves `arcd_chunks.json` and `arcd_embeddings.npy`, used by day 41."""
    import sys

    import numpy as np

    sys.path += ["../day16", "../day36"]
    from embed import embed_in_batches, normalize
    from load_corpus import load_jsonl

    docs = load_jsonl("../day36/arcd_docs.jsonl")
    chunks = build_chunks(docs)
    lengths = sorted(len(c["text"]) for c in chunks)
    print(f"{len(docs)} docs -> {len(chunks)} chunks, median {lengths[len(lengths) // 2]} chars, max {lengths[-1]}")
    json.dump(chunks, open("arcd_chunks.json", "w", encoding="utf-8"), ensure_ascii=False)
    # Embed the title with the text: "<title>: <chunk>" gives each piece its topic.
    matrix = normalize(embed_in_batches([f"{c['title']}: {c['text']}" for c in chunks], batch_size=32))
    np.save("arcd_embeddings.npy", matrix)
    print("saved arcd_chunks.json and arcd_embeddings.npy", matrix.shape)


if __name__ == "__main__":
    paragraph = ("تونس دولة في شمال أفريقيا. عاصمتها مدينة تونس. يبلغ عدد سكانها حوالي 12 مليون نسمة. "
                 "من أهم مدنها صفاقس وسوسة. هل تعرف القيروان؟ هي من أقدم المدن الإسلامية في المغرب العربي.")
    print("sentences:")
    for s in split_sentences(paragraph):
        print("  -", s)
    print("\nchunks of at most 80 characters, 1 sentence of overlap:")
    for c in build_chunks([{"id": "d0", "title": "تونس", "text": paragraph}], max_chars=80, overlap=1):
        print(f"  {c['id']} ({len(c['text'])} chars): {c['text']}")
