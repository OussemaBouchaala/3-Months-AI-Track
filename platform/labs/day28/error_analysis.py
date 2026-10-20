# Numbers say HOW MUCH fails. Error analysis says WHY, so you know what to fix next.
# Check uses hand-made results. Run reads the per-question log your harness saves (see the brief).
import json
from collections import Counter

IDK = "I don't know based on the documents."
BUCKETS = ("ok", "retrieval_miss", "generation_error", "false_idk", "invented_answer", "unsupported_claim")


def bucket(item, result):
    """item: test item. result: {"answer", "retrieved": [ids], "correct": 0/1, "faithful": 0/1}.
    Decide in THIS order:
      unanswerable item: "ok" if IDK in answer else "invented_answer"
      answerable and IDK in answer: "false_idk"
      none of the item's source_ids in retrieved: "retrieval_miss"
      correct == 1 and faithful == 1: "ok"
      correct == 1 and faithful == 0: "unsupported_claim"   (right by luck or from training data)
      otherwise: "generation_error"   (the right chunk was there, the answer is still wrong)"""
    # TODO
    ...


def bucket_counts(items, results):
    """Counter of buckets as a plain dict, every name in BUCKETS present (0 if none)."""
    # TODO
    ...


def examples(items, results, name, n=3):
    """The first n questions that fall in bucket `name`."""
    # TODO
    ...


def top_problem(counts):
    """The non-"ok" bucket with the most items. None if everything is ok."""
    # TODO
    ...


if __name__ == "__main__":
    items = json.load(open("../day22/testset_v1.json", encoding="utf-8"))
    results = json.load(open("../day27/per_question.json", encoding="utf-8"))   # one dict per item, same order
    counts = bucket_counts(items, results)
    for name in BUCKETS:
        print(f"{name:<18} {counts[name]:>3}  e.g. {examples(items, results, name, 2)}")
    print("fix first:", top_problem(counts))
