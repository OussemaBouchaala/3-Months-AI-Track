# Scanned contracts have no text layer: pypdf returns "" and your index silently misses them.
# Decide per page: text layer or OCR. Then clean what OCR and page layout add: hyphens, headers, page numbers.
import re
from collections import Counter

PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?[-–]?\s*\d+\s*(?:/\s*\d+)?\s*[-–]?\s*$", re.I)


def needs_ocr(page_text, min_letters=50):
    """True when the text layer has fewer than min_letters letters (str.isalpha, any script)."""
    # TODO
    ...


def text_quality(text):
    """Share of non-space characters that are letters, digits or common punctuation .,;:!?؟،؛'"()%-/
    0.0 for empty text. Clean text is above 0.95; OCR garbage like "|~}^ ¦" drags it down."""
    # TODO
    ...


def dehyphenate(text):
    """Join words split across lines with a hyphen: "loca-\\ntion" -> "location". Only between letters."""
    # TODO
    ...


def remove_repeated_lines(pages, min_share=0.6):
    """pages: list of page texts. A stripped, non-empty line that appears on at least min_share of the pages
    (and on at least 2 pages) is a header/footer: remove it everywhere. Also remove page-number lines
    (PAGE_NUMBER: "3", "- 3 -", "Page 3/10"). Return the cleaned pages."""
    # TODO
    ...


def process_pages(page_texts, ocr_fn, min_letters=50):
    """For each page i: keep its text layer, or call ocr_fn(i) if needs_ocr. Then remove_repeated_lines over all
    pages, then dehyphenate each page. Return [{"page": i + 1, "method": "text"|"ocr", "text": ..., "quality": ...}]."""
    # TODO
    ...


if __name__ == "__main__":
    # Needs: pip install pypdf pdf2image pytesseract, plus the Tesseract program with the "ara" and "fra" languages,
    # and Poppler for pdf2image. On Windows: the UB Mannheim Tesseract installer, tick Arabic and French.
    import sys
    from pdf2image import convert_from_path
    from pypdf import PdfReader
    import pytesseract

    path = sys.argv[1] if len(sys.argv) > 1 else "../docs/contrat_scan.pdf"
    texts = [p.extract_text() or "" for p in PdfReader(path).pages]
    ocr = lambda i: pytesseract.image_to_string(convert_from_path(path, dpi=300, first_page=i + 1, last_page=i + 1)[0], lang="ara+fra")
    for p in process_pages(texts, ocr):
        flag = "  <- check by hand" if p["quality"] < 0.9 else ""
        print(f"page {p['page']:3} {p['method']:4} quality {p['quality']:.2f} {len(p['text']):6} chars{flag}")
