# Real client documents: PDFs, Word files, web pages, text exports. Turn each into clean text + metadata.
# Standard library only, except PDFs (pypdf, already used for text PDFs; scans come tomorrow).
import io
import re
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
BLOCK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "table"}
INVISIBLE = "​‌‍‎‏﻿"     # zero-width chars, LRM/RLM marks, BOM


def detect_type(name, head):
    """Type from the first bytes (head) first, then the extension:
    b"%PDF" -> "pdf"; b"PK\\x03\\x04" (a zip) with a .docx name -> "docx";
    .html/.htm or head starting with b"<" (after whitespace) -> "html"; .txt/.md -> "text"; else "unknown"."""
    # TODO
    ...


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        pass   # TODO: entering <script>/<style>: self.skip += 1; a block tag: append "\n"

    def handle_endtag(self, tag):
        pass   # TODO: leaving <script>/<style>: self.skip -= 1; a block tag: append "\n"

    def handle_data(self, data):
        pass   # TODO: keep data only when not inside script/style


def html_to_text(html):
    """Visible text: no tags, no <script>/<style> content, entities decoded (&amp; -> &),
    a newline around block tags (p, div, br, li, h1-h6, ...)."""
    # TODO
    ...


def docx_to_text(data):
    """A .docx is a zip; the text is in word/document.xml. One line per paragraph (w:p),
    joining the w:t pieces inside it."""
    # TODO
    ...


def clean_text(text):
    """NFKC (turns Arabic presentation forms like ﻻ into normal letters), remove INVISIBLE chars,
    spaces/tabs collapsed to one space, spaces around newlines removed, 3+ newlines -> 2, strip."""
    # TODO
    ...


def parse_file(path):
    """{"id": file stem, "path": str(path), "type": ..., "text": clean text}. Raise ValueError for "unknown"."""
    path = Path(path)
    data = path.read_bytes()
    kind = detect_type(path.name, data[:8])
    if kind == "pdf":
        from pypdf import PdfReader
        raw = "\n\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    elif kind == "docx":
        raw = docx_to_text(data)
    elif kind == "html":
        raw = html_to_text(data.decode("utf-8", errors="replace"))
    elif kind == "text":
        raw = data.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"unknown file type: {path.name}")
    return {"id": path.stem, "path": str(path), "type": kind, "text": clean_text(raw)}


if __name__ == "__main__":
    import json
    import sys
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "../docs")
    docs, skipped = [], []
    for f in sorted(folder.glob("*")):
        try:
            docs.append(parse_file(f))
        except Exception as e:                       # one bad file must not stop the batch
            skipped.append((f.name, str(e)[:80]))
    Path("parsed.jsonl").write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in docs), encoding="utf-8")
    print(len(docs), "parsed;", len(skipped), "skipped:", skipped)
    for d in docs:
        print(f"{d['type']:5} {len(d['text']):7} chars  {d['id']}")
