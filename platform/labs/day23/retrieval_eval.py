# Did retrieval find the right chunk? recall@k, hit@k and MRR over the whole test set.
# Check uses tiny hand-made rankings. Run compares keyword, vector and hybrid on your testset_v1.json.
import json
import statistics


def recall_at_k(retrieved, relevant, k):
    """Share of the relevant ids found in the first k retrieved: |relevant ∩ retrieved[:k]| / |relevant|."""
    # TODO
    ...


def hit_at_k(retrieved, relevant, k):
    """1.0 if at least one relevant id is in the first k retrieved, else 0.0."""
    # TODO
    ...


def reciprocal_rank(retrieved, relevant):
    """1 / (position of the FIRST relevant id), positions starting at 1. None found -> 0.0."""
    # TODO
    ...


def evaluate_retrieval(items, retrieve, ks=(1, 3, 5)):
    """items: dicts with "question" and "source_ids". retrieve(question) -> list of ids, best first.
    Skip unanswerable items (no source_ids): there's nothing to find.
    Return {"n": items used, "recall@1": mean, "recall@3": mean, ..., "hit@1": ..., ..., "mrr": mean}
    with one recall@k and one hit@k key per k."""
    # TODO
    ...


if __name__ == "__main__":
    import sys

    import numpy as np

    sys.path += ["../day16", "../day20"]
    from embed import embed, normalize, search
    from hybrid import bm25_scores, rank_ids, rrf

    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    matrix = np.load("../day16/embeddings.npy")
    ids, texts = [c["id"] for c in chunks], [c["text"] for c in chunks]
    items = json.load(open("../day22/testset_v1.json", encoding="utf-8"))

    def keyword(q):
        return rank_ids(ids, bm25_scores(q, texts))

    def vector(q):
        return [ids[i] for i, _ in search(normalize(embed([q]))[0], matrix, k=len(ids))]

    def hybrid(q):
        return rrf([keyword(q), vector(q)])

    print("| retriever | n | recall@1 | recall@3 | recall@5 | mrr |\n|---|---|---|---|---|---|")
    for name, r in [("keyword", keyword), ("vector", vector), ("hybrid", hybrid)]:
        m = evaluate_retrieval(items, r)
        print(f"| {name} | {m['n']} | {m['recall@1']:.2f} | {m['recall@3']:.2f} | {m['recall@5']:.2f} | {m['mrr']:.2f} |")
