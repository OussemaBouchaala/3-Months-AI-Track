"""Mixed Tunisian text: detect what you're looking at before you process it.

Tunisian listings and messages mix scripts and languages in one sentence:

- `Appartement S+2 للبيع في Sahloul, prix 250 mille` (French + Arabic)
- `3andi chi9a fi Sousse, 9adech el kra?` (**Arabizi**: Arabic written with Latin letters,
  where digits stand for Arabic sounds: 3 = ع, 7 = ح, 9 = ق)

Before you normalize, tokenize or choose a prompt language, you need to know which is which.

1. `script_of`: the script of one word (Arabic, Latin, digits).
2. `script_ratio`: the share of each script in a text.
3. `is_arabizi`: is this Latin word really Arabic in disguise?
4. `detect_lang`: Arabic, French or English for a whole text.
5. `split_runs`: cut a mixed text into same-script pieces.
"""
import re
from collections import Counter
from itertools import groupby

FR_WORDS = {"le", "la", "les", "de", "des", "du", "et", "à", "pour", "avec", "est", "une", "un", "prix", "vendre", "louer", "chambre"}
EN_WORDS = {"the", "and", "for", "with", "is", "a", "an", "of", "to", "price", "sale", "rent", "room", "flat", "apartment"}
# Arabizi: digits used as Arabic letters, Tunisian usage
ARABIZI = {"2": "ء", "3": "ع", "5": "خ", "7": "ح", "9": "ق"}


def script_of(token):
    """The script of one word: "arabic", "digit", "latin" or "other".

    The checks go in order: any Arabic letter (`[ء-ي]`) makes it Arabic;
    only digits makes it a number; any other letter (`isalpha`, which also
    accepts é, à) makes it Latin.

    Example:
        >>> [script_of(t) for t in ["سوسة", "Sahloul", "2026", "é", "_"]]
        ['arabic', 'latin', 'digit', 'latin', 'other']
    """
    if re.search("[ء-ي]", token):
        return "arabic"
    if token.isdigit():
        return "digit"
    if any(c.isalpha() for c in token):
        return "latin"
    return "other"


def script_ratio(text):
    """The share of words in each script.

    `re.findall(r"\\w+", text)` lists the words; `Counter` counts their
    scripts; dividing by the number of words gives shares that add up to 1.

    Example:
        >>> script_ratio("شقة للبيع Sahloul 250")
        {'arabic': 0.5, 'latin': 0.25, 'digit': 0.25}
    """
    toks = re.findall(r"\w+", text)
    c = Counter(script_of(t) for t in toks)
    return {k: v / len(toks) for k, v in c.items()}


def is_arabizi(token):
    """True for a Latin word that uses a digit as an Arabic letter (2, 3, 5, 7 or 9).

    It needs **both** a letter and one of those digits: `3andi` (عندي) and
    `chi9a` (شقة) are Arabizi, but `2026` (no letter) and `sousse` (no
    digit) are not.

    Example:
        >>> [is_arabizi(t) for t in ["3andi", "chi9a", "7ata", "2026", "sousse"]]
        [True, True, True, False, False]
    """
    return any(c.isalpha() for c in token) and any(d in token for d in ARABIZI) and not re.search("[ء-ي]", token)


def detect_lang(text):
    """The language of a whole text: "ar", "fr" or "en".

    - **Arabic** if at least half the words are Arabic script or Arabizi.
      Also if there are 2+ Arabizi words and they outnumber the French and
      English hits, because Arabizi sentences contain plain words like
      "fi" or "el" that look Latin.
    - Otherwise count common French and English words: more English means
      "en". A tie goes to "fr", since most Tunisian listings in Latin script
      are French.

    Example:
        >>> detect_lang("شقة للكراء قرب البحر"), detect_lang("3andi chi9a fi Sousse 9adech el kra")
        ('ar', 'ar')
        >>> detect_lang("Appartement à louer avec 2 chambres"), detect_lang("Flat for rent near the beach")
        ('fr', 'en')
    """
    toks = re.findall(r"\w+", text)
    low = [t.lower() for t in toks]
    fr, en = sum(t in FR_WORDS for t in low), sum(t in EN_WORDS for t in low)
    arabizi = sum(is_arabizi(t) for t in toks)
    if sum(script_of(t) == "arabic" or is_arabizi(t) for t in toks) >= len(toks) / 2 or (arabizi >= 2 and arabizi > fr + en):
        return "ar"
    return "en" if en > fr else "fr"


def split_runs(text):
    """Cut a mixed text into pieces of the same script, skipping numbers and symbols.

    `itertools.groupby` groups **consecutive** items with the same key, here
    the script. Each group is joined back into one string.

    Example:
        >>> split_runs("شقة للبيع Appartement S+2 في سوسة")
        [('arabic', 'شقة للبيع'), ('latin', 'Appartement S'), ('arabic', 'في سوسة')]
    """
    toks = [(script_of(t), t) for t in re.findall(r"\w+", text)]
    toks = [p for p in toks if p[0] in ("arabic", "latin")]
    return [(s, " ".join(t for _, t in grp)) for s, grp in groupby(toks, key=lambda p: p[0])]


if __name__ == "__main__":
    for t in ["Appartement S+2 للبيع في Sahloul, prix 250 mille",
              "3andi chi9a fi Sousse, 9adech el kra?",
              "Flat for rent near the beach, 3 rooms",
              "شقة للكراء قرب البحر"]:
        print(t)
        ratio = {k: round(v, 2) for k, v in script_ratio(t).items()}
        print(f"   language: {detect_lang(t)}   scripts: {ratio}")
        print(f"   pieces:   {split_runs(t)}")
