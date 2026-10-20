# The core functions of the project, gathered in one module (in your repo: app/core.py).
# They come from Weeks 6-10. Today you don't change them: you write tests that would catch it if someone did.
import math
import re

DIACRITICS = re.compile("[ً-ْٰ]")
PHONE = re.compile(r"(?<!\d)(?:(?:\+|00)216[ .]?)?[2-9]\d(?:[ .]?\d{3}){2}(?!\d)")


def normalize_arabic(text):
    """Remove diacritics and tatweel; أ إ آ -> ا; ة -> ه; ى -> ي."""
    text = DIACRITICS.sub("", text).replace("ـ", "")
    text = re.sub("[أإآ]", "ا", text)
    return text.replace("ة", "ه").replace("ى", "ي")


def chunk_sentences(sentences, max_chars=500, overlap=1):
    """Pack sentences into chunks of at most max_chars (a longer sentence stays alone);
    each new chunk starts with the last `overlap` sentences of the previous one."""
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
    """Remove [k] markers outside 1..n_sources. Return (text, sorted removed k's)."""
    removed = sorted({int(k) for k in re.findall(r"\[(\d+)\]", answer) if not 1 <= int(k) <= n_sources})
    text = re.sub(r"\[(\d+)\]", lambda m: m.group() if 1 <= int(m.group(1)) <= n_sources else "", answer)
    return text, removed


def mask_phones(text):
    """Replace Tunisian phone numbers with [PHONE]."""
    return PHONE.sub("[PHONE]", text)


def percentile(values, p):
    """Nearest-rank percentile; None for an empty list."""
    if not values:
        return None
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1]
