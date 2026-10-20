# Arabic keyword search
**Topic:** Arabic glues "and", "the", "with", "their" onto words; strip them so keywords can match.

## Real example
An English search engine does the same with plurals and "-ing" (a toy stemmer, rules longest-first, and never cut a word too short):

```python
SUFFIXES = ["ings", "ing", "es", "s"]

def stem(w, min_len=3):
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= min_len:
            return w[: -len(s)]
    return w

for w in ["bookings", "booking", "books", "bus", "is"]:
    print(w, "->", stem(w))
```

"bus" stays "bus" thanks to the minimum length. Arabic needs prefixes too: و (and), ال (the), ب (with), ل (for).

## Your mission
A light stemmer + tokenizer, and proof it increases keyword overlap.

## Steps
1. `light_stem`: one prefix, then one suffix, each only if ≥ `MIN_STEM` letters remain; skip non-Arabic words.
2. `tokenize_ar`: normalize (day37), lowercase, `\w+`, stem.
3. `overlap`: size of the set intersection.
4. **Run**: the stemmed overlap should beat the raw one on all three pairs. Then plug `tokenize_ar` into your Week 3 BM25 (`hybrid.py`) for Arabic.

## Done when
**Check** passes, and you've noted recall@5 of BM25 on ARCD with and without stemming (Saturday measures it properly).
