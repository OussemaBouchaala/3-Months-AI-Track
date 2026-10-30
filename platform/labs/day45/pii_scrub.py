"""Mask personal data (PII) before real client documents touch any API or log.

Names, phone numbers, emails, ID cards and bank accounts must not leave the client's
machine. Each one is replaced by a placeholder like `[PHONE_1]`. The **same value always
gets the same placeholder**, so the text still makes sense ("[PHONE_1] called twice"),
and the mapping lets you put the real values back afterwards.

1. The patterns: `EMAIL`, `RIB` (bank account), `PHONE`, `CIN` (national ID), Tunisian formats.
2. `find_pii`: every match, without overlaps.
3. `scrub`: replace matches with numbered placeholders.
4. `scrub_names`: the same for known names.
5. `restore`: put the original values back.
"""
import re

EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
RIB = r"(?<!\d)\d{2}(?:\s?\d){18}(?!\d)"          # Tunisian RIB: 20 digits, sometimes in groups
PHONE = r"(?<!\d)(?:(?:\+|00)216[ .]?)?[2-9]\d(?:[ .]?\d{3}){2}(?!\d)"
CIN = r"(?<!\d)[01]\d{7}(?!\d)"

# Order matters: a RIB contains 8-digit runs, so it must be found before phones and CINs.
PATTERNS = [("RIB", RIB), ("EMAIL", EMAIL), ("PHONE", PHONE), ("CIN", CIN)]


def find_pii(text):
    """Every piece of personal data as `(kind, start, end, value)`, sorted by position.

    The patterns:

    - **PHONE**: optional `+216` or `00216`, then 8 digits starting with 2-9,
      grouped `2 + 3 + 3` with optional spaces or dots.
    - **CIN**: exactly 8 digits starting with 0 or 1.
    - `(?<!\\d)` and `(?!\\d)` mean "no digit just before / after", so a
      number inside a longer number is not matched.

    Patterns run in `PATTERNS` order and a match that **overlaps** an earlier
    one is skipped, so the 8 digits inside a RIB aren't also reported as a phone.

    Example:
        >>> for kind, start, end, value in find_pii("RIB 08006000123456789012, tel +216 98 123 456, CIN 01234567"):
        ...     print(kind, value)
        RIB 08006000123456789012
        PHONE +216 98 123 456
        CIN 01234567
    """
    found = []
    for kind, pat in PATTERNS:
        if not pat:
            continue
        for m in re.finditer(pat, text):
            if all(m.end() <= s or m.start() >= e for _, s, e, _ in found):
                found.append((kind, m.start(), m.end(), m.group()))
    return sorted(found, key=lambda t: t[1])


def _replace(text, spans, mapping):
    """Swap each span for its placeholder; shared by `scrub` and `scrub_names`.

    `reverse` maps a value to its placeholder so a repeated value reuses it.
    A new value of a kind gets the next number for that kind. The text is
    rebuilt from the pieces between spans, left to right.

    Example:
        >>> _replace("call 98123456 or 98123456", [("PHONE", 5, 13, "98123456"), ("PHONE", 17, 25, "98123456")], None)
        ('call [PHONE_1] or [PHONE_1]', {'[PHONE_1]': '98123456'})
    """
    mapping = {} if mapping is None else mapping
    reverse = {v: k for k, v in mapping.items()}
    out, pos = [], 0
    for kind, s, e, value in spans:
        if value not in reverse:
            n = sum(1 for k in mapping if k.startswith(f"[{kind}_")) + 1
            reverse[value] = f"[{kind}_{n}]"
            mapping[reverse[value]] = value
        out += [text[pos:s], reverse[value]]
        pos = e
    out.append(text[pos:])
    return "".join(out), mapping


def scrub(text, mapping=None):
    """Mask all personal data in `text`. Returns `(masked_text, mapping)`.

    Pass the mapping from a previous document to keep the numbering across
    documents: the same phone stays `[PHONE_1]` everywhere.

    Example:
        >>> masked, m = scrub("a 98123456")
        >>> masked
        'a [PHONE_1]'
        >>> scrub("b 22333444 and 98123456", m)
        ('b [PHONE_2] and [PHONE_1]', {'[PHONE_1]': '98123456', '[PHONE_2]': '22333444'})
    """
    return _replace(text, find_pii(text), mapping)


def scrub_names(text, names, mapping=None):
    """Mask known names (whole words, any case) as `[NAME_n]`.

    Names can't be found with a pattern, so you pass the list (from your
    client file). `\\b` (word boundary) stops "Salma" from matching inside
    "Salmane"; `re.escape` protects names with special characters.

    Example:
        >>> scrub_names("salma said Salma; Salmane no", ["Salma"])[0]
        '[NAME_1] said [NAME_2]; Salmane no'
    """
    spans = []
    for name in names:
        for m in re.finditer(r"\b" + re.escape(name) + r"\b", text, re.I):
            if all(m.end() <= s or m.start() >= e for _, s, e, _ in spans):
                spans.append(("NAME", m.start(), m.end(), m.group()))
    return _replace(text, sorted(spans, key=lambda t: t[1]), mapping)


def restore(text, mapping):
    """Put the original values back, for the answer you show the client.

    Never send restored text to an outside API: restore only at the very end,
    on your own machine.

    Example:
        >>> restore("Call [PHONE_1] now", {"[PHONE_1]": "98123456"})
        'Call 98123456 now'
    """
    for ph, value in mapping.items():
        text = text.replace(ph, value)
    return text


if __name__ == "__main__":
    msg = ("Bonjour, c'est Salma Ben Ali, CIN 09876543. Rappelez-moi au +216 98 123 456 ou "
           "salma.benali@gmail.com. RIB 08 006 0001234567890 12")
    masked, m = scrub(msg)
    masked, m = scrub_names(masked, ["Salma Ben Ali"], m)
    print("what the API sees:", masked)
    print("mapping (stays local):", m)
    print("restored == original:", restore(masked, m) == msg)
