"""Scanned contracts have no text layer: pypdf returns "" and your index silently misses them.

Decide **page by page**: keep the text layer when it's there, run OCR when it isn't.
Then clean what OCR and page layout add: words cut by hyphens, headers repeated on
every page, page numbers.

1. `needs_ocr`: is this page's text layer empty or almost?
2. `text_quality`: a 0-1 score that flags OCR garbage.
3. `dehyphenate`: "loca-\\ntion" back to "location".
4. `remove_repeated_lines`: headers, footers and page numbers out.
5. `process_pages`: the whole pipeline over a document.
"""
import re
from collections import Counter

# A line that is only a page number: "3", "- 3 -", "Page 3/10", "page 3".
PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?[-–]?\s*\d+\s*(?:/\s*\d+)?\s*[-–]?\s*$", re.I)


def needs_ocr(page_text, min_letters=50):
    """True when the page's text layer has fewer than `min_letters` letters.

    A scanned page often has no text at all, or just a stray page number.
    Counting **letters** (`str.isalpha`, true for Arabic and Latin alike)
    ignores digits and dashes. `page_text or ""` treats `None` as empty.

    Example:
        >>> needs_ocr(""), needs_ocr(None), needs_ocr("12 / 3 \\n --")
        (True, True, True)
        >>> needs_ocr("Le locataire paie un mois de loyer hors charges à la signature.")
        False
    """
    return sum(c.isalpha() for c in page_text or "") < min_letters


def text_quality(text):
    """The share of non-space characters that look like real text.

    Letters, digits and common punctuation (including the Arabic `؟ ، ؛`)
    count as good. Clean text scores about 1.0; OCR garbage like `|~}^ ¦`
    drags the score down, so you know which pages to check by hand.

    Example:
        >>> text_quality("Loyer: 900 TND (charges).")
        1.0
        >>> round(text_quality("Loyer |~}^ ¦"), 2)
        0.5
        >>> text_quality("")
        0.0
    """
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    good = sum(c.isalnum() or c in ".,;:!?؟،؛'\"()%-/" for c in chars)
    return good / len(chars)


def dehyphenate(text):
    """Join words that the layout split across two lines with a hyphen.

    `[^\\W\\d_]` means "a letter" (a word character that is not a digit or
    `_`). The lookbehind `(?<=...)` and lookahead `(?=...)` require a letter
    on both sides of `-\\n` without consuming it, so only `-\\n` is removed.
    A real dash between numbers ("2024-\\n2025") stays.

    Example:
        >>> dehyphenate("la loca-\\ntion annuelle")
        'la location annuelle'
        >>> dehyphenate("2024-\\n2025")
        '2024-\\n2025'
    """
    return re.sub(r"(?<=[^\W\d_])-\n(?=[^\W\d_])", "", text)


def remove_repeated_lines(pages, min_share=0.6):
    """Remove headers, footers and page numbers from every page.

    1. Count on how many pages each line appears (a `set` per page, so a
       line counted twice on one page still counts once).
    2. A line on at least `min_share` of the pages, and on at least 2 pages,
       is a header or footer: it goes.
    3. Lines that match `PAGE_NUMBER` go too.

    Without this, "Dar Yasmine - Contrat" becomes the most "relevant" text in
    your index, since it's in every chunk.

    Example:
        >>> pages = ["Dar Yasmine\\nArticle 1\\n- 1 -", "Dar Yasmine\\nArticle 2\\n- 2 -", "Dar Yasmine\\nArticle 3\\nPage 3/3"]
        >>> remove_repeated_lines(pages)
        ['Article 1', 'Article 2', 'Article 3']
        >>> remove_repeated_lines(["A\\nB", "A\\nC", "D"])
        ['B', 'C', 'D']
    """
    counts = Counter(l for p in pages for l in {x.strip() for x in p.splitlines() if x.strip()})
    repeated = {l for l, n in counts.items() if n >= 2 and n >= min_share * len(pages)}
    return ["\n".join(l for l in p.splitlines() if l.strip() not in repeated and not PAGE_NUMBER.match(l)) for p in pages]


