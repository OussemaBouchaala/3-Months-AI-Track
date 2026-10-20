# Tests for core.py. Run them with:  python -m pytest test_core.py -q   (pip install pytest)
# Bench's Check goes further: it plants 6 bugs in core.py ("mutants") one at a time and checks that
# at least one of your tests fails for each. A test suite that passes on buggy code protects nothing.
from core import chunk_sentences, clean_citations, mask_phones, normalize_arabic, percentile


def test_alef_variants_become_plain_alef():
    assert normalize_arabic("أسعار") == normalize_arabic("اسعار") == "اسعار"


# TODO: at least 8 more tests. Ideas, one behavior per test:
#   normalize_arabic: diacritics removed; taa marbuta; tatweel
#   chunk_sentences: respects max_chars; overlap repeats the last sentence; a long sentence stays whole
#   clean_citations: out-of-range markers removed and reported, [0] included
#   mask_phones: +216 format; a CIN (starts with 0/1) and a 9-digit number are NOT masked
#   percentile: p95 of 1..20; empty list -> None
