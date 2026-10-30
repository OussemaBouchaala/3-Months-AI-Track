"""Week 4's evaluation, re-run on real Arabic.

Does normalization + stemming + hybrid search actually help on Arabic? ARCD's questions
come with their source paragraph, so the test set is free: for each question, did search
find the right paragraph?

1. `sample_questions`: a random but **reproducible** sample.
2. `doc_ranking`: from a ranking of chunks to a ranking of documents.
3. `doc_recall_at_k`: did the right document appear in the top k?
4. `answer_found`: is the short gold answer inside the model's answer?
5. `compare_table`: the variants side by side, with the gain over the baseline.

Running the file compares 4 variants on a small built-in example. `run_on_arcd()` runs
the real comparison on 100 ARCD questions (needs days 16, 20, 36-40).
"""
import random


def sample_questions(questions, n, seed=0):
    """`n` questions picked at random, the same ones every time for the same seed.

    `random.Random(seed)` is a random generator of its own: with a fixed seed,
    every run (and every variant) is tested on the **same** questions, so the
    comparison is fair.

    Example:
        >>> qs = list(range(50))
        >>> sample_questions(qs, 5, seed=1) == sample_questions(qs, 5, seed=1)
        True
        >>> sample_questions(qs, 5, seed=1) == sample_questions(qs, 5, seed=2)
        False
        >>> len(sample_questions(qs, 80))
        50
    """
    return list(questions) if n >= len(questions) else random.Random(seed).sample(questions, n)


def doc_ranking(chunk_ids):
    """Turn a ranking of chunks into a ranking of documents, without duplicates.

    Search returns chunks, but ARCD labels documents. Several chunks can come
    from the same document; a document's rank is that of its **first** chunk.

    Example:
        >>> doc_ranking(["d3-c0", "d7-c2", "d3-c1", "d9-c0"])
        ['d3', 'd7', 'd9']
    """
    out = []
    for c in chunk_ids:
        d = c.rsplit("-c", 1)[0]
        if d not in out:
            out.append(d)
    return out


def doc_recall_at_k(chunk_ids, source_doc_ids, k):
    """The share of the right documents found in the top `k` documents.

    Counting documents, not chunks: 3 chunks of the same wrong document must
    not push the right one out of the top k by themselves.

    Example:
        >>> doc_recall_at_k(["d3-c0", "d3-c1", "d3-c2", "d9-c0"], ["d9"], k=2)
        1.0
        >>> doc_recall_at_k(["d3-c0", "d4-c0", "d9-c0"], ["d9"], k=2)
        0.0
    """
    return len(set(source_doc_ids) & set(doc_ranking(chunk_ids)[:k])) / len(source_doc_ids)


def answer_found(prediction, gold, norm=lambda s: s):
    """True if the short gold answer appears inside the model's answer.

    ARCD answers are short spans copied from the paragraph, so "is it
    inside?" is a fair test. Pass a `norm` function (like day 37's
    `normalize_arabic`) so أحمد in one and احمد in the other still match.

    Example:
        >>> answer_found("عاصمة تونس هي مدينة تونس.", "مدينة تونس")
        True
        >>> answer_found("ذهب أحمد", "احمد"), answer_found("ذهب أحمد", "احمد", norm=lambda s: s.replace("أ", "ا"))
        (False, True)
    """
    return bool(gold.strip()) and norm(gold) in norm(prediction)


def compare_table(rows, baseline):
    """A Markdown table of the variants, with the recall@5 change versus the baseline.

    `:+.2f` always prints the sign, so gains (+0.07) and losses (-0.02)
    stand out.

    Example:
        >>> rows = [{"variant": "bm25 raw", "recall@1": 0.41, "recall@5": 0.62},
        ...         {"variant": "bm25 stemmed", "recall@1": 0.5, "recall@5": 0.69}]
        >>> print(compare_table(rows, "bm25 raw"))
        | variant | recall@1 | recall@5 | Δ recall@5 |
        |---|---|---|---|
        | bm25 raw | 0.41 | 0.62 | +0.00 |
        | bm25 stemmed | 0.50 | 0.69 | +0.07 |
        <BLANKLINE>
    """
    base = next(r for r in rows if r["variant"] == baseline)["recall@5"]
    out = "| variant | recall@1 | recall@5 | Δ recall@5 |\n|---|---|---|---|\n"
    for r in rows:
        out += f"| {r['variant']} | {r['recall@1']:.2f} | {r['recall@5']:.2f} | {r['recall@5'] - base:+.2f} |\n"
    return out


