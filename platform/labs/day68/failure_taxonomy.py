""""78% correct" doesn't tell you what to fix.

Label every failure with **one** cause, count them, and fix the top one first. Rules
first: cheap, explainable, and the same every run. Then read a few examples of each
label to make sure the rules are right.

1. `CATEGORIES`: the possible causes, in pipeline order.
2. `classify`: one case -> one label (or "ok").
3. `taxonomy` and `pareto`: counts, and how much the top causes explain.
4. `failure_rate_by`: where it fails (language, document type...).
5. `examples`: ids to read by hand.
"""
from collections import Counter

CATEGORIES = ["retrieval_miss", "false_idk", "invented_answer", "wrong_answer", "bad_citation", "action_error"]


def classify(case):
    """The **first** thing that went wrong in a case, following the pipeline.

    - Action questions: did the action succeed?
    - Questions with no answer in the documents (`type: "idk"`): saying
      "I don't know" is right; anything else is an invented answer.
    - Answerable questions, in pipeline order: the right chunk wasn't
      retrieved (the model never had a chance), then a wrong "I don't
      know", then a wrong answer, then a bad citation.

    Checking in that order gives the **root** cause: a retrieval miss that
    also led to "I don't know" is a retrieval problem.

    Example:
        >>> base = {"type": "answer", "said_idk": False, "gold_retrieved": True, "correct": True, "citation_ok": True}
        >>> classify(base)
        'ok'
        >>> classify(dict(base, gold_retrieved=False, said_idk=True))
        'retrieval_miss'
        >>> classify(dict(base, citation_ok=False)), classify({"type": "idk", "said_idk": False})
        ('bad_citation', 'invented_answer')
    """
    if case["type"] == "action":
        return "ok" if case.get("action_ok") else "action_error"
    if case["type"] == "idk":
        return "ok" if case["said_idk"] else "invented_answer"
    if not case["gold_retrieved"]:
        return "retrieval_miss"
    if case["said_idk"]:
        return "false_idk"
    if not case["correct"]:
        return "wrong_answer"
    if not case["citation_ok"]:
        return "bad_citation"
    return "ok"


def taxonomy(cases):
    """`{label: count}` for failures only, most common first.

    `Counter` counts the labels; `pop("ok")` drops the successes. The sort
    key `(-count, position in CATEGORIES)` breaks ties in pipeline order.

    Example:
        >>> base = {"type": "answer", "said_idk": False, "gold_retrieved": True, "correct": True, "citation_ok": True}
        >>> cases = [dict(base, gold_retrieved=False)] * 4 + [dict(base, correct=False)] * 2 + [base] * 5 + [dict(base, citation_ok=False)]
        >>> taxonomy(cases)
        {'retrieval_miss': 4, 'wrong_answer': 2, 'bad_citation': 1}
    """
    c = Counter(classify(x) for x in cases)
    c.pop("ok", None)
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], CATEGORIES.index(kv[0]))))


def pareto(counts):
    """Each label with its count and the **cumulative** share of all failures.

    Usually the top one or two causes explain most failures ("fix retrieval
    and half the failures go away"). This makes that visible.

    Example:
        >>> pareto({"retrieval_miss": 4, "wrong_answer": 2, "invented_answer": 1, "bad_citation": 1})
        [('retrieval_miss', 4, 0.5), ('wrong_answer', 2, 0.75), ('invented_answer', 1, 0.88), ('bad_citation', 1, 1.0)]
    """
    total = sum(counts.values())
    out, run = [], 0
    for label, n in counts.items():
        run += n
        out.append((label, n, round(run / total, 2)))
    return out


def failure_rate_by(cases, key):
    """The share of failed cases per value of `key` (e.g. `"lang"`).

    `classify(x) != "ok"` is True/False, and the mean of booleans is the
    share of True. This is how you find "Derja fails 3 times more than French".

    Example:
        >>> base = {"type": "answer", "said_idk": False, "gold_retrieved": True, "correct": True, "citation_ok": True}
        >>> cases = [dict(base, lang="derja", correct=False), dict(base, lang="derja"), dict(base, lang="fr")]
        >>> failure_rate_by(cases, "lang")
        {'derja': 0.5, 'fr': 0.0}
    """
    groups = {}
    for x in cases:
        groups.setdefault(x[key], []).append(classify(x) != "ok")
    return {k: round(sum(v) / len(v), 2) for k, v in sorted(groups.items())}


def examples(cases, label, n=3):
    """The ids of the first `n` cases with a label: open them and read.
    If the examples don't fit the label, fix the rules, not the counts.

    Example:
        >>> cases = [{"id": "q1", "type": "idk", "said_idk": False}, {"id": "q2", "type": "idk", "said_idk": True}]
        >>> examples(cases, "invented_answer"), examples(cases, "false_idk")
        (['q1'], [])
    """
    return [x["id"] for x in cases if classify(x) == label][:n]


def print_report(cases):
    """The whole analysis: Pareto table with examples, then rates by language
    and by document type.

    Example:
        >>> print_report([{"id": "q1", "lang": "fr", "type": "idk", "said_idk": False}])
        invented_answer    1  cumulative 100%   e.g. ['q1']
        failure rate by language: {'fr': 1.0}
        failure rate by doc type: add doc_type to see it
    """
    for label, n, cum in pareto(taxonomy(cases)):
        print(f"{label:16} {n:3}  cumulative {cum:.0%}   e.g. {examples(cases, label)}")
    print("failure rate by language:", failure_rate_by(cases, "lang"))
    print("failure rate by doc type:", failure_rate_by(cases, "doc_type") if cases and "doc_type" in cases[0] else "add doc_type to see it")


if __name__ == "__main__":
    import json
    import random
    from pathlib import Path
    real = Path("../day64/per_question.jsonl")
    if real.exists():
        print_report([json.loads(l) for l in real.read_text(encoding="utf-8").splitlines() if l.strip()])
    else:
        # Demo: 60 simulated cases where Derja questions often miss retrieval.
        rng = random.Random(4)
        cases = []
        for i in range(60):
            lang, doc = rng.choice(["fr", "fr", "ar", "derja"]), rng.choice(["contract", "faq", "scan"])
            kind = "idk" if i % 10 == 0 else "action" if i % 10 == 1 else "answer"
            cases.append({"id": f"q{i:02}", "lang": lang, "doc_type": doc, "type": kind,
                          "said_idk": kind == "idk" and rng.random() < 0.7 or rng.random() < 0.05,
                          "gold_retrieved": rng.random() > (0.45 if lang == "derja" else 0.12 if doc == "scan" else 0.05),
                          "correct": rng.random() < 0.94, "citation_ok": rng.random() < 0.96, "action_ok": rng.random() < 0.8})
        print_report(cases)
