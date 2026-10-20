# Hybrid search: keyword scores (BM25) + vector ranking, fused with Reciprocal Rank Fusion.
# Keywords catch exact terms (CIN, 150 TND, a name); vectors catch meaning across languages.
import json
import math
import re
from collections import Counter


def tokenize(text):
    """Lowercase, then every run of word characters: re.findall(r"\w+", text.lower()).
    \w matches Arabic letters too."""
    # TODO
    ...


def bm25_scores(query, docs, k1=1.5, b=0.75):
    """One BM25 score per doc (same order as docs).
    For each query term t present in the collection:
        idf(t) = ln((N - df + 0.5) / (df + 0.5) + 1)        df = number of docs containing t
        score += idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avgdl))
    tf = count of t in the doc's tokens, len(doc) = number of tokens, avgdl = average doc length.
    Repeated query terms count once."""
    # TODO
    ...


def rank_ids(ids, scores):
    """ids sorted by score, best first."""
    # TODO
    ...


def rrf(rankings, k=60):
    """Reciprocal Rank Fusion. rankings: lists of ids, each best first.
    Each id gets sum over rankings of 1 / (k + rank), rank starting at 1. Missing from a ranking = no points.
    Return all ids sorted by fused score, best first."""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    import numpy as np

    sys.path.append("../day16")
    from embed import embed, normalize, search

    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    matrix = np.load("../day16/embeddings.npy")
    ids = [c["id"] for c in chunks]
    heading = {c["id"]: c["heading"] for c in chunks}

    for q in ["CIN passport payslips", "150 TND report", "what do I need to bring to sign a lease?"]:
        keyword = rank_ids(ids, bm25_scores(q, [c["text"] for c in chunks]))
        qv = normalize(embed([q]))[0]
        vector = [ids[i] for i, _ in search(qv, matrix, k=len(ids))]
        fused = rrf([keyword, vector])
        print(q)
        for name, r in [("keyword", keyword), ("vector", vector), ("hybrid", fused)]:
            print(f"   {name:<8}", [heading[i] for i in r[:3]])
