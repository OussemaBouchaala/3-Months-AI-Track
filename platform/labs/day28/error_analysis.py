"""Why does it fail?

Numbers say **how much** fails ("correct 0.78"). Error analysis says **why**, so you know
what to fix next. Every answer goes into exactly one bucket, and the biggest
non-ok bucket is the next thing to work on.

1. `bucket`: decides the one bucket of a single answer.
2. `bucket_counts`: how many answers fall in each bucket.
3. `examples`: a few real questions from one bucket, to read.
4. `top_problem`: the biggest bucket that isn't "ok".

Running the file uses 10 example answers. `run_on_my_results()` reads the real log
saved by day 27's harness.
"""
from collections import Counter

IDK = "I don't know based on the documents."
BUCKETS = ("ok", "retrieval_miss", "generation_error", "false_idk", "invented_answer", "unsupported_claim")


def bucket(item, result):
    """The one bucket an answer falls in. The **first rule that matches wins**, so the order matters.

    - **Unanswerable** item (no `source_ids`): saying "I don't know" is right
      (`ok`); anything else is an `invented_answer`.
    - Answerable but the model said "I don't know": `false_idk` (too cautious).
    - None of the right chunks were retrieved: `retrieval_miss`. The model
      never had a chance, so fix search, not the prompt.
    - Correct and faithful: `ok`.
    - Correct but not faithful: `unsupported_claim`. Right by luck or from
      training data, not from your documents.
    - Otherwise: `generation_error`. The right chunk was there and the answer
      is still wrong, so fix the prompt or the model.

    Example:
        >>> answerable = {"source_ids": ["c1"]}
        >>> bucket(answerable, {"answer": "Opens at 9 [1]", "retrieved": ["c1"], "correct": 1, "faithful": 1})
        'ok'
        >>> bucket(answerable, {"answer": "Opens at 8 [1]", "retrieved": ["c7"], "correct": 0, "faithful": 0})
        'retrieval_miss'
        >>> bucket(answerable, {"answer": IDK, "retrieved": ["c1"], "correct": 0, "faithful": 1})
        'false_idk'
        >>> bucket({"source_ids": []}, {"answer": "Yes, we sell cars", "retrieved": ["c2"], "correct": 0, "faithful": 0})
        'invented_answer'
    """
    idk = IDK in result["answer"]
    if not item["source_ids"]:
        return "ok" if idk else "invented_answer"
    if idk:
        return "false_idk"
    if not set(item["source_ids"]) & set(result["retrieved"]):
        return "retrieval_miss"
    if result["correct"] and result["faithful"]:
        return "ok"
    if result["correct"]:
        return "unsupported_claim"
    return "generation_error"


def bucket_counts(items, results):
    """How many answers fall in each bucket, with every bucket listed (0 if empty).

    `Counter` counts the buckets. The dict comprehension then lists them in
    the fixed `BUCKETS` order and fills in 0 for buckets nobody fell into, so
    the report always has the same rows.

    Example:
        >>> items = [{"source_ids": ["c1"]}, {"source_ids": ["c2"]}, {"source_ids": []}]
        >>> results = [{"answer": "a", "retrieved": ["c1"], "correct": 1, "faithful": 1},
        ...            {"answer": "b", "retrieved": ["c9"], "correct": 0, "faithful": 0},
        ...            {"answer": IDK, "retrieved": [], "correct": 1, "faithful": 1}]
        >>> bucket_counts(items, results)
        {'ok': 2, 'retrieval_miss': 1, 'generation_error': 0, 'false_idk': 0, 'invented_answer': 0, 'unsupported_claim': 0}
    """
    c = Counter(bucket(i, r) for i, r in zip(items, results))
    return {name: c.get(name, 0) for name in BUCKETS}


def examples(items, results, name, n=3):
    """The first `n` questions that fall in bucket `name`, to read them yourself.

    Counts tell you which bucket to fix; reading 3 real examples tells you **how**.

    Example:
        >>> items = [{"question": "Opening hours?", "source_ids": ["c1"]},
        ...          {"question": "Parking?", "source_ids": ["c2"]}]
        >>> results = [{"answer": "x", "retrieved": ["c5"], "correct": 0, "faithful": 0},
        ...            {"answer": "y", "retrieved": ["c6"], "correct": 0, "faithful": 0}]
        >>> examples(items, results, "retrieval_miss", n=1)
        ['Opening hours?']
    """
    return [i["question"] for i, r in zip(items, results) if bucket(i, r) == name][:n]


def top_problem(counts):
    """The non-"ok" bucket with the most answers: what to fix first. `None` if all are ok.

    `max(bad, key=bad.get)` returns the key with the highest count.

    Example:
        >>> top_problem({"ok": 40, "retrieval_miss": 6, "false_idk": 3})
        'retrieval_miss'
        >>> print(top_problem({"ok": 50, "retrieval_miss": 0}))
        None
    """
    bad = {k: v for k, v in counts.items() if k != "ok" and v > 0}
    return max(bad, key=bad.get) if bad else None


def run_on_my_results():
    """The same report on your real results: the test set from day 22 and the
    per-question log that day 27's harness saved for the best config."""
    import json

    items = json.load(open("../day22/testset_v1.json", encoding="utf-8"))
    results = json.load(open("../day27/per_question.json", encoding="utf-8"))
    report(items, results)


def report(items, results):
    """Print the count and 2 example questions for every bucket, then what to fix first."""
    counts = bucket_counts(items, results)
    for name in BUCKETS:
        print(f"{name:<18} {counts[name]:>3}  e.g. {examples(items, results, name, 2)}")
    print("fix first:", top_problem(counts))


if __name__ == "__main__":
    # 10 example answers from a shop's FAQ bot.
    Q = lambda q, src: {"question": q, "source_ids": src}
    R = lambda ans, ret, c, f: {"answer": ans, "retrieved": ret, "correct": c, "faithful": f}
    items = [Q("Opening hours?", ["c1"]), Q("Do you deliver to Sfax?", ["c2"]), Q("Return policy?", ["c3"]),
             Q("Price of the blue mug?", ["c4"]), Q("Do you sell cars?", []), Q("Gift cards?", ["c6"]),
             Q("Parking nearby?", ["c7"]), Q("Who is the CEO?", []), Q("Student discount?", ["c9"]),
             Q("Phone number?", ["c10"])]
    results = [R("9am to 7pm [1]", ["c1"], 1, 1), R("Yes, in 2 days [1]", ["c5"], 0, 0),
               R("30 days with receipt [1]", ["c3"], 1, 1), R("12 TND [1]", ["c4"], 0, 1),
               R(IDK, [], 1, 1), R(IDK, ["c6"], 0, 1), R("Yes, behind the shop [1]", ["c8"], 0, 0),
               R("Mr. Ben Ali [1]", ["c1"], 0, 0), R("10% with a card", ["c9"], 1, 0), R("71 000 000 [1]", ["c3"], 0, 0)]
    report(items, results)
