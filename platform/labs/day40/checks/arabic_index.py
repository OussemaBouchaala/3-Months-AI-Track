ss = fn("split_sentences")
check("splits on . ؟ ! ؛ and newlines", lambda: ss("تونس جميلة. هل زرت صفاقس؟ نعم! ثم\nسوسة؛ والمنستير") == ["تونس جميلة.", "هل زرت صفاقس؟", "نعم!", "ثم", "سوسة؛", "والمنستير"])
check("no empty pieces", lambda: ss("أ.  \n\n ب.") == ["أ.", "ب."])
cs = fn("chunk_sentences")
S = ["aaaa.", "bbbb.", "cccc.", "dddd."]          # 5 chars each; joined pairs are 11 chars
check("packs sentences up to max_chars", lambda: cs(S, max_chars=11, overlap=0) == ["aaaa. bbbb.", "cccc. dddd."])
check("overlap repeats the last sentence", lambda: cs(S, max_chars=11, overlap=1) == ["aaaa. bbbb.", "bbbb. cccc.", "cccc. dddd."])
check("a sentence longer than max_chars is its own chunk", lambda: cs(["x" * 30, "yy."], max_chars=10, overlap=0) == ["x" * 30, "yy."])
check("everything fits -> one chunk", lambda: cs(S, max_chars=500) == [" ".join(S)])
check("no chunk is only overlap", lambda: cs(S, max_chars=11, overlap=1)[-1] != "dddd." and all(len(c) > 5 for c in cs(S, max_chars=11, overlap=1)))
bc = fn("build_chunks")
docs = [{"id": "d0", "title": "تونس", "text": "aaaa. bbbb. cccc."}, {"id": "d1", "title": "صفاقس", "text": "zz."}]
check("build_chunks ids restart per doc and keep doc_id and title", lambda: [(c["id"], c["doc_id"], c["title"]) for c in bc(docs, max_chars=11, overlap=0)] == [("d0-c0", "d0", "تونس"), ("d0-c1", "d0", "تونس"), ("d1-c0", "d1", "صفاقس")])
check("doc_of", lambda: fn("doc_of")("d12-c3") == "d12")
