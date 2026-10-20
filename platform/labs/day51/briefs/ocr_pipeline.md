# OCR for scanned pages
**Topic:** detect pages without text, OCR only those, then remove what layout adds: hyphenation, headers, page numbers.

## Real example
Cleaning a book's scanned pages (different documents, the same layout noise):

```python
import re
from collections import Counter
pages = ["THE OLD HOUSE\nIt was a cold mor-\nning.\n12", "THE OLD HOUSE\nShe opened the door.\n13"]
seen = Counter(l for p in pages for l in set(p.splitlines()))
clean = []
for p in pages:
    lines = [l for l in p.splitlines() if seen[l] < len(pages) and not l.strip().isdigit()]
    clean.append(re.sub(r"(?<=[a-z])-\n(?=[a-z])", "", "\n".join(lines)))
print(clean)
```

The running title on every page and the page numbers would otherwise end up inside your chunks, and in every embedding.

## Your mission
Write the page pipeline for your scanned documents.

## Steps
1. `needs_ocr` (letters in the text layer) and `text_quality`.
2. `dehyphenate` and `remove_repeated_lines`.
3. `process_pages` with an injected `ocr_fn` (so it's testable without Tesseract).
4. Install Tesseract with Arabic and French, then **Run** on one real scanned contract. Read the pages flagged under 0.9.

## Done when
**Check** passes and you know which of your documents are scans and how good their OCR is.
