"""The golden set: your project's exam, built from the user interview's real questions.

Every number in weeks 8-10 is computed on this set, so it deserves care. Each item says
what is asked, in which language, what kind of answer is expected, and where the answer
lives in the documents.

- `type` "answer": the documents answer it; `expected` holds the key fact.
- `type` "idk": the documents don't answer it; the right reply is "I don't know".
- `type` "action": the user wants something done (a tool call).

1. `validate_item`: catch broken items early.
2. `norm_question` and `dedupe`: remove near-duplicate questions.
3. `coverage`: how many items per language or category.
4. `split_dev_test`: a dev part to tune on, a test part kept for the final score.
5. `gaps`: what the set as a whole is missing.
"""
import random
import re
from collections import Counter

LANGS = {"ar", "fr", "en", "derja", "arabizi"}
TYPES = {"answer", "idk", "action"}      # idk: the documents don't answer it; action: needs a tool

# 22 example items for the agency assistant, in 5 languages.
GOLDEN = [
    {"id": "q01", "question": "Combien de mois de caution pour une location à l'année ?", "lang": "fr", "category": "deposit", "type": "answer", "expected": "2 mois de loyer", "source": "handbook#c2"},
    {"id": "q02", "question": "شنوة الضمان كي نكري دار؟", "lang": "derja", "category": "deposit", "type": "answer", "expected": "شهرين", "source": "handbook#c2"},
    {"id": "q03", "question": "When do I get my deposit back?", "lang": "en", "category": "deposit", "type": "answer", "expected": "within 30 days", "source": "handbook#c2"},
    {"id": "q04", "question": "Kaddeh el commission ki nechri appart?", "lang": "arabizi", "category": "fees", "type": "answer", "expected": "2%", "source": "handbook#c0"},
    {"id": "q05", "question": "What is the agency fee when I buy?", "lang": "en", "category": "fees", "type": "answer", "expected": "2%", "source": "handbook#c0"},
    {"id": "q06", "question": "Frais d'agence pour une location saisonnière ?", "lang": "fr", "category": "fees", "type": "answer", "expected": "10%", "source": "handbook#c1"},
    {"id": "q07", "question": "Quels documents pour louer ?", "lang": "fr", "category": "documents", "type": "answer", "expected": "CIN", "source": "handbook#c5"},
    {"id": "q08", "question": "شنية الوثائق اللازمة باش نكري؟", "lang": "derja", "category": "documents", "type": "answer", "expected": "بطاقة التعريف", "source": "handbook#c5"},
    {"id": "q09", "question": "I'm a student, can I rent without payslips?", "lang": "en", "category": "documents", "type": "answer", "expected": "guarantee letter", "source": "handbook#c5"},
    {"id": "q10", "question": "Le loyer peut augmenter de combien ?", "lang": "fr", "category": "rent", "type": "answer", "expected": "5%", "source": "handbook#c6"},
    {"id": "q11", "question": "Can the rent go up in the first year?", "lang": "en", "category": "rent", "type": "answer", "expected": "no", "source": "handbook#c6"},
    {"id": "q12", "question": "كم يمكن الزيادة في معلوم الكراء؟", "lang": "ar", "category": "rent", "type": "answer", "expected": "5%", "source": "handbook#c6"},
    {"id": "q13", "question": "Réserver une visite samedi à 10h pour l'appartement S+2", "lang": "fr", "category": "visits", "type": "action", "expected": "book_visit", "source": ""},
    {"id": "q14", "question": "Can I visit on Sunday?", "lang": "en", "category": "visits", "type": "answer", "expected": "Monday to Saturday", "source": "handbook#c3"},
    {"id": "q15", "question": "نجم نبطل الزيارة ؟", "lang": "derja", "category": "visits", "type": "answer", "expected": "ساعتين", "source": "handbook#c4"},
    {"id": "q16", "question": "Est-ce que les animaux sont acceptés ?", "lang": "fr", "category": "pets", "type": "answer", "expected": "si le propriétaire l'autorise", "source": "handbook#c13"},
    {"id": "q17", "question": "Can I bring my dog to a residence with a pool?", "lang": "en", "category": "pets", "type": "answer", "expected": "no", "source": "handbook#c13"},
    {"id": "q18", "question": "واش القطط مسموحة؟", "lang": "derja", "category": "pets", "type": "answer", "expected": "إذا سمح المالك", "source": "handbook#c13"},
    {"id": "q19", "question": "Quel est le prix du m2 à Sahloul ?", "lang": "fr", "category": "out_of_scope", "type": "idk", "expected": "", "source": ""},
    {"id": "q20", "question": "Do you sell cars?", "lang": "en", "category": "out_of_scope", "type": "idk", "expected": "", "source": ""},
    {"id": "q21", "question": "شكون رئيس البلدية؟", "lang": "derja", "category": "out_of_scope", "type": "idk", "expected": "", "source": ""},
    {"id": "q22", "question": "combien de mois de caution pour une location a l'annee", "lang": "fr", "category": "deposit", "type": "answer", "expected": "2 mois", "source": "handbook#c2"},
]



