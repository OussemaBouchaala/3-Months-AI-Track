IDK = var("IDK")
b = fn("bucket")
A = {"question": "q", "source_ids": ["c1"], "answer": "x"}
U = {"question": "u", "source_ids": [], "answer": ""}
R = lambda answer="ans [1]", retrieved=("c1",), correct=1, faithful=1: {"answer": answer, "retrieved": list(retrieved), "correct": correct, "faithful": faithful}
check("unanswerable + IDK -> ok", lambda: b(U, R(IDK, ())) == "ok")
check("unanswerable + answer -> invented_answer", lambda: b(U, R("Yes [1]", ("c2",), 0, 0)) == "invented_answer")
check("answerable + IDK -> false_idk (even if retrieval missed)", lambda: b(A, R(IDK, ("c9",), 0, 1)) == "false_idk")
check("source not retrieved -> retrieval_miss", lambda: b(A, R(retrieved=("c2", "c3"), correct=0, faithful=0)) == "retrieval_miss")
check("retrieved, correct, faithful -> ok", lambda: b(A, R()) == "ok")
check("correct but not faithful -> unsupported_claim", lambda: b(A, R(faithful=0)) == "unsupported_claim")
check("retrieved but wrong -> generation_error", lambda: b(A, R(correct=0, faithful=1)) == "generation_error")

items = [A, A, A, U]
results = [R(), R(retrieved=("c5",), correct=0), R(retrieved=("c7",), correct=0), R("We sell cars", ("c1",), 0, 0)]
check("bucket_counts has every bucket", lambda: fn("bucket_counts")(items, results) ==
      {"ok": 1, "retrieval_miss": 2, "generation_error": 0, "false_idk": 0, "invented_answer": 1, "unsupported_claim": 0})
check("examples returns the questions of a bucket", lambda: fn("examples")([{**A, "question": "q1"}, {**A, "question": "q2"}], [R(retrieved=()), R(retrieved=())], "retrieval_miss", n=1) == ["q1"])
tp = fn("top_problem")
check("top_problem ignores ok", lambda: tp({"ok": 40, "retrieval_miss": 6, "false_idk": 3}) == "retrieval_miss")
check("top_problem is None when all ok", lambda: tp({"ok": 50, "retrieval_miss": 0}) is None)
