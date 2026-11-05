# Hybrid search: keyword scores (BM25) + vector ranking, fused with Reciprocal Rank Fusion.
# Keywords catch exact terms (CIN, 150 TND, a name); vectors catch meaning across languages.
import json
import math
import re
from collections import Counter
import statistics


def tokenize(text):
    """Lowercase, then every run of word characters: re.findall(r"\w+", text.lower()).
    \w matches Arabic letters too."""
    # TODO
    return re.findall(r"\w+", text.lower())


def bm25_scores(query, docs, k1=1.5, b=0.75):
    """One BM25 score per doc (same order as docs).
    For each query term t present in the collection:
        idf(t) = ln((N - df + 0.5) / (df + 0.5) + 1)        df = number of docs containing t
        score += idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / avgdl))
    tf = count of t in the doc's tokens, len(doc) = number of tokens, avgdl = average doc length.
    Repeated query terms count once."""
    # TODO
    tokens= [tokenize(d) for d in docs]
    N = len(docs)
    avgdl= statistics.mean([len(doc) for doc in tokens]) if N>0 else 0
    uquery=set(tokenize(query))
    df={t:0 for t in uquery}
    doc_counters=[Counter(doc) for doc in tokens]
    for counter in doc_counters:
        for t in uquery:
            if counter[t] > 0: # Check if term exists in this doc
                df[t] += 1
    scores = [0.0] * N
    for t in uquery:
        if df[t] == 0: continue # Term not in collection, idf undefined/0
        
        # idf = ln((N - df + 0.5) / (df + 0.5) + 1)
        idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1)
        
        for i in range(N):
            tf = doc_counters[i][t]
            if tf == 0: continue # Term not in this doc
            
            dl = len(tokens[i])
            # Term score = idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))
            norm = tf + k1 * (1 - b + b * dl / avgdl)
            scores[i] += idf * tf * (k1 + 1) / norm
            
    return scores        


def rank_ids(ids, scores):
    """ids sorted by score, best first."""
    # TODO
    return [id_ for id_, _ in sorted(zip(ids,scores), key=lambda x: x[1] , reverse=True)]


def rrf(rankings, k=60):
    """Reciprocal Rank Fusion. rankings: lists of ids, each best first.
    Each id gets sum over rankings of 1 / (k + rank), rank starting at 1. Missing from a ranking = no points.
    Return all ids sorted by fused score, best first."""
    # TODO
    fused = {}
    for ranking in rankings:
            for rank,doc_id in enumerate(ranking,start=1):
                fused[doc_id]= fused.get(doc_id,0)+1/(k+rank)
    return [doc_id for doc_id, _ in sorted(fused.items(), key=lambda x: x[1], reverse=True)]


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
