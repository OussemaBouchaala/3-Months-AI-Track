# Keyword search that understands Arabic word shapes: "والمدرسة" (and the school) should match "مدرسة".
# A light stemmer strips common prefixes and suffixes. It's crude, fast, and usually a big win for BM25.
import json
import re
import sys

sys.path.append("../day37")
from arabic_norm import normalize_arabic   # yesterday's normalizer

# Longest first, so "وال" is tried before "و".
PREFIXES = ["وبال", "وال", "بال", "كال", "فال", "لل", "ال", "و", "ف", "ب", "ل", "ك"]
SUFFIXES = ["هما", "كما", "ات", "ون", "ين", "ان", "ها", "هم", "كم", "نا"]
MIN_STEM = 3


def light_stem(word):
    """Remove at most ONE prefix (the first in PREFIXES that the word starts with), then at most ONE suffix
    (first match in SUFFIXES), but only when what remains has at least MIN_STEM letters.
    Words that aren't Arabic (no letter in ء-ي) are returned unchanged."""
    # TODO
    ...


def tokenize_ar(text, stem=True):
    """normalize_arabic, lowercase, re.findall(r"\w+"), then light_stem each token if stem."""
    # TODO
    ...


def overlap(query, doc, stem=True):
    """Number of DISTINCT query tokens that also appear in the doc's tokens."""
    # TODO
    ...


if __name__ == "__main__":
    pairs = [("المدارس في صفاقس", "توجد مدرسة كبيرة بصفاقس"),
             ("الطلاب والمعلمون", "طالب ومعلم"),
             ("كتابهم", "الكتاب")]
    for q, d in pairs:
        print(q, "|", d, "| raw:", overlap(q, d, stem=False), "stemmed:", overlap(q, d), tokenize_ar(q), tokenize_ar(d))
