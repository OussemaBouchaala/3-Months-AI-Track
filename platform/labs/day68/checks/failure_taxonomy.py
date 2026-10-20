cl = fn("classify")
base = {"type": "answer", "said_idk": False, "gold_retrieved": True, "correct": True, "citation_ok": True}
check("a good answer is ok", lambda: cl(base) == "ok")
check("retrieval miss comes first, even if it also said idk", lambda: cl(dict(base, gold_retrieved=False, said_idk=True)) == "retrieval_miss")
check("false_idk, wrong_answer, bad_citation in order", lambda: cl(dict(base, said_idk=True, correct=False)) == "false_idk" and cl(dict(base, correct=False, citation_ok=False)) == "wrong_answer" and cl(dict(base, citation_ok=False)) == "bad_citation")
check("idk questions: ok or invented_answer", lambda: cl({"type": "idk", "said_idk": True}) == "ok" and cl({"type": "idk", "said_idk": False, "gold_retrieved": False}) == "invented_answer")
check("action questions: ok or action_error", lambda: cl({"type": "action", "action_ok": True}) == "ok" and cl({"type": "action", "action_ok": False}) == "action_error")
C = ([dict(base, id=f"r{i}", lang="derja", gold_retrieved=False) for i in range(4)] + [dict(base, id=f"w{i}", lang="fr", correct=False) for i in range(2)]
     + [{"type": "idk", "said_idk": False, "id": "i1", "lang": "en"}, {"type": "idk", "said_idk": True, "id": "i2", "lang": "en"}]
     + [dict(base, id=f"ok{i}", lang="fr") for i in range(4)] + [dict(base, id="b1", lang="fr", citation_ok=False)])
tx = fn("taxonomy")
check("taxonomy: failures only, most common first, ties by category order", lambda: list(tx(C).items()) == [("retrieval_miss", 4), ("wrong_answer", 2), ("invented_answer", 1), ("bad_citation", 1)])
pr = fn("pareto")
check("pareto: cumulative share", lambda: pr(tx(C)) == [("retrieval_miss", 4, 0.5), ("wrong_answer", 2, 0.75), ("invented_answer", 1, 0.88), ("bad_citation", 1, 1.0)])
fr = fn("failure_rate_by")
check("failure_rate_by language", lambda: fr(C, "lang") == {"derja": 1.0, "en": 0.5, "fr": 0.43})
ex = fn("examples")
check("examples: first n ids of a label", lambda: ex(C, "retrieval_miss", 2) == ["r0", "r1"] and ex(C, "false_idk") == [])
