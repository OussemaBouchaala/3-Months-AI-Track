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
    if len(text)==0: return []
    step = size - overlap
    start= 0
    chunks=[]
    while(start+size<len(text)):
        chunks.append(text[start:start+size])
        start= start+step
    chunks.append(text[start:])
    return chunks

def split_by_heading(markdown):
    """Split a Markdown document on lines that start with "## ".
    Return a list of (heading, body) tuples: heading without the "## ", body stripped.
    Text before the first "## " heading is ignored (it's the title and intro)."""
    # TODO: re.split(r"^## ", markdown, flags=re.M) is a good start
    parts=re.split(r"^## ", markdown, flags=re.M)
    result=[]
    for part in parts[1:]:
        heading, body = part.split("\n", maxsplit=1)
        result.append((heading.strip(), body.strip()))
    return result

def chunk_by_heading(markdown, max_chars=600, overlap=OVERLAP):
    """One chunk per section. A section whose body is longer than max_chars is cut with chunk_fixed.
    Return a list of dicts: {"id": "c0", "heading": heading, "text": heading + "\n" + piece}
    with ids c0, c1, c2... in document order. Keeping the heading in the text helps retrieval."""
    # TODO
    sections = split_by_heading(markdown)
    chunks=[]
    i=0
    for sec in sections:
        if len(sec[1])>max_chars:
            for piece in chunk_fixed(sec[1]):
                chunks.append({"id":"c"+str(i),
                "heading":sec[0],
                "text":sec[0]+"\n"+piece})
                i+=1
        else:
            chunks.append({"id":"c"+str(i),
            "heading":sec[0],
            "text":sec[0]+"\n"+sec[1]})
            i+=1
    return chunks

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
