"""Real client documents come as PDFs, Word files, web pages and text exports.
Turn each one into **clean text plus metadata**, the input of everything that follows.

1. `detect_type`: what kind of file is this? Trust the first bytes, then the name.
2. `_Text` and `html_to_text`: the visible text of a web page.
3. `docx_to_text`: the paragraphs of a Word file (it's a zip of XML).
4. `clean_text`: remove invisible marks, odd Arabic forms and extra spaces.
5. `parse_file`: one file in, one `{"id", "path", "type", "text"}` record out.

Standard library only, except PDFs (pypdf, as in Week 2; scans come tomorrow).
"""
import io
import re
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"   # the Word XML namespace
BLOCK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "table"}
INVISIBLE = "​‌‍‎‏﻿"     # zero-width chars, LRM/RLM marks, BOM


def detect_type(name, head):
    """The file type, from its first bytes (`head`) first, then its extension.

    Clients rename files carelessly: a "contrat.docx" can really be a PDF.
    Every file format starts with a signature ("magic bytes"):

    - `%PDF` means a PDF, whatever the name says.
    - `PK\\x03\\x04` means a zip. A .docx is a zip, but so is a .xlsx,
      so the name decides between them.
    - A file starting with `<` (after spaces) is HTML.
    - `.txt` and `.md` are plain text. Anything else is `"unknown"`.

    Example:
        >>> detect_type("contrat.docx", b"%PDF-1.7")
        'pdf'
        >>> detect_type("a.docx", b"PK\\x03\\x04"), detect_type("a.xlsx", b"PK\\x03\\x04")
        ('docx', 'unknown')
        >>> detect_type("noext", b"  <html>"), detect_type("notes.md", b"# Fees")
        ('html', 'text')
    """
    ext = Path(name).suffix.lower()
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"PK\x03\x04") and ext == ".docx":
        return "docx"
    if ext in (".html", ".htm") or head.lstrip().startswith(b"<"):
        return "html"
    if ext in (".txt", ".md"):
        return "text"
    return "unknown"


class _Text(HTMLParser):
    """An HTML parser that keeps only the text a person would see.

    `HTMLParser` reads the page and calls a method for each piece:
    `handle_starttag` for `<p>`, `handle_endtag` for `</p>`, `handle_data`
    for the text in between. `convert_charrefs=True` turns `&amp;` into `&`.

    - `skip` counts how deep we are inside `<script>` or `<style>`: their
      content is code, not text.
    - A block tag (`p`, `div`, `li`, `h1`...) adds a newline, so paragraphs
      don't run into each other.

    Example:
        >>> p = _Text()
        >>> p.feed("<p>Hi</p><script>x=1</script><b>there</b>")
        >>> p.parts
        ['\\n', 'Hi', '\\n', 'there']
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(html):
    """The visible text of a web page: feed it to `_Text`, join the pieces.

    The result still has extra newlines; `clean_text` tidies them later.

    Example:
        >>> page = "<style>p{color:red}</style><h1>Frais</h1><p>Loyer &amp; charges</p>"
        >>> html_to_text(page)
        '\\nFrais\\n\\nLoyer & charges\\n'
    """
    p = _Text()
    p.feed(html)
    return "".join(p.parts)


def docx_to_text(data):
    """The text of a Word file, one line per paragraph.

    A .docx is a zip; the text lives in `word/document.xml`. Each paragraph
    is a `<w:p>`, and Word splits its text into "runs" `<w:t>` wherever the
    formatting changes (bold, a typo it underlined...). So: for each
    paragraph, join its `w:t` pieces.

    `p.iter(W_NS + "t")` finds every `w:t` inside the paragraph; the
    namespace is part of the tag name in ElementTree.

    Example (we build a tiny .docx in memory):
        >>> buf = io.BytesIO()
        >>> body = "<w:p><w:r><w:t>Frais </w:t></w:r><w:r><w:t>d'agence</w:t></w:r></w:p><w:p><w:r><w:t>Caution</w:t></w:r></w:p>"
        >>> xml = f'<w:document xmlns:w="{W_NS[1:-1]}"><w:body>{body}</w:body></w:document>'
        >>> with zipfile.ZipFile(buf, "w") as z:
        ...     z.writestr("word/document.xml", xml)
        >>> docx_to_text(buf.getvalue())
        "Frais d'agence\\nCaution"
    """
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        root = ElementTree.fromstring(z.read("word/document.xml"))
    return "\n".join("".join(t.text or "" for t in p.iter(W_NS + "t")) for p in root.iter(W_NS + "p"))


def clean_text(text):
    """Make text from any source look the same before chunking.

    1. **NFKC** turns compatibility forms into normal letters: the ligature
       `ﻻ` that some PDFs produce becomes the two letters `لا`.
    2. Remove invisible characters (zero-width, LRM/RLM direction marks, BOM):
       they break keyword search silently.
    3. Collapse runs of spaces, tabs and non-breaking spaces into one space.
    4. Remove spaces at the start and end of lines.
    5. Three or more newlines become two (at most one empty line).

    Example:
        >>> clean_text("\\u200fمرحبا \\u200b  بكم\\t!")
        'مرحبا بكم !'
        >>> clean_text("ﻻ")
        'لا'
        >>> clean_text("  a  \\n\\n\\n\\n  b \\n")
        'a\\n\\nb'
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.translate({ord(c): None for c in INVISIBLE})
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_file(path):
    """One file in, one record out: `{"id": file stem, "path", "type", "text"}`.

    Read the bytes once, detect the type from the first 8, then use the
    right extractor and clean the result. An unknown type raises
    `ValueError`, so the batch loop can skip that file and say why.

    Example:
        >>> import tempfile
        >>> f = Path(tempfile.mkdtemp()) / "frais.html"
        >>> _ = f.write_text("<h1>Frais</h1><p>Loyer &amp; charges</p>", encoding="utf-8")
        >>> rec = parse_file(f)
        >>> rec["id"], rec["type"], rec["text"]
        ('frais', 'html', 'Frais\\n\\nLoyer & charges')
    """
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