def validate_item(item):
    """The problems of one item, as a list of messages (`[]` = valid).

    Checks: id, question and category are present; the language and type
    are known; an "answer" item says what the answer should contain.

    Example:
        >>> validate_item(GOLDEN[0])
        []
        >>> validate_item({"id": "x", "question": "", "lang": "de", "category": "c", "type": "answer"})
        ['missing question', "bad lang 'de'", 'answer without expected']
    """
    errs = []
    for k in ("id", "question", "category"):
        if not str(item.get(k, "")).strip():
            errs.append(f"missing {k}")
    if item.get("lang") not in LANGS:
        errs.append(f"bad lang {item.get('lang')!r}")
    if item.get("type") not in TYPES:
        errs.append(f"bad type {item.get('type')!r}")
    if item.get("type") == "answer" and not str(item.get("expected", "")).strip():
        errs.append("answer without expected")
    return errs


def norm_question(q):
    """A question reduced to lowercase words, to spot duplicates.

    `[^\\w\\s]|_` matches anything that is not a letter, digit or space
    (punctuation, including the Arabic ؟), which is replaced by a space;
    then runs of spaces collapse into one.

    Example:
        >>> norm_question("  Combien   de caution ?! ")
        'combien de caution'
        >>> norm_question("شنوة الضمان؟")
        'شنوة الضمان'
    """
    q = re.sub(r"[^\w\s]|_", " ", q.lower())
    return re.sub(r"\s+", " ", q).strip()


def dedupe(items):
    """Keep the first item of each normalized question, in order.

    Duplicates would count the same question twice and skew every score.

    Example:
        >>> qs = [{"id": "1", "question": "Prix ?"}, {"id": "2", "question": "prix"}, {"id": "3", "question": "Frais"}]
        >>> [i["id"] for i in dedupe(qs)]
        ['1', '3']
    """
    seen, out = set(), []
    for i in items:
        k = norm_question(i["question"])
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out


def coverage(items, key):
    """How many items per value of `key` (language, category, type), most common first.

    Example:
        >>> coverage(dedupe(GOLDEN), "lang")
        {'fr': 8, 'en': 7, 'derja': 5, 'arabizi': 1, 'ar': 1}
    """
    return dict(Counter(i[key] for i in items).most_common())


def split_dev_test(items, test_share=0.3, seed=0):
    """Split into **dev** (to look at and tune on) and **test** (kept for the final score).

    The split is **stratified**: each category is split separately, so the
    test part has a bit of every category instead of, by bad luck, none of
    "pets". A category with 2+ items always gives at least 1 to test. A
    fixed `seed` makes the split the same every run.

    If you tune on the test questions, the final score flatters you: that's
    why test stays closed until week 10.

    Example:
        >>> dev, test = split_dev_test(dedupe(GOLDEN))
        >>> len(dev), len(test)
        (15, 7)
        >>> sorted({i["category"] for i in test})
        ['deposit', 'documents', 'fees', 'out_of_scope', 'pets', 'rent', 'visits']
    """
    dev, test = [], []
    for cat in sorted({i["category"] for i in items}):
        group = [i for i in items if i["category"] == cat]
        random.Random(seed).shuffle(group)
        k = round(len(group) * test_share)
        if len(group) >= 2:
            k = max(1, k)
        test += group[:k]
        dev += group[k:]
    return dev, test


def gaps(items, min_per_category=3, min_langs=2, min_idk=2):
    """What the set as a whole is missing, in plain words (`[]` = fine).

    A category with fewer than 3 items gives a meaningless score for that
    category; one language only hides language problems; without "idk"
    items you never test that the assistant admits what it doesn't know.

    Example:
        >>> gaps(dedupe(GOLDEN))
        []
        >>> gaps([{"category": "pets", "lang": "fr", "type": "answer"}])
        ["category 'pets' has 1 item (< 3)", 'only 1 language', "only 0 'idk' items"]
    """
    out = []
    for cat, n in coverage(items, "category").items():
        if n < min_per_category:
            out.append(f"category '{cat}' has {n} item{'s' if n != 1 else ''} (< {min_per_category})")
    langs = len({i["lang"] for i in items})
    if langs < min_langs:
        out.append(f"only {langs} language{'s' if langs != 1 else ''}")
    idk = sum(i["type"] == "idk" for i in items)
    if idk < min_idk:
        out.append(f"only {idk} 'idk' items")
    return out


if __name__ == "__main__":
    import json
    bad = {i.get("id"): validate_item(i) for i in GOLDEN if validate_item(i)}
    print("invalid:", bad or "none")
    items = dedupe(GOLDEN)
    print(f"{len(GOLDEN)} items, {len(items)} after removing duplicates")
    print("langs:", coverage(items, "lang"))
    print("categories:", coverage(items, "category"))
    print("gaps:", gaps(items) or "none")
    dev, test = split_dev_test(items)
    for name, part in (("golden_dev.jsonl", dev), ("golden_test.jsonl", test)):
        with open(name, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(i, ensure_ascii=False) + "\n" for i in part)
    print(len(dev), "dev /", len(test), "test, saved. Don't look at test until week 10.")
