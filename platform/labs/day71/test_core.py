"""Tests for `core.py`, the ones your CI will run on every push (day 75).

Each test checks **one behavior** with a plain `assert`: if it's true, nothing happens; if
it's false, the test fails and says which behavior broke. pytest finds every function
whose name starts with `test_` and runs it.

A good suite is judged by the bugs it catches, not by how many lines it runs. Bench's
**Check** plants 8 bugs in `core.py` ("mutants"), one at a time; each must make at least
one test fail. The `__main__` demo below does the same with one planted bug.

Run it for real with `pip install pytest`, then `python -m pytest test_core.py -q`.
"""
from core import chunk_sentences, clean_citations, mask_phones, normalize_arabic, percentile


def test_alef_variants_become_plain_alef():
    """أسعار (with hamza) and اسعار must become the same word, or a search
    for one misses documents written with the other.

    Catches: alef variants no longer normalized.

    Example:
        >>> normalize_arabic("أسعار"), normalize_arabic("اسعار")
        ('اسعار', 'اسعار')
    """
    assert normalize_arabic("أسعار") == normalize_arabic("اسعار") == "اسعار"


def test_diacritics_and_tatweel_removed():
    """Vowel marks and the tatweel stretch must disappear.

    Catches: diacritics kept.

    Example:
        >>> normalize_arabic("مَدْرَسَة"), normalize_arabic("مـــدرسة")
        ('مدرسه', 'مدرسه')
    """
    assert normalize_arabic("مَدْرَسَة") == normalize_arabic("مـــدرسة") == "مدرسه"


def test_taa_marbuta_and_alef_maqsura():
    """ة -> ه and ى -> ي, checked in one real phrase.

    Catches: taa marbuta kept.

    Example:
        >>> normalize_arabic("مستشفى المدينة")
        'مستشفي المدينه'
    """
    assert normalize_arabic("مستشفى المدينة") == "مستشفي المدينه"


def test_chunks_respect_max_chars():
    """No chunk longer than the limit (the embedding model truncates the rest).

    Example:
        >>> [len(c) for c in chunk_sentences(["a" * 40, "b" * 40, "c" * 40, "d" * 40], max_chars=90, overlap=0)]
        [81, 81]
    """
    sents = ["a" * 40, "b" * 40, "c" * 40, "d" * 40]
    assert all(len(c) <= 90 for c in chunk_sentences(sents, max_chars=90, overlap=0))


def test_overlap_repeats_last_sentence():
    """With `overlap=1`, the second chunk starts with the last sentence of
    the first. The exact expected list leaves no room for a bug.

    Catches: overlap ignored.

    Example:
        >>> chunk_sentences(["one two.", "three four.", "five six."], max_chars=25, overlap=1)
        ['one two. three four.', 'three four. five six.']
    """
    chunks = chunk_sentences(["one two.", "three four.", "five six."], max_chars=25, overlap=1)
    assert chunks == ["one two. three four.", "three four. five six."]


def test_no_overlap_when_zero():
    """`overlap=0` must really mean no repeated sentence.

    Example:
        >>> chunk_sentences(["aaaa.", "bbbb.", "cccc."], max_chars=11, overlap=0)
        ['aaaa. bbbb.', 'cccc.']
    """
    assert chunk_sentences(["aaaa.", "bbbb.", "cccc."], max_chars=11, overlap=0) == ["aaaa. bbbb.", "cccc."]


def test_long_sentence_stays_whole():
    """A sentence longer than `max_chars` is kept whole, never cut.

    Catches: long sentences cut in pieces.

    Example:
        >>> "x" * 200 in chunk_sentences(["short.", "x" * 200, "end."], max_chars=50, overlap=0)
        True
    """
    long = "x" * 200
    assert long in chunk_sentences(["short.", long, "end."], max_chars=50, overlap=0)


def test_clean_citations_removes_out_of_range():
    """`[4]` with 3 sources and `[0]` are both removed, and both reported.

    Catches: `[0]` kept as a valid citation (an easy off-by-one: `k <= n` alone).

    Example:
        >>> clean_citations("A [1]. B [4]. C [0].", 3)
        ('A [1]. B . C .', [0, 4])
    """
    assert clean_citations("A [1]. B [4]. C [0].", 3) == ("A [1]. B . C .", [0, 4])


def test_clean_citations_keeps_valid():
    """The other side: valid markers stay untouched. Testing only removal
    would let a bug that removes everything pass.

    Example:
        >>> clean_citations("A [1][3].", 3)
        ('A [1][3].', [])
    """
    assert clean_citations("A [1][3].", 3) == ("A [1][3].", [])


def test_mask_phone_formats():
    """Both formats agents meet: international with spaces, and 8 digits.

    Example:
        >>> mask_phones("tel +216 98 123 456 ou 22333444")
        'tel [PHONE] ou [PHONE]'
    """
    assert mask_phones("tel +216 98 123 456 ou 22333444") == "tel [PHONE] ou [PHONE]"


def test_mask_phones_leaves_cin_and_long_numbers():
    """What must **not** be masked: a CIN (starts with 0) and a 9-digit
    reference. Masking them would destroy information the answer needs.

    Catches: a loose phone regex that masks CINs and pieces of long numbers.

    Example:
        >>> mask_phones("CIN 09876543, ref 981234567")
        'CIN 09876543, ref 981234567'
    """
    assert mask_phones("CIN 09876543, ref 981234567") == "CIN 09876543, ref 981234567"


def test_percentile_nearest_rank():
    """p95 of 1..20 is 19 by nearest rank (rank `ceil(0.95 x 20)` = 19).
    A version that rounds gets 20: an off-by-one that changes your latency report.

    Catches: rounding instead of nearest rank.

    Example:
        >>> percentile(list(range(1, 21)), 95), percentile([5, 1, 3], 50)
        (19, 3)
    """
    assert percentile(list(range(1, 21)), 95) == 19
    assert percentile([5, 1, 3], 50) == 3


def test_percentile_empty():
    """No data: `None`, not a crash (an evaluation with 0 runs happens).

    Example:
        >>> print(percentile([], 95))
        None
    """
    assert percentile([], 95) is None


def run_tests():
    """A tiny pytest: run every `test_` function of this file, return the
    names of the failing ones.

    `globals()` is the dict of everything defined in this module.

    Example:
        >>> run_tests()
        []
    """
    failed = []
    for name, t in list(globals().items()):
        if name.startswith("test_") and callable(t):
            try:
                t()
            except Exception:
                failed.append(name)
    return failed


if __name__ == "__main__":
    tests = [n for n in globals() if n.startswith("test_")]
    print(f"{len(tests)} tests on the real core.py, failing: {run_tests() or 'none'}")

    # Plant a bug, like Bench's Check does: a percentile that rounds instead of nearest rank.
    import math
    real = percentile
    percentile = lambda values, p: sorted(values)[min(len(values) - 1, round(p / 100 * len(values)))] if values else None
    print("with a planted percentile bug, failing:", run_tests())
    percentile = real

    # And one bug the suite would MISS if test_clean_citations_removes_out_of_range didn't include [0]:
    real = clean_citations
    clean_citations = lambda answer, n: real(answer.replace("[0]", "[1]"), n)   # silently keeps [0] as a citation
    print("with a planted citation bug, failing:", run_tests())
    clean_citations = real