def parse_folder(folder):
    """Parse every file of a folder. Returns `(docs, skipped)`.

    One bad file must not stop the batch: its error goes into `skipped`
    with the file name, and the loop moves on.

    Example:
        >>> import tempfile
        >>> d = Path(tempfile.mkdtemp())
        >>> _ = (d / "a.txt").write_text("Bonjour", encoding="utf-8")
        >>> _ = (d / "b.xlsx").write_bytes(b"PK\\x03\\x04")
        >>> docs, skipped = parse_folder(d)
        >>> [x["id"] for x in docs], skipped
        (['a'], [('b.xlsx', 'unknown file type: b.xlsx')])
    """
    docs, skipped = [], []
    for f in sorted(Path(folder).glob("*")):
        try:
            docs.append(parse_file(f))
        except Exception as e:
            skipped.append((f.name, str(e)[:80]))
    return docs, skipped


def run_on_my_docs(folder="../docs", out="parsed.jsonl"):
    """The real run: parse your client's folder and write `parsed.jsonl`
    (one JSON record per line), which day 52 reads.

    Example (note): needs your documents in ../docs.
        >>> run_on_my_docs()  # doctest: +SKIP
    """
    import json
    docs, skipped = parse_folder(folder)
    Path(out).write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in docs), encoding="utf-8")
    print(len(docs), "parsed;", len(skipped), "skipped:", skipped)
    for d in docs:
        print(f"{d['type']:5} {len(d['text']):7} chars  {d['id']}")


if __name__ == "__main__":
    import sys
    import tempfile
    if len(sys.argv) > 1 or Path("../docs").is_dir():
        run_on_my_docs(sys.argv[1] if len(sys.argv) > 1 else "../docs")
    else:
        # No ../docs yet: build a small mixed folder and parse it.
        demo = Path(tempfile.mkdtemp())
        (demo / "frais.html").write_text("<html><script>track()</script><h1>Frais d'agence</h1>"
                                         "<p>Un mois de loyer &amp; TVA</p></html>", encoding="utf-8")
        (demo / "faq.md").write_text("# FAQ\n\n\n\nLa caution :   ‏شهرين", encoding="utf-8")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("word/document.xml", f'<w:document xmlns:w="{W_NS[1:-1]}"><w:body>'
                       "<w:p><w:r><w:t>Article 1 - </w:t></w:r><w:r><w:t>Loyer</w:t></w:r></w:p>"
                       "<w:p><w:r><w:t>900 TND par mois.</w:t></w:r></w:p></w:body></w:document>")
        (demo / "bail.docx").write_bytes(buf.getvalue())
        (demo / "tarifs.xlsx").write_bytes(b"PK\x03\x04 not a docx")
        docs, skipped = parse_folder(demo)
        print(len(docs), "parsed;", len(skipped), "skipped:", skipped)
        for d in docs:
            print(f"--- {d['type']:5} {d['id']}\n{d['text']}")
