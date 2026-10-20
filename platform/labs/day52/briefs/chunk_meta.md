# Chunks with metadata
**Topic:** sections, stable ids, content hashes and a contextual header, so a chunk knows where it comes from.

## Real example
Recipes split by heading, each step keeping its recipe and section (a different corpus, same idea):

```python
import hashlib
text = "# Couscous\n## Ingredients\nSemolina, lamb.\n## Steps\nSteam twice."
section, out = "", []
for line in text.splitlines():
    if line.startswith("#"):
        section = line.lstrip("#").strip()
    else:
        out.append({"section": section, "text": line, "hash": hashlib.sha1(line.encode()).hexdigest()[:8],
                    "embed_text": f"Couscous > {section}\n{line}"})
for c in out:
    print(c)
```

"Steam twice." alone is meaningless to an embedding model; "Couscous > Steps / Steam twice." isn't.

## Your mission
Turn `parsed.jsonl` into chunks that carry their document, section, language and hash.

## Steps
1. `split_sections` with the `HEADING` pattern (adjust it to your documents' headings).
2. `content_hash`.
3. `make_chunks` with an injected chunker and language detector (Week 6's).
4. `dedupe_chunks`: the same clause in 40 contracts should be stored once.
5. **Run** and read 5 chunks' `embed_text`.

## Done when
**Check** passes and `chunks.json` exists with sections filled for most chunks.
