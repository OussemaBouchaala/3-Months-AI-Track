# Normalize Arabic text
**Topic:** many spellings, one form: diacritics, alef variants, taa marbuta, digits.

## Real example
A phone-contacts app matches names however people typed them. The same idea with Latin text: accents and case are "noise" for matching, so both sides get normalized the same way before comparing:

```python
import unicodedata

def norm(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")   # drop accent marks
    return " ".join(s.lower().split())

saved = ["Hélène  Ben Ali", "Raphaël Trabelsi"]
typed = "helene ben ali"
print([name for name in saved if norm(name) == norm(typed)])
```

Arabic diacritics are also "Mn" marks, which is why stripping them works the same way.

## Your mission
Write the normalizer you'll apply to both documents and questions.

## Steps
1. `strip_diacritics`: `DIACRITICS.sub("", ...)` and remove `TATWEEL`.
2. `normalize_alef` and `normalize_letters` (one `str.translate` or a few `replace`).
3. `arabic_digits_to_ascii` with `str.maketrans`.
4. `normalize_arabic`: chain them, then `" ".join(text.split())`.
5. **Run**: the first two samples must become identical.

## Done when
**Check** passes on vowelled, hamza, taa marbuta, tatweel and digit cases.
