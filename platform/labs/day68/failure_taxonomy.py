# "78% correct" doesn't tell you what to fix. Label every failure with ONE cause, count them, and fix the top one.
# Rules first (cheap, explainable); read examples of each to make sure the labels are right.
from collections import Counter

CATEGORIES = ["retrieval_miss", "false_idk", "invented_answer", "wrong_answer", "bad_citation", "action_error"]


def classify(case):
    """case: {"type": "answer"|"idk"|"action", "said_idk": bool, "gold_retrieved": bool, "correct": bool,
    "citation_ok": bool, "action_ok": bool (only for type "action")}. Return ONE label, checked in this order:
    - type "action": "ok" if action_ok else "action_error"
    - type "idk": "ok" if said_idk else "invented_answer"
    - type "answer": not gold_retrieved -> "retrieval_miss"; said_idk -> "false_idk"; not correct -> "wrong_answer";
      not citation_ok -> "bad_citation"; else "ok"."""
    # TODO
    ...


def taxonomy(cases):
    """{label: count} for failures only (no "ok"), most common first; ties in CATEGORIES order."""
    # TODO
    ...


def pareto(counts):
    """[(label, count, cumulative share of all failures rounded to 2), ...] in the order of counts."""
    # TODO
    ...


def failure_rate_by(cases, key):
    """{value of case[key]: share of cases that are not "ok", rounded to 2}, values sorted."""
    # TODO
    ...


def examples(cases, label, n=3):
    """The first n cases' ids with that label."""
    # TODO
    ...


if __name__ == "__main__":
    import json
    cases = [json.loads(l) for l in open("../day64/per_question.jsonl", encoding="utf-8")]
    t = taxonomy(cases)
    for label, n, cum in pareto(t):
        print(f"{label:16} {n:3}  cumulative {cum:.0%}   e.g. {examples(cases, label)}")
    print("failure rate by language:", failure_rate_by(cases, "lang"))
    print("failure rate by doc type:", failure_rate_by(cases, "doc_type") if cases and "doc_type" in cases[0] else "add doc_type to see it")
