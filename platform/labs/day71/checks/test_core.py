import math, re, sys
import core as _core
tests = {k: v for k, v in ns.items() if k.startswith("test_") and callable(v)}
def run_all():
    bad = []
    for name, t in tests.items():
        try:
            t()
        except Exception as e:
            bad.append(name)
    return bad
check("at least 9 test functions", lambda: len(tests) >= 9)
check("every test passes on the real core.py", lambda: tests and run_all() == [] or (_ for _ in ()).throw(CheckFailed(f"failing: {run_all()}")))

def _norm_no_alef(text):
    text = _core.DIACRITICS.sub("", text).replace("ـ", "")
    return text.replace("ة", "ه").replace("ى", "ي")
def _norm_no_diac(text):
    text = re.sub("[أإآ]", "ا", text.replace("ـ", ""))
    return text.replace("ة", "ه").replace("ى", "ي")
def _norm_no_taa(text):
    text = _core.DIACRITICS.sub("", text).replace("ـ", "")
    return re.sub("[أإآ]", "ا", text).replace("ى", "ي")
def _chunk_no_overlap(sentences, max_chars=500, overlap=1):
    return _core.chunk_sentences(sentences, max_chars, 0)
def _chunk_split_long(sentences, max_chars=500, overlap=1):
    out = []
    for c in _core.chunk_sentences(sentences, max_chars, overlap):
        out += [c[i:i + max_chars] for i in range(0, len(c), max_chars)]
    return out
def _cite_keep_zero(answer, n):
    removed = sorted({int(k) for k in re.findall(r"\[(\d+)\]", answer) if int(k) > n})
    return re.sub(r"\[(\d+)\]", lambda m: m.group() if int(m.group(1)) <= n else "", answer), removed
def _phones_loose(text):
    return re.sub(r"(?:(?:\+|00)216[ .]?)?\d{2}(?:[ .]?\d{3}){2}", "[PHONE]", text)
def _pct_round(values, p):
    if not values:
        return None
    s = sorted(values)
    return s[max(0, min(len(s) - 1, round(p / 100 * len(s))))]
MUTANTS = [("normalize_arabic", _norm_no_alef, "alef variants not normalized"),
           ("normalize_arabic", _norm_no_diac, "diacritics kept"),
           ("normalize_arabic", _norm_no_taa, "taa marbuta kept"),
           ("chunk_sentences", _chunk_no_overlap, "overlap ignored"),
           ("chunk_sentences", _chunk_split_long, "long sentences cut in pieces"),
           ("clean_citations", _cite_keep_zero, "[0] kept as a valid citation"),
           ("mask_phones", _phones_loose, "masks CINs and pieces of long numbers"),
           ("percentile", _pct_round, "rounds instead of nearest rank")]
def survivors():
    alive = []
    for name, mutant, what in MUTANTS:
        saved_ns, saved_mod = ns.get(name), getattr(_core, name)
        ns[name] = mutant
        setattr(_core, name, mutant)
        try:
            if not run_all():
                alive.append(what)
        finally:
            ns[name] = saved_ns
            setattr(_core, name, saved_mod)
    return alive
def _killed(group):
    def f():
        alive = [w for w in survivors() if w in group]
        if alive:
            raise CheckFailed("your tests still pass with this bug: " + "; ".join(alive))
        return True
    return f
check("catches broken Arabic normalization (alef, diacritics, taa marbuta)", _killed({"alef variants not normalized", "diacritics kept", "taa marbuta kept"}))
check("catches broken chunking (overlap, long sentences)", _killed({"overlap ignored", "long sentences cut in pieces"}))
check("catches a citation bug ([0] kept)", _killed({"[0] kept as a valid citation"}))
check("catches a phone regex that masks CINs", _killed({"masks CINs and pieces of long numbers"}))
check("catches a percentile off-by-one", _killed({"rounds instead of nearest rank"}))
