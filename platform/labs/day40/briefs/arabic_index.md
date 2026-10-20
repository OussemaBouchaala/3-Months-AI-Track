# Sentence-aware chunks
**Topic:** cut on sentence boundaries (including ؟ and ؛), overlap by whole sentences, keep the document id.

## Real example
Subtitles for a video are packed into cards of at most 40 characters without cutting a sentence, and each card starts with the last sentence of the previous one so a reader never loses the thread:

```python
sentences = ["Hi.", "Welcome to Sousse.", "The beach is close.", "Rent is 900 TND.", "Call us!"]
max_chars, cards, cur = 40, [], []
for s in sentences:
    if cur and len(" ".join(cur + [s])) > max_chars:
        cards.append(" ".join(cur))
        cur = cur[-1:]                    # overlap: one sentence
    cur.append(s)
cards.append(" ".join(cur))
print(*cards, sep="\n")
```

## Your mission
Chunk the ARCD paragraphs by sentences and embed them.

## Steps
1. `split_sentences`: `SENT_END.split`, strip, drop empties.
2. `chunk_sentences`: the greedy packing above, with the "never only overlap" rule.
3. `build_chunks` and `doc_of`.
4. **Run** (Ollama with bge-m3 must be up). It saves `arcd_chunks.json` and `arcd_embeddings.npy`.

## Done when
**Check** passes and both files are saved.
