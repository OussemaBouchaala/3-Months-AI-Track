# Week 4's evaluation, re-run on real Arabic: does normalization + stemming + hybrid search help?
# ARCD's questions come with their source paragraph and an answer span, so the test set is free.
import random


def sample_questions(questions, n, seed=0):
    """A reproducible random sample: random.Random(seed).sample(questions, n) (all of them if n >= len)."""
    # TODO
    ...


def doc_ranking(chunk_ids):
    """Chunks d3-c0, d7-c2, d3-c1, d9-c0 -> documents d3, d7, d9: first appearance order, no duplicates.
    (A chunk id's document is everything before the last "-c".)"""
    # TODO
    ...


def doc_recall_at_k(chunk_ids, source_doc_ids, k):
    """recall@k at DOCUMENT level: share of source_doc_ids found in the first k documents of doc_ranking."""
    # TODO
    ...


def answer_found(prediction, gold, norm=lambda s: s):
    """ARCD answers are short spans copied from the paragraph. Count a hit when norm(gold) appears
    inside norm(prediction). Empty gold -> False."""
    # TODO
    ...


def compare_table(rows, baseline):
    """rows: [{"variant": name, "recall@1": x, "recall@5": y}, ...]. baseline: the variant name to compare to.
    Markdown, rows in the given order, recall with 2 decimals and the recall@5 change vs baseline as +0.07 / -0.02 / +0.00:
    | variant | recall@1 | recall@5 | Δ recall@5 |"""
    # TODO
    ...


if __name__ == "__main__":
    import json
    import sys

    import numpy as np

    sys.path += ["../day16", "../day20", "../day36", "../day37", "../day38"]
    from arabic_keywords import tokenize_ar
    from arabic_norm import normalize_arabic
    from embed import embed, normalize, search
    from hybrid import rrf
    from load_corpus import load_jsonl
    import hybrid

    chunks = json.load(open("../day40/arcd_chunks.json", encoding="utf-8"))
    matrix = np.load("../day40/arcd_embeddings.npy")
    ids = [c["id"] for c in chunks]
    texts = [f"{c['title']}: {c['text']}" for c in chunks]
    qs = sample_questions(load_jsonl("../day36/arcd_questions.jsonl"), 100)

    def bm25_with(tokenizer):
        hybrid.tokenize = tokenizer                # reuse your Week 3 BM25 with another tokenizer
        def run(q):
            scores = hybrid.bm25_scores(q, texts)
            return [ids[i] for i in np.argsort(-np.array(scores))]
        return run

    raw = bm25_with(lambda t: t.lower().split())
    stemmed = bm25_with(lambda t: tokenize_ar(t))
    def vector(q):
        return [ids[i] for i, _ in search(normalize(embed([q]))[0], matrix, k=50)]
    variants = {"bm25 raw": raw, "bm25 normalized+stemmed": stemmed, "vector bge-m3": vector,
                "hybrid (stemmed + vector)": lambda q: rrf([stemmed(q)[:50], vector(q)])}
    rows = []
    for name, retrieve in variants.items():
        r1, r5 = [], []
        for q in qs:
            got = retrieve(q["question"])
            r1.append(doc_recall_at_k(got, q["source_ids"], 1))
            r5.append(doc_recall_at_k(got, q["source_ids"], 5))
        rows.append({"variant": name, "recall@1": sum(r1) / len(r1), "recall@5": sum(r5) / len(r5)})
    table = compare_table(rows, baseline="bm25 raw")
    print(table)
    open("arabic_results.md", "w", encoding="utf-8").write(table)
