sq = fn("sample_questions")
qs = [{"q": i} for i in range(50)]
check("sample_questions is reproducible and sized", lambda: sq(qs, 10, seed=1) == sq(qs, 10, seed=1) and len(sq(qs, 10)) == 10 and sq(qs, 10, 1) != sq(qs, 10, 2))
check("sample_questions with n >= len returns everything", lambda: sorted(x["q"] for x in sq(qs, 80)) == list(range(50)))
dr = fn("doc_ranking")
check("doc_ranking dedupes in first-seen order", lambda: dr(["d3-c0", "d7-c2", "d3-c1", "d9-c0", "d12-c4"]) == ["d3", "d7", "d9", "d12"])
dk = fn("doc_recall_at_k")
check("doc_recall_at_k counts documents, not chunks", lambda: dk(["d3-c0", "d3-c1", "d3-c2", "d9-c0"], ["d9"], 2) == 1.0 and dk(["d3-c0", "d3-c1", "d4-c0", "d9-c0"], ["d9"], 2) == 0.0)
af = fn("answer_found")
check("answer_found: span inside the prediction", lambda: af("عاصمة تونس هي مدينة تونس.", "مدينة تونس"))
check("answer_found uses norm on both sides", lambda: af("ذهب أحمد إلى المدرسة", "احمد", norm=lambda s: s.replace("أ", "ا")) and not af("ذهب أحمد", "احمد"))
check("empty gold -> False", lambda: af("anything", "") is False)
rows = [{"variant": "bm25 raw", "recall@1": 0.41, "recall@5": 0.62}, {"variant": "bm25 stemmed", "recall@1": 0.5, "recall@5": 0.69}, {"variant": "vector", "recall@1": 0.45, "recall@5": 0.6}]
ct = lambda: [l for l in fn("compare_table")(rows, "bm25 raw").strip().splitlines() if l.strip()]
check("compare_table: header, separator, one row per variant", lambda: len(ct()) == 5 and "Δ" in ct()[0])
check("deltas vs baseline with a sign", lambda: "+0.00" in ct()[2] and "+0.07" in ct()[3] and "-0.02" in ct()[4] and "0.69" in ct()[3])