def process_pages(page_texts, ocr_fn, min_letters=50):
    """The pipeline for one document.

    1. For each page: keep its text layer, or call `ocr_fn(i)` when
       `needs_ocr` says so (OCR is slow, so only where needed).
    2. Remove repeated lines **across all pages** (it needs to see them all).
    3. Dehyphenate each page and score its quality.

    `ocr_fn` is passed in, so you can test the pipeline with a fake OCR and
    plug Tesseract in for real.

    Example:
        >>> fake_ocr = lambda i: f"Article {i}: le loca-\\ntaire paie {i + 1} mois de caution."
        >>> for p in process_pages(["Le locataire paie un mois de loyer hors charges à la signature du bail.", ""], fake_ocr):
        ...     print(p["page"], p["method"], p["quality"], p["text"])
        1 text 1.0 Le locataire paie un mois de loyer hors charges à la signature du bail.
        2 ocr 1.0 Article 1: le locataire paie 2 mois de caution.
    """
    methods, texts = [], []
    for i, t in enumerate(page_texts):
        if needs_ocr(t, min_letters):
            methods.append("ocr")
            texts.append(ocr_fn(i))
        else:
            methods.append("text")
            texts.append(t)
    texts = [dehyphenate(t) for t in remove_repeated_lines(texts)]
    return [{"page": i + 1, "method": m, "text": t, "quality": round(text_quality(t), 3)} for i, (m, t) in enumerate(zip(methods, texts))]


def print_report(pages):
    """One line per page; a quality under 0.9 is flagged for a human check.

    Example:
        >>> print_report([{"page": 1, "method": "ocr", "quality": 0.72, "text": "x" * 40}])
        page   1 ocr  quality 0.72     40 chars  <- check by hand
    """
    for p in pages:
        flag = "  <- check by hand" if p["quality"] < 0.9 else ""
        print(f"page {p['page']:3} {p['method']:4} quality {p['quality']:.2f} {len(p['text']):6} chars{flag}")


def run_on_my_scan(path="../docs/contrat_scan.pdf"):
    """The real run on a scanned PDF, with Tesseract.

    Needs: `pip install pypdf pdf2image pytesseract`, the Tesseract program
    with the "ara" and "fra" languages, and Poppler for pdf2image. On
    Windows: the UB Mannheim Tesseract installer, tick Arabic and French.

    Example (note): needs Tesseract and your scan.
        >>> run_on_my_scan()  # doctest: +SKIP
    """
    from pdf2image import convert_from_path
    from pypdf import PdfReader
    import pytesseract

    texts = [p.extract_text() or "" for p in PdfReader(path).pages]
    ocr = lambda i: pytesseract.image_to_string(convert_from_path(path, dpi=300, first_page=i + 1, last_page=i + 1)[0], lang="ara+fra")
    print_report(process_pages(texts, ocr))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_on_my_scan(sys.argv[1])
    else:
        # A 3-page contract: page 1 has a text layer, pages 2 and 3 are scans.
        layer = ["Dar Yasmine - Contrat de location\nArticle 1 - Loyer\nLe loyer mensuel est de neuf cents dinars, payable "
                 "avant le cinq de chaque mois.\n- 1 -", "", "  2 "]
        scans = {1: "Dar Yasmine - Contrat de location\nArticle 2 - Caution\nLe loca-\ntaire verse deux mois de caution, "
                    "rembour-\nsée sous trente jours.\n- 2 -",
                 2: "Dar Yasmine - Contrat de location\nArticle 3 ~|~ Signa^ture\n¦¦ Fait à Tunis |~} le ~~\n- 3 -"}
        pages = process_pages(layer, lambda i: scans[i])
        print_report(pages)
        for p in pages:
            print(f"--- page {p['page']}\n{p['text']}")
