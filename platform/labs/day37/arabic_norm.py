# Arabic normalization: make the same word look the same, however it was typed.
# أحمد / احمد / إحمد, مدرسة / مدرسه, مُدَرِّس / مدرس, and ٢٠٢٦ / 2026 should all match.
import re

DIACRITICS = re.compile("[ً-ْٰ]")   # tanween, fatha, damma, kasra, shadda, sukun, dagger alef
TATWEEL = "ـ"                                    # ـ  the stretching character: مـــدرســة


def strip_diacritics(text):
    """Remove the short-vowel marks (DIACRITICS) and the tatweel."""
    # TODO
    ...


def normalize_alef(text):
    """أ إ آ ٱ  ->  ا"""
    # TODO: re.sub("[أإآٱ]", "ا", text)
    ...


def normalize_letters(text, taa_marbuta=True):
    """ى -> ي (alef maqsura), ؤ -> و, ئ -> ي, and if taa_marbuta: ة -> ه."""
    # TODO
    ...


def arabic_digits_to_ascii(text):
    """٠١٢٣٤٥٦٧٨٩ (Arabic-Indic) and ۰۱۲۳۴۵۶۷۸۹ (Persian) -> 0123456789. Hint: str.maketrans."""
    # TODO
    ...


def normalize_arabic(text, taa_marbuta=True):
    """All of the above, in this order: diacritics, alef, letters, digits. Then collapse runs of whitespace
    into one space and strip. Latin text passes through unchanged (lowercasing is not done here)."""
    # TODO
    ...


if __name__ == "__main__":
    samples = ["أَحْمَدُ ذهب إلى المدرسة", "احمد ذهب الى المدرسه", "مـــدرســة الإمام", "سنة ٢٠٢٦، مستشفى", "Appartement S+2 à Sousse"]
    for s in samples:
        print(f"{s!r:<34} -> {normalize_arabic(s)!r}")
    print("same after normalization:", normalize_arabic(samples[0]) == normalize_arabic(samples[1]))
