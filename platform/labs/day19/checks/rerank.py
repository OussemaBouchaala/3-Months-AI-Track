sp = lambda: fn("score_prompt")("Can I bring my dog?", "Dogs are banned near the pool.")
check("score_prompt includes the query and the passage", lambda: "Can I bring my dog?" in sp() and "Dogs are banned near the pool." in sp())
check("score_prompt asks for a 0 to 10 score", lambda: "0" in sp() and "10" in sp())
ps = fn("parse_score")
check("parse_score('8') -> 8.0", lambda: ps("8") == 8.0 and isinstance(ps("8"), float))
check("parse_score('Score: 7.5/10') -> 7.5", lambda: ps("Score: 7.5/10") == 7.5)
check("parse_score clamps to 10", lambda: ps("42") == 10.0)
check("parse_score with no number -> 0.0", lambda: ps("I can't tell") == 0.0)

cands = [{"id": "a", "text": "pool rules"}, {"id": "b", "text": "pets allowed"}, {"id": "c", "text": "visits"}, {"id": "d", "text": "pets and pool"}]
scores = {"pool rules": 4, "pets allowed": 7, "visits": 1, "pets and pool": 9}
out = lambda: fn("rerank")("dog?", [dict(c) for c in cands], lambda q, t: scores[t], top_n=2)
check("rerank returns top_n, best first", lambda: [c["id"] for c in out()] == ["d", "b"])
check("each result has its rerank_score", lambda: [c["rerank_score"] for c in out()] == [9, 7])
check("rerank doesn't modify the input dicts", lambda: (lambda cs: (fn("rerank")("q", cs, lambda q, t: 1.0), "rerank_score" not in cs[0])[1])([dict(c) for c in cands]),
      'Return new dicts: {**c, "rerank_score": s}')
check("ties keep the retrieval order", lambda: [c["id"] for c in fn("rerank")("q", [dict(c) for c in cands], lambda q, t: 5.0, top_n=4)] == ["a", "b", "c", "d"])
