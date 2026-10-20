vi = fn("validate_item")
good = {"id": "a", "question": "Q?", "lang": "fr", "category": "c", "type": "answer", "expected": "x"}
check("validate_item accepts a valid item", lambda: vi(good) == [])
check("validate_item flags bad lang, bad type, missing question", lambda: len(vi(dict(good, lang="de", type="maybe", question=""))) == 3)
check("an 'answer' needs expected; an 'idk' doesn't", lambda: vi(dict(good, expected="")) != [] and vi(dict(good, type="idk", expected="")) == [])
nq = fn("norm_question")
check("norm_question: case, punctuation, spaces", lambda: nq("  Combien   de caution ?! ") == "combien de caution" and nq("شنوة الضمان؟") == "شنوة الضمان")
dd = fn("dedupe")
check("dedupe keeps the first of near-duplicates", lambda: [i["id"] for i in dd([dict(good, id="1", question="Prix ?"), dict(good, id="2", question="prix"), dict(good, id="3", question="Frais")])] == ["1", "3"])
cv = fn("coverage")
check("coverage counts, most common first", lambda: list(cv([{"c": "x"}, {"c": "y"}, {"c": "y"}], "c").items()) == [("y", 2), ("x", 1)])
sp = fn("split_dev_test")
items = [dict(good, id=f"{c}{n}", category=c) for c, k in (("a", 10), ("b", 3), ("c", 1)) for n in range(k)]
def _split():
    dev, test = sp(items, 0.3, seed=1)
    ids = [i["id"] for i in dev + test]
    return len(ids) == len(set(ids)) == 14 and sum(i["category"] == "a" for i in test) == 3 and sum(i["category"] == "b" for i in test) == 1 and sum(i["category"] == "c" for i in test) == 0
check("split is stratified by category, no overlap", _split)
check("split is reproducible with the seed", lambda: sp(items, 0.3, 4) == sp(items, 0.3, 4))
gp = fn("gaps")
check("gaps reports small categories, languages and idk", lambda: len(gp(items, 3, 2, 2)) == 3 and any("'c'" in g for g in gp(items, 3, 2, 2)))
G = lambda: var("GOLDEN")
check("GOLDEN: at least 20 valid items", lambda: len(G()) >= 20 and all(vi(i) == [] for i in G()))
check("GOLDEN: at least 2 languages, 2 'idk' items, unique ids", lambda: len({i["lang"] for i in G()}) >= 2 and sum(i["type"] == "idk" for i in G()) >= 2 and len({i["id"] for i in G()}) == len(G()))
