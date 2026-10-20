# Day 18 checked that citation numbers exist. A client-facing answer needs more: every sentence cited,
# markers in one format, and a cheap check that the cited chunk actually says what the sentence claims.
import re

IDK = "I don't know based on the documents."
SENT = re.compile(r"(?<=[.!?؟])\s+")


def normalize_markers(answer):
    """Rewrite "[1, 2]", "[1,2]" and "[1] [2]" as "[1][2]"."""
    # TODO
    ...


def clean_citations(answer, n_sources):
    """normalize_markers, then remove markers [k] with k outside 1..n_sources. Return (text, sorted removed k's)."""
    # TODO
    ...


def sentence_citations(answer):
    """[(sentence without its markers, [cited numbers in order, no duplicates]), ...] splitting on SENT.
    A marker right after the final period ("... TND. [2]") belongs to that sentence."""
    # TODO
    ...


def citation_coverage(answer):
    """Share of sentences with at least one citation. The IDK answer counts as fully covered (1.0)."""
    # TODO
    ...


def _words(text):
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) >= 4 or w.isdigit()}


def unsupported_claims(answer, chunks, min_overlap=0.5):
    """chunks: the numbered sources (chunks[0] is [1]). A cited sentence is supported when, for at least one
    cited chunk, the share of the sentence's words (\\w+, lowercased, length >= 4 or all digits) found in that
    chunk's text is >= min_overlap. Return the cited sentences that are NOT supported."""
    # TODO
    ...


def render_sources(answer, chunks):
    """One line per cited source, in citation order: "[2] Bail type > Article 4 (bail7)".
    Use title and section (" > section" only when there is one) and doc_id."""
    # TODO
    ...


if __name__ == "__main__":
    chunks = [{"title": "Règlement", "section": "Caution", "doc_id": "reglement", "text": "Le locataire paie une caution de deux mois de loyer."},
              {"title": "Règlement", "section": "Animaux", "doc_id": "reglement", "text": "Avec un animal, la caution augmente d'un demi-mois."}]
    raw = "La caution est de deux mois de loyer [1, 3]. Avec un chat, elle augmente d'un demi-mois [2]. Le chat doit être vacciné [2]."
    text, removed = clean_citations(raw, len(chunks))
    print(text, "| removed:", removed)
    print("coverage:", citation_coverage(text))
    print("unsupported:", unsupported_claims(text, chunks))
    print(render_sources(text, chunks))
