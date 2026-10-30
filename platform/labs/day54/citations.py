"""Day 18 checked that citation numbers exist. A client-facing answer needs more.

Every sentence should be cited, markers should have one format, and a cheap check
should catch a sentence whose cited chunk doesn't actually say what it claims.

1. `normalize_markers`: "[1, 2]" and "[1] [2]" become "[1][2]".
2. `clean_citations`: drop markers pointing at sources that don't exist.
3. `sentence_citations`: which sentence cites what.
4. `citation_coverage`: the share of sentences that cite something.
5. `unsupported_claims`: cited sentences their source doesn't back up.
6. `render_sources`: the "Sources" list under the answer.
"""
import re

IDK = "I don't know based on the documents."
SENT = re.compile(r"(?<=[.!?؟])\s+")      # split after . ! ? or the Arabic ؟, on the spaces that follow


def normalize_markers(answer):
    """Rewrite every citation style the model invents as `[1][2]`.

    1. `[1, 2]` / `[1,2]`: the regex finds a list of numbers inside one pair
       of brackets, and the lambda rebuilds it as one bracket per number.
    2. `[1] [2]`: remove spaces between `]` and a following `[digits]`.
       The lookahead `(?=\\d+\\])` checks it's really a marker.

    Example:
        >>> normalize_markers("a [1, 2]. b [3,4]. c [5] [6].")
        'a [1][2]. b [3][4]. c [5][6].'
    """
    answer = re.sub(r"\[(\d+(?:\s*,\s*\d+)+)\]", lambda m: "".join(f"[{n.strip()}]" for n in m.group(1).split(",")), answer)
    return re.sub(r"\](\s+)\[(?=\d+\])", "][", answer)


def clean_citations(answer, n_sources):
    """Normalize, then remove markers `[k]` with `k` outside `1..n_sources`.

    A model sometimes cites `[4]` when it got 3 sources, or `[0]`. Showing
    a link to nothing destroys trust. Returns `(text, removed numbers)`, so
    you can log how often it happens.

    Example:
        >>> clean_citations("Deux mois [1, 4]. Oui [0][2].", 3)
        ('Deux mois [1]. Oui [2].', [0, 4])
    """
    text = normalize_markers(answer)
    removed = sorted({int(k) for k in re.findall(r"\[(\d+)\]", text) if not 1 <= int(k) <= n_sources})
    text = re.sub(r"\[(\d+)\]", lambda m: m.group() if 1 <= int(m.group(1)) <= n_sources else "", text)
    return text, removed


def sentence_citations(answer):
    """`[(sentence without markers, [cited numbers]), ...]`.

    Split on `SENT`, collect each sentence's numbers (in order, without
    duplicates: `dict.fromkeys` keeps the first of each), and remove the
    markers from the text.

    A marker after the final period ("... TND. [2]") is split off as an
    empty "sentence"; it is merged back into the sentence before it.

    Example:
        >>> sentence_citations("Deux mois [1]. Avec un chat [2][1] un demi-mois. Merci!")
        [('Deux mois.', [1]), ('Avec un chat un demi-mois.', [2, 1]), ('Merci!', [])]
        >>> sentence_citations("Le loyer est 900 TND. [2]")
        [('Le loyer est 900 TND.', [2])]
    """
    out = []
    for s in SENT.split(normalize_markers(answer).strip()):
        if not s:
            continue
        nums = list(dict.fromkeys(int(k) for k in re.findall(r"\[(\d+)\]", s)))
        out.append((re.sub(r"\s*\[\d+\]", "", s).strip(), nums))
    if len(out) > 1 and not out[-1][0] and out[-1][1]:            # "... TND. [2]" split off on its own
        last = out.pop()
        out[-1] = (out[-1][0], list(dict.fromkeys(out[-1][1] + last[1])))
    return out


def citation_coverage(answer):
    """The share of sentences with at least one citation.

    The "I don't know" answer has nothing to cite, so it counts as fully
    covered (1.0). Track this number in your evals: it should stay near 1.

    Example:
        >>> citation_coverage("A [1]. B. C [2]. D.")
        0.5
        >>> citation_coverage(IDK)
        1.0
    """
    if IDK in answer:
        return 1.0
    sc = sentence_citations(answer)
    return sum(1 for _, nums in sc if nums) / len(sc) if sc else 0.0


def _words(text):
    """The meaningful words of a text: lowercased, 4+ letters, or numbers.

    Short words ("la", "de", "est") appear everywhere and prove nothing;
    numbers ("900", "2") are exactly what must match.

    Example:
        >>> sorted(_words("La caution est de 2 mois."))
        ['2', 'caution', 'mois']
    """
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) >= 4 or w.isdigit()}


def unsupported_claims(answer, chunks, min_overlap=0.5):
    """Cited sentences that none of their sources seem to support.

    For each cited sentence: the share of its words found in a cited
    chunk. If at least one cited chunk reaches `min_overlap`, it passes.
    `chunks[0]` is source `[1]`.

    It's a cheap word-overlap test, not proof, but it catches the classic
    failure: a fact the model added from its own memory with a citation
    stuck on it.

    Example:
        >>> chunks = [{"text": "Le locataire paie une caution de deux mois de loyer."},
        ...           {"text": "Avec un animal, la caution augmente d'un demi-mois."}]
        >>> unsupported_claims("La caution est de deux mois de loyer [1]. Le chat doit être vacciné [2].", chunks)
        ['Le chat doit être vacciné.']
    """
    out = []
    for sentence, nums in sentence_citations(answer):
        words = _words(sentence)
        if not nums or not words:
            continue
        ok = any(len(words & _words(chunks[n - 1]["text"])) / len(words) >= min_overlap for n in nums if 1 <= n <= len(chunks))
        if not ok:
            out.append(sentence)
    return out


def render_sources(answer, chunks):
    """The "Sources" block shown under the answer, one line per cited
    source, in the order they're first cited: `[2] Title > Section (doc_id)`.

    Example:
        >>> chunks = [{"title": "R", "section": "Caution", "doc_id": "reg"}, {"title": "FAQ", "section": "", "doc_id": "faq"}]
        >>> print(render_sources("X [2]. Y [1][2].", chunks))
        [2] FAQ (faq)
        [1] R > Caution (reg)
    """
    lines = []
    for n in dict.fromkeys(n for _, nums in sentence_citations(answer) for n in nums):
        c = chunks[n - 1]
        head = f"{c['title']} > {c['section']}" if c.get("section") else c["title"]
        lines.append(f"[{n}] {head} ({c['doc_id']})")
    return "\n".join(lines)


if __name__ == "__main__":
    chunks = [{"title": "Règlement", "section": "Caution", "doc_id": "reglement", "text": "Le locataire paie une caution de deux mois de loyer."},
              {"title": "Règlement", "section": "Animaux", "doc_id": "reglement", "text": "Avec un animal, la caution augmente d'un demi-mois."}]
    raw = "La caution est de deux mois de loyer [1, 3]. Avec un chat, elle augmente d'un demi-mois [2]. Le chat doit être vacciné [2]."
    print("model said: ", raw)
    text, removed = clean_citations(raw, len(chunks))
    print("cleaned:    ", text, "| removed:", removed)
    print("coverage:   ", citation_coverage(text))
    print("unsupported:", unsupported_claims(text, chunks))
    print("Sources:\n" + render_sources(text, chunks))
