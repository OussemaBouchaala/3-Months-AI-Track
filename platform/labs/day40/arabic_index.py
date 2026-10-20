# Index the Arabic corpus: sentence-aware chunks that remember their document, then embeddings.
# Check uses tiny texts. Run chunks ARCD (day36) and embeds it with bge-m3 (day16): ~10 minutes on a laptop.
import json
import re

SENT_END = re.compile(r"(?<=[.!?؟؛])\s+|\n+")    # split AFTER . ! ? ؟ ؛ followed by space, or on newlines


def split_sentences(text):
    """Split with SENT_END, strip each piece, drop empty ones."""
    # TODO
    ...


def chunk_sentences(sentences, max_chars=500, overlap=1):
    """Greedy packing: add sentences to the current chunk while the joined text (" ".join) stays <= max_chars.
    When the next sentence doesn't fit, close the chunk and start the next one with the last `overlap`
    sentence(s) of the previous chunk, then continue. A single sentence longer than max_chars is its own chunk.
    Return a list of strings. No chunk may be only overlap: the last chunk must contain something new."""
    # TODO
    ...


def build_chunks(docs, max_chars=500, overlap=1):
    """docs: [{"id": "d0", "title": ..., "text": ...}].
    Return [{"id": "d0-c0", "doc_id": "d0", "title": ..., "text": chunk}, ...]: ids restart at c0 for each doc."""
    # TODO
    ...


def doc_of(chunk_id):
    """'d12-c3' -> 'd12'"""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    import numpy as np

    sys.path += ["../day16", "../day36"]
    from embed import embed, embed_in_batches, normalize
    from load_corpus import load_jsonl

    docs = load_jsonl("../day36/arcd_docs.jsonl")
    chunks = build_chunks(docs)
    lengths = sorted(len(c["text"]) for c in chunks)
    print(f"{len(docs)} docs -> {len(chunks)} chunks, median {lengths[len(lengths) // 2]} chars, max {lengths[-1]}")
    json.dump(chunks, open("arcd_chunks.json", "w", encoding="utf-8"), ensure_ascii=False)
    # Embed the title with the text: "<title>: <chunk>" gives each piece its topic (like headings in Week 3).
    matrix = normalize(embed_in_batches([f"{c['title']}: {c['text']}" for c in chunks], batch_size=32))
    np.save("arcd_embeddings.npy", matrix)
    print("saved arcd_chunks.json and arcd_embeddings.npy", matrix.shape)
