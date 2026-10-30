"""Arabic normalization: make the same word look the same, however it was typed.

People write the same Arabic word in many ways: أحمد / احمد / إحمد, مدرسة / مدرسه,
with or without short vowels (مُدَرِّس / مدرس), with Arabic or Western digits (٢٠٢٦ / 2026).
To a computer these are all **different strings**, so a search for one misses the others.
Normalization maps them all to one form, before indexing **and** before searching.

1. `strip_diacritics`: remove short-vowel marks and the stretching character.
2. `normalize_alef`: all forms of alef become plain ا.
3. `normalize_letters`: ى → ي, ؤ → و, ئ → ي, and (optionally) ة → ه.
4. `arabic_digits_to_ascii`: ٠-٩ and ۰-۹ become 0-9.
5. `normalize_arabic`: all of the above, plus clean whitespace.
"""
import re

DIACRITICS = re.compile("[ً-ْٰ]")   # tanween, fatha, damma, kasra, shadda, sukun, dagger alef
TATWEEL = "ـ"                                  # ـ  the stretching character: مـــدرســة


def strip_diacritics(text):
    """Remove the short-vowel marks (harakat, shadda, sukun) and the tatweel.

    Most Arabic text online is written without vowel marks, so they only get
    in the way of matching. `DIACRITICS` is a regex **character range**
    covering all of them, from U+064B to U+0652, plus U+0670.
    The tatweel `ـ` only stretches a word visually: مـــدرســة is مدرسة.

    Example:
        >>> strip_diacritics("مُدَرِّسٌ")
        'مدرس'
        >>> strip_diacritics("مـــدرســة")
        'مدرسة'
    """
    return DIACRITICS.sub("", text).replace(TATWEEL, "")


def normalize_alef(text):
    """Turn every alef with a hamza or madda (أ إ آ ٱ) into a plain ا.

    People often skip the hamza when typing, so أحمد and احمد must match.

    Example:
        >>> normalize_alef("أحمد إبراهيم آمنة")
        'احمد ابراهيم امنة'
    """
    return re.sub("[أإآٱ]", "ا", text)


def normalize_letters(text, taa_marbuta=True):
    """Unify letters that are often swapped when typing.

    - ى (alef maqsura) → ي: مستشفى / مستشفي.
    - ؤ → و and ئ → ي: the hamza seat is often dropped.
    - ة (taa marbuta) → ه, because many people type مدرسه for مدرسة. It's
      optional (`taa_marbuta=False`) since it also merges a few real words.

    Example:
        >>> normalize_letters("مستشفى مؤسسة رئيس")
        'مستشفي موسسه رييس'
        >>> normalize_letters("مدرسة", taa_marbuta=False)
        'مدرسة'
    """
    text = text.replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    return text.replace("ة", "ه") if taa_marbuta else text


def arabic_digits_to_ascii(text):
    """Turn Arabic-Indic (٠-٩) and Persian (۰-۹) digits into 0-9.

    `str.maketrans(from, to)` builds a character-for-character table, and
    `translate` applies it in one pass, faster than ten `replace` calls.

    Example:
        >>> arabic_digits_to_ascii("سنة ٢٠٢٦ و ۱۲")
        'سنة 2026 و 12'
    """
    return text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))


def normalize_arabic(text, taa_marbuta=True):
    """All the steps above, in order, then clean the whitespace.

    `" ".join(text.split())` turns any run of spaces, tabs and newlines into a
    single space and trims both ends. Latin text passes through unchanged
    (lowercasing is done later, by the tokenizer).

    Example:
        >>> normalize_arabic("أَحْمَدُ ذهب إلى المدرسة") == normalize_arabic("احمد ذهب الى المدرسه")
        True
        >>> normalize_arabic("  سنة   ٢٠٢٦ ")
        'سنه 2026'
        >>> normalize_arabic("Appartement S+2 à Sousse")
        'Appartement S+2 à Sousse'
    """
    text = arabic_digits_to_ascii(normalize_letters(normalize_alef(strip_diacritics(text)), taa_marbuta))
    return " ".join(text.split())


if __name__ == "__main__":
    samples = ["أَحْمَدُ ذهب إلى المدرسة", "احمد ذهب الى المدرسه", "مـــدرســة الإمام", "سنة ٢٠٢٦، مستشفى", "Appartement S+2 à Sousse"]
    for s in samples:
        print(f"{s!r:<34} -> {normalize_arabic(s)!r}")
    print("same after normalization:", normalize_arabic(samples[0]) == normalize_arabic(samples[1]))
