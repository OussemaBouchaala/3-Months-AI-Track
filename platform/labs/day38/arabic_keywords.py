"""Keyword search that understands Arabic word shapes.

In Arabic, little words stick to the front and back of a word: والمدرسة is و + ال + مدرسة
("and the school"), كتابهم is كتاب + هم ("their book"). A plain keyword search sees
والمدرسة and مدرسة as different words and misses the match.

A **light stemmer** cuts the most common prefixes and suffixes. It's crude (no grammar,
no dictionary) but fast, and usually a big win for BM25 on Arabic.

1. `light_stem`: cut at most one prefix and one suffix from a word.
2. `tokenize_ar`: normalize (day 37), split into words, stem each one.
3. `overlap`: how many query words a document shares, to see the effect.
"""
import re
import sys

sys.path.append("../day37")
try:
    from arabic_norm import normalize_arabic   # day 37's normalizer
except ImportError:                            # day 37 not opened yet: a minimal copy
    def normalize_arabic(text, taa_marbuta=True):
        text = re.sub("[ً-ْٰـ]", "", text)
        text = re.sub("[أإآٱ]", "ا", text).replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
        text = text.replace("ة", "ه") if taa_marbuta else text
        return " ".join(text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")).split())

# Longest first, so "وال" is tried before "و".
PREFIXES = ["وبال", "وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ل", "ك"]
SUFFIXES = ["هما", "كما", "ات", "ون", "ين", "ان", "ها", "هم", "كم", "نا"]
MIN_STEM = 3


def light_stem(word):
    """Cut at most ONE prefix, then at most ONE suffix, keeping at least 3 letters.

    - The lists are ordered **longest first**: for والمدرسه, "وال" must win
      over "و", or we'd keep "المدرسه".
    - `MIN_STEM = 3` protects short words: بيت ("house") starts with ب but is
      not ب + يت. Most Arabic roots have 3 letters, so a stem can't be shorter.
    - Words without Arabic letters (`[ء-ي]` is the Arabic letter range) are left alone.

    Example:
        >>> light_stem("والمدرسه"), light_stem("بالسياره"), light_stem("وكتابهم")
        ('مدرسه', 'سياره', 'كتاب')
        >>> light_stem("المعلمون"), light_stem("طالبات")
        ('معلم', 'طالب')
        >>> light_stem("بيت"), light_stem("sousse")
        ('بيت', 'sousse')
    """
    if not re.search("[ء-ي]", word):
        return word
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= MIN_STEM:
            word = word[len(p):]
            break
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= MIN_STEM:
            word = word[: -len(s)]
            break
    return word


def tokenize_ar(text, stem=True):
    """Text to search tokens: normalize, lowercase, split into words, stem.

    `re.findall(r"\\w+", ...)` keeps runs of letters and digits, so
    punctuation disappears. The same function must be used for documents
    **and** queries, or they won't match.

    Example:
        >>> tokenize_ar("والمدرسة الكبيرة في صفاقس")
        ['مدرسه', 'كبيره', 'في', 'صفاقس']
        >>> tokenize_ar("والمدرسة", stem=False)
        ['والمدرسه']
        >>> tokenize_ar("Sousse S+2")
        ['sousse', 's', '2']
    """
    toks = re.findall(r"\w+", normalize_arabic(text).lower())
    return [light_stem(t) for t in toks] if stem else toks


def overlap(query, doc, stem=True):
    """How many **distinct** query tokens also appear in the document.

    A tiny relevance score, just to compare with and without stemming.

    Example:
        >>> overlap("الطلاب والمعلمون", "طلاب ومعلم", stem=False)
        0
        >>> overlap("الطلاب والمعلمون", "طلاب ومعلم")
        2
    """
    return len(set(tokenize_ar(query, stem)) & set(tokenize_ar(doc, stem)))


if __name__ == "__main__":
    pairs = [("المدارس في صفاقس", "توجد مدرسة كبيرة بصفاقس"),
             ("الطلاب والمعلمون", "طالب ومعلم"),
             ("كتابهم", "الكتاب")]
    for q, d in pairs:
        print(f"{q} | {d}")
        print(f"   without stemming: {overlap(q, d, stem=False)} shared words {tokenize_ar(q, False)} {tokenize_ar(d, False)}")
        print(f"   with stemming:    {overlap(q, d)} shared words {tokenize_ar(q)} {tokenize_ar(d)}")
