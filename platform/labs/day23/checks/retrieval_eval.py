r = fn("recall_at_k")
check("recall@3: 1 of 2 relevant found -> 0.5", lambda: r(["a", "x", "b", "c"], ["a", "c"], 3) == 0.5)
check("recall@4: both found -> 1.0", lambda: r(["a", "x", "b", "c"], ["a", "c"], 4) == 1.0)
check("recall@1: miss -> 0.0", lambda: r(["x", "a"], ["a"], 1) == 0.0)
h = fn("hit_at_k")
check("hit@k is 1.0 with at least one relevant in the top k", lambda: h(["x", "a"], ["a", "z"], 2) == 1.0 and h(["x", "a"], ["a"], 1) == 0.0)
rr = fn("reciprocal_rank")
check("reciprocal_rank: first relevant at position 3 -> 1/3", lambda: abs(rr(["x", "y", "a", "b"], ["b", "a"]) - 1 / 3) < 1e-9)
check("reciprocal_rank: none found -> 0.0", lambda: rr(["x"], ["a"]) == 0.0)

items = [{"question": "q1", "source_ids": ["a"]}, {"question": "q2", "source_ids": ["b"]}, {"question": "q3", "source_ids": []}]
rankings = {"q1": ["a", "b", "c"], "q2": ["c", "a", "b"]}
asked = []


def fake_retrieve(q):
    asked.append(q)
    return rankings[q]


m = lambda: fn("evaluate_retrieval")(items, fake_retrieve, ks=(1, 3))
check("evaluate_retrieval skips unanswerable items", lambda: m()["n"] == 2 and "q3" not in asked)
check("evaluate_retrieval averages recall@k", lambda: m()["recall@1"] == 0.5 and m()["recall@3"] == 1.0)
check("evaluate_retrieval reports hit@k and mrr", lambda: m()["hit@3"] == 1.0 and abs(m()["mrr"] - (1 + 1 / 3) / 2) < 1e-9)
check("one key per k", lambda: set(m()) == {"n", "recall@1", "recall@3", "hit@1", "hit@3", "mrr"})
