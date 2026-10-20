# Before real client documents touch any API or log: mask personal data (PII).
# Same value -> same placeholder, so the text still makes sense ("[PHONE_1] called twice").
import re

EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
RIB = r"(?<!\d)\d{2}(?:\s?\d){18}(?!\d)"          # Tunisian RIB: 20 digits, sometimes in groups
PHONE = r""   # TODO: 8 digits starting with 2-9, optional +216 / 00216 prefix, optional spaces or dots:
              # "+216 98 123 456", "98123456", "00216 71.234.567". Not inside a longer number.
CIN = r""     # TODO: national ID: exactly 8 digits starting with 0 or 1, not inside a longer number.

# Order matters: a RIB contains 8-digit runs, so it must be found before phones and CINs.
PATTERNS = [("RIB", RIB), ("EMAIL", EMAIL), ("PHONE", PHONE), ("CIN", CIN)]


def find_pii(text):
    """[(kind, start, end, value), ...] sorted by start. Go through PATTERNS in order; skip a match
    that overlaps one already found. Skip patterns that are empty strings."""
    # TODO
    ...


def scrub(text, mapping=None):
    """Replace each PII value with [KIND_n], numbered per kind in order of first appearance.
    The same value always gets the same placeholder. mapping: {placeholder: original}, reused and
    extended across calls (so a second document keeps the numbering). Return (masked_text, mapping)."""
    # TODO
    ...


def scrub_names(text, names, mapping=None):
    """Mask known names (whole words, case-insensitive) as [NAME_n], same rules as scrub."""
    # TODO
    ...


def restore(text, mapping):
    """Put the original values back (for showing the answer to the agent, never to the API)."""
    # TODO
    ...


if __name__ == "__main__":
    msg = "Bonjour, c'est Salma Ben Ali, CIN 09876543. Rappelez-moi au +216 98 123 456 ou salma.benali@gmail.com. RIB 08 006 0001234567890 12"
    masked, m = scrub(msg)
    masked, m = scrub_names(masked, ["Salma Ben Ali"], m)
    print(masked)
    print(m)
    print(restore(masked, m) == msg)