def evaluate(variants, questions):
    """recall@1 and recall@5 for each retrieval variant, as rows for `compare_table`."""
    rows = []
    for name, retrieve in variants.items():
        r1, r5 = [], []
        for q in questions:
            got = retrieve(q["question"])
            r1.append(doc_recall_at_k(got, q["source_ids"], 1))
            r5.append(doc_recall_at_k(got, q["source_ids"], 5))
        rows.append({"variant": name, "recall@1": sum(r1) / len(r1), "recall@5": sum(r5) / len(r5)})
    return rows


def run_on_arcd():
    """The real comparison on 100 ARCD questions: raw BM25, normalized+stemmed BM25,
    bge-m3 vectors, and hybrid. Writes `arabic_results.md`."""
    import json
    import sys

    import numpy as np

    sys.path += ["../day16", "../day20", "../day36", "../day37", "../day38"]
    import hybrid
    from arabic_keywords import tokenize_ar
    from embed import embed, normalize, search
    from hybrid import rrf
    from load_corpus import load_jsonl

    chunks = json.load(open("../day40/arcd_chunks.json", encoding="utf-8"))
    matrix = np.load("../day40/arcd_embeddings.npy")
    ids = [c["id"] for c in chunks]
    texts = [f"{c['title']}: {c['text']}" for c in chunks]
    qs = sample_questions(load_jsonl("../day36/arcd_questions.jsonl"), 100)

    def bm25_with(tokenizer):
        hybrid.tokenize = tokenizer                # reuse Week 3's BM25 with another tokenizer
        def run(q):
            scores = hybrid.bm25_scores(q, texts)
            return [ids[i] for i in np.argsort(-np.array(scores))]
        return run

    raw, stemmed = bm25_with(lambda t: t.lower().split()), bm25_with(tokenize_ar)
    vector = lambda q: [ids[i] for i, _ in search(normalize(embed([q]))[0], matrix, k=50)]
    variants = {"bm25 raw": raw, "bm25 normalized+stemmed": stemmed, "vector bge-m3": vector,
                "hybrid (stemmed + vector)": lambda q: rrf([stemmed(q)[:50], vector(q)])}
    table = compare_table(evaluate(variants, qs), baseline="bm25 raw")
    print(table)
    open("arabic_results.md", "w", encoding="utf-8").write(table)


if __name__ == "__main__":
    import re

    # A tiny corpus: 4 paragraphs, 4 questions typed the way people really type.
    chunks = {"d0-c0": "المدرسة الكبيرة في صفاقس تفتح أبوابها في سبتمبر",
              "d1-c0": "مستشفى سوسة الجامعي يستقبل المرضى كل يوم",
              "d2-c0": "تأسست القيروان سنة ٦٧٠ ميلادية",
              "d3-c0": "الطلاب والمعلمون في تونس العاصمة"}
    questions = [{"question": "متى تفتح المدارس في صفاقس", "source_ids": ["d0"]},
                 {"question": "مستشفي سوسه", "source_ids": ["d1"]},
                 {"question": "متى تأسست القيروان 670", "source_ids": ["d2"]},
                 {"question": "طالب في تونس", "source_ids": ["d3"]}]

    def keyword_search(tokenize):
        def run(q):
            qt = set(tokenize(q))
            return sorted(chunks, key=lambda cid: -len(qt & set(tokenize(chunks[cid]))))
        return run

    def raw_tokens(t):
        return re.findall(r"\w+", t)

    def normalized_stemmed(t):
        t = re.sub("[أإآ]", "ا", t).replace("ى", "ي").replace("ة", "ه")
        t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
        words = re.findall(r"\w+", t)
        return [re.sub("^(وال|بال|ال|و)", "", w) if len(w) > 4 else w for w in words]

    rows = evaluate({"keywords raw": keyword_search(raw_tokens),
                     "keywords normalized+stemmed": keyword_search(normalized_stemmed)}, questions)
    print(compare_table(rows, baseline="keywords raw"))
