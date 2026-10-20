# Cut the handbook into chunks
**Topic:** fixed-size chunks with overlap vs one chunk per heading.

## Real example
A podcast app cuts long transcripts into overlapping windows so a search for "interest rates" finds the minute where it's discussed, even if the sentence crosses a cut:

```python
transcript = "Today we talk about interest rates. Rates went up twice this year. Next, housing prices in Tunis."
size, overlap = 40, 12
step = size - overlap
windows = []
for start in range(0, len(transcript), step):
    windows.append(transcript[start:start + size])
    if start + size >= len(transcript):
        break
for w in windows:
    print(repr(w))
```

Look at the ends and starts of neighbours: they share 12 characters.

## Your mission
Write both chunkers and save the handbook as 14 heading-based chunks.

## Steps
1. `chunk_fixed`: a `while` loop over start positions, `step = size - overlap`, stop when a piece reaches the end.
2. `split_by_heading`: `re.split(r"^## ", markdown, flags=re.M)`, drop the first part, then split each part into its first line (heading) and the rest (body).
3. `chunk_by_heading`: one chunk per section, `chunk_fixed` for long bodies, ids `c0`, `c1`...
4. **Run**: it prints both versions and writes `chunks.json` for tomorrow.

## Done when
**Check** passes and `chunks.json` has 14 chunks.
