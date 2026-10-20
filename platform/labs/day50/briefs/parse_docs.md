# Parse real documents
**Topic:** one function per format, clean text out, and a batch that survives a broken file.

## Real example
Extracting text from a spreadsheet saved as CSV, with invisible characters cleaned (a different format, same goal):

```python
import csv, io, re, unicodedata
raw = "﻿nom;ville\n‏سلمى;سوسة\nAli ;  Sfax\n"
rows = list(csv.reader(io.StringIO(raw), delimiter=";"))
clean = [[re.sub(r"\s+", " ", unicodedata.normalize("NFKC", c).replace("﻿", "").replace("‏", "")).strip() for c in r] for r in rows]
print(rows[0], "->", clean[0])
print(clean)
```

The BOM (`﻿`) at the start of an exported file and RLM marks in Arabic text are invisible, but they break string comparisons and keyword search.

## Your mission
Write the parser that turns your client's folder into `parsed.jsonl`.

## Steps
1. `detect_type`: magic bytes first (a `.docx` that is really a PDF happens).
2. `_Text` + `html_to_text` with `html.parser`.
3. `docx_to_text` with `zipfile` + `ElementTree`.
4. `clean_text`: NFKC, invisible chars, spaces, newlines.
5. **Run** `python parse_docs.py <your docs folder>`. Look at the skipped files and the shortest texts.

## Done when
**Check** passes and every document of your project is in `parsed.jsonl` or in the skipped list with a reason.
