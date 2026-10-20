# Cut the handbook into chunks a retriever can find. Check runs on small strings, no model needed.
import json
import re

SIZE = 400       # characters per chunk for fixed-size chunking
OVERLAP = 80     # characters shared by two neighbouring chunks


def chunk_fixed(text, size=SIZE, overlap=OVERLAP):
    """Cut text into pieces of `size` characters. Each piece starts `size - overlap` characters
    after the previous one, so neighbours share `overlap` characters.
    Stop once a piece reaches the end of the text. Empty text -> [].
    Example: chunk_fixed("abcdefghij", 4, 1) -> ["abcd", "defg", "ghij"]"""
    # TODO
    ...


def split_by_heading(markdown):
    """Split a Markdown document on lines that start with "## ".
    Return a list of (heading, body) tuples: heading without the "## ", body stripped.
    Text before the first "## " heading is ignored (it's the title and intro)."""
    # TODO: re.split(r"^## ", markdown, flags=re.M) is a good start
    ...


def chunk_by_heading(markdown, max_chars=600, overlap=OVERLAP):
    """One chunk per section. A section whose body is longer than max_chars is cut with chunk_fixed.
    Return a list of dicts: {"id": "c0", "heading": heading, "text": heading + "\n" + piece}
    with ids c0, c1, c2... in document order. Keeping the heading in the text helps retrieval."""
    # TODO
    ...


if __name__ == "__main__":
    doc = open("handbook.md", encoding="utf-8").read()

    fixed = chunk_fixed(doc)
    print(f"fixed: {len(fixed)} chunks; one of them starts mid-sentence:\n  {fixed[3][:70]!r}")

    chunks = chunk_by_heading(doc)
    print(f"by heading: {len(chunks)} chunks")
    for c in chunks:
        print(f"  {c['id']:>4}  {len(c['text']):>4} chars  {c['heading']}")

    json.dump(chunks, open("chunks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved chunks.json (Tuesday embeds it)")
