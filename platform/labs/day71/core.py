"""The core functions of the project, gathered in one module (in your repo: `app/core.py`).

They come from Weeks 6-10. Today nothing here changes: `test_core.py` writes the tests
that would catch it if someone broke one of them.

1. `normalize_arabic` (day 37): the same word, however it was typed.
2. `chunk_sentences` (day 40): sentences packed into chunks, with overlap.
3. `clean_citations` (day 54): drop markers that point at no source.
4. `mask_phones` (day 45): Tunisian phone numbers out of the text.
5. `percentile` (day 46): p95 latency by nearest rank.
"""
import math
import re

# Arabic diacritics (tanwin, short vowels, shadda, sukun) and the dagger alef.
DIACRITICS = re.compile("[ً-ْٰ]")
PHONE = re.compile(r"(?<!\d)(?:(?:\+|00)216[ .]?)?[2-9]\d(?:[ .]?\d{3}){2}(?!\d)")


def normalize_arabic(text):
    """Make Arabic spellings of the same word identical, so search matches them.

    - Remove diacritics (the short-vowel marks, `DIACRITICS`) and tatweel
      `ـ` (the stretching line in مـــدرسة).
    - Alef with hamza or madda `أ إ آ` -> plain `ا`.
    - `ة` -> `ه` and `ى` -> `ي`: people type them both ways.

    Example:
        >>> normalize_arabic("أسعار"), normalize_arabic("مَدْرَسَة"), normalize_arabic("مستشفى المدينة")
        ('اسعار', 'مدرسه', 'مستشفي المدينه')
    """
    text = DIACRITICS.sub("", text).replace("ـ", "")
    text = re.sub("[أإآ]", "ا", text)
    return text.replace("ة", "ه").replace("ى", "ي")


def chunk_sentences(sentences, max_chars=500, overlap=1):
    """Pack sentences into chunks of at most `max_chars`.

    - Add sentences to the current chunk until the next one would make it too long.
    - The new chunk starts with the last `overlap` sentences of the previous
      one, so a fact split across two sentences is still found together.
    - A sentence longer than `max_chars` stays whole, alone in its chunk:
      cutting it would cut a clause in half.

    Example:
        >>> chunk_sentences(["one two.", "three four.", "five six."], max_chars=25, overlap=1)
        ['one two. three four.', 'three four. five six.']
        >>> chunk_sentences(["short.", "x" * 60, "end."], max_chars=50, overlap=0)
        ['short.', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'end.']
    """
    chunks, current = [], []
    for s in sentences:
        if current and len(" ".join(current + [s])) > max_chars:
            chunks.append(" ".join(current))
            current = current[-overlap:] if overlap else []
            if current and len(" ".join(current + [s])) > max_chars:
                current = []
        current.append(s)
    if current:
        chunks.append(" ".join(current))
    return chunks


def clean_citations(answer, n_sources):
    """Remove citation markers `[k]` with `k` outside `1..n_sources`.

    Returns `(text, removed numbers)`. `[0]` is invalid too: sources are
    numbered from 1.

    Example:
        >>> clean_citations("A [1]. B [4]. C [0].", 3)
        ('A [1]. B . C .', [0, 4])
    """
    removed = sorted({int(k) for k in re.findall(r"\[(\d+)\]", answer) if not 1 <= int(k) <= n_sources})
    text = re.sub(r"\[(\d+)\]", lambda m: m.group() if 1 <= int(m.group(1)) <= n_sources else "", answer)
    return text, removed


def mask_phones(text):
    """Replace Tunisian phone numbers with `[PHONE]`.

    `PHONE` accepts `+216` / `00216`, then 8 digits starting with 2-9, with
    optional spaces or dots. `(?<!\\d)` and `(?!\\d)` refuse a match inside
    a longer number, and a CIN starts with 0 or 1, so neither is masked.

    Example:
        >>> mask_phones("tel +216 98 123 456 ou 22333444")
        'tel [PHONE] ou [PHONE]'
        >>> mask_phones("CIN 09876543, ref 981234567")
        'CIN 09876543, ref 981234567'
    """
    return PHONE.sub("[PHONE]", text)


def percentile(values, p):
    """The nearest-rank percentile: sort, take the value at rank `ceil(p/100 x n)`.

    Example:
        >>> percentile(list(range(1, 21)), 95), percentile([5, 1, 3], 50), percentile([], 95)
        (19, 3, None)
    """
    if not values:
        return None
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1]


if __name__ == "__main__":
    print(normalize_arabic("أَسْعَار الكِرَاء في المدينة"))
    print(chunk_sentences(["Le loyer est de 900 TND.", "La caution est de deux mois.", "Les animaux sont acceptés."], max_chars=60))
    print(clean_citations("Deux mois [1][5].", 2))
    print(mask_phones("Rappelez Amel au +216 98 123 456, CIN 09876543."))
    print(percentile([1.2, 0.8, 4.5, 2.0, 9.7, 1.1], 95))
