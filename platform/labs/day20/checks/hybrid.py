import math
from collections import Counter

check("tokenize lowercases and keeps Arabic", lambda: fn("tokenize")("CIN, Passport! الضمان 2") == ["cin", "passport", "الضمان", "2"])

docs = ["the deposit is two months", "visits are free free free", "the deposit returns in 30 days after the keys", "pets"]


def ref_bm25(query, docs, k1=1.5, b=0.75):
    tok = lambda t: __import__("re").findall(r"\w+", t.lower())
    D = [tok(d) for d in docs]
    N, avg = len(D), sum(map(len, D)) / len(D)
    out = []
    for d in D:
        tf, s = Counter(d), 0.0
        for t in set(tok(query)):
            df = sum(t in x for x in D)
            if df == 0:
                continue
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avg))
        out.append(s)
    return out


bm = lambda q: fn("bm25_scores")(q, docs)
check("bm25 returns one score per doc", lambda: len(bm("deposit")) == 4)
check("docs without the term score 0", lambda: bm("deposit")[1] == 0 and bm("deposit")[3] == 0)
check("the shorter doc with the term scores higher (length normalization)", lambda: bm("deposit")[0] > bm("deposit")[2])
check("scores match the BM25 formula", lambda: all(abs(a - b) < 1e-9 for a, b in zip(bm("deposit keys"), ref_bm25("deposit keys", docs))),
      "idf = ln((N - df + 0.5) / (df + 0.5) + 1); tf part = tf*(k1+1) / (tf + k1*(1 - b + b*len/avgdl))")
check("repeated query terms count once", lambda: len(bm("free")) == 4 and bm("free free") == bm("free"))
check("a term in no doc adds nothing", lambda: len(bm("deposit")) == 4 and bm("deposit zzz") == bm("deposit"))
check("rank_ids sorts best first", lambda: fn("rank_ids")(["a", "b", "c"], [0.1, 2.0, 0.5]) == ["b", "c", "a"])
r = fn("rrf")
check("rrf: consistently high beats once-first", lambda: r([["a", "b", "c", "d"], ["b", "d", "a", "c"]])[0] == "b")
check("rrf includes ids missing from one ranking", lambda: sorted(r([["a", "b"], ["c"]])) == ["a", "b", "c"])
check("rrf uses 1/(k+rank) with rank from 1", lambda: r([["x", "y"], ["y", "z"]], k=1)[:2] == ["y", "x"])
