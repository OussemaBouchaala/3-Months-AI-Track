# The golden set: YOUR project's exam, built from the interview's real questions.
# Every number in Weeks 8-10 is computed on it, so it deserves a Saturday.
import random
import re
from collections import Counter

LANGS = {"ar", "fr", "en", "derja", "arabizi"}
TYPES = {"answer", "idk", "action"}      # idk: the documents don't answer it; action: needs a tool

GOLDEN = [
    # TODO: at least 20 items from your interview (and variations of them). Example:
    {"id": "q01", "question": "Combien de mois de caution pour une location à l'année ?", "lang": "fr",
     "category": "deposit", "type": "answer", "expected": "2 mois de loyer", "source": "handbook#c2"},
]


def validate_item(item):
    """List of error strings ([] if valid):
    - missing or empty id / question / category,
    - lang not in LANGS, type not in TYPES,
    - type "answer" without a non-empty "expected"."""
    # TODO
    ...


def norm_question(q):
    """lowercase, remove punctuation (anything that is not a letter, digit or space), collapse spaces, strip."""
    # TODO
    ...


def dedupe(items):
    """Keep the first item of each normalized question, in order."""
    # TODO
    ...


def coverage(items, key):
    """{value: count} for items[key], most common first (a plain dict built from Counter.most_common())."""
    # TODO
    ...


def split_dev_test(items, test_share=0.3, seed=0):
    """Stratified by category. For each category (sorted by name): shuffle its items with random.Random(seed),
    put round(n * test_share) of them in test (at least 1 when n >= 2), the rest in dev.
    Return (dev, test). Same seed -> same split."""
    # TODO
    ...


def gaps(items, min_per_category=3, min_langs=2, min_idk=2):
    """Human-readable problems with the set as a whole, e.g. "category 'pets' has 1 item (< 3)",
    "only 1 language", "only 0 'idk' items". [] when the set is fine."""
    # TODO
    ...


if __name__ == "__main__":
    import json
    bad = {i.get("id"): validate_item(i) for i in GOLDEN if validate_item(i)}
    print("invalid:", bad or "none")
    items = dedupe(GOLDEN)
    print("langs:", coverage(items, "lang"), "categories:", coverage(items, "category"))
    print("gaps:", gaps(items) or "none")
    dev, test = split_dev_test(items)
    for name, part in (("golden_dev.jsonl", dev), ("golden_test.jsonl", test)):
        with open(name, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(i, ensure_ascii=False) + "\n" for i in part)
    print(len(dev), "dev /", len(test), "test. Don't look at test until Week 10.")
