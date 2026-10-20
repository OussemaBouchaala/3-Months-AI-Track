# Load a real Arabic corpus
**Topic:** many questions share one paragraph: deduplicate the documents, keep the link from question to source.

## Real example
A news site's Q&A dataset: three rows, two share the same article. Same transformation you'll write: distinct documents get ids, every question points to its document:

```python
rows = [{"context": "Tunis is the capital of Tunisia.", "question": "Capital of Tunisia?", "answers": {"text": ["Tunis"]}},
        {"context": "Tunis is the capital of Tunisia.", "question": "Which country is Tunis the capital of?", "answers": {"text": ["Tunisia"]}},
        {"context": "Sfax is a port city.", "question": "What kind of city is Sfax?", "answers": {"text": ["a port city"]}}]
doc_id, docs, questions = {}, [], []
for r in rows:
    if r["context"] not in doc_id:
        doc_id[r["context"]] = f"d{len(docs)}"
        docs.append({"id": doc_id[r["context"]], "text": r["context"]})
    questions.append({"question": r["question"], "answer": r["answers"]["text"][0], "source_ids": [doc_id[r["context"]]]})
print(len(docs), "docs;", questions[1])
```

## Your mission
Download ARCD, turn it into a document collection plus a ready-made test set.

## Steps
1. `rows_url`: build the query string (or use `urllib.parse.urlencode`).
2. `fetch_rows`: loop over offsets 0, 100, 200... until `total`, collect `r["row"]`.
3. `to_corpus`: a dict from context to doc id; one question per row.
4. `save_jsonl` / `load_jsonl`.
5. **Run** (needs internet). Look at a few paragraphs: this is Modern Standard Arabic from Wikipedia.
6. Update `CORPUS_NAME` and `CORPUS_PATH` in `../day14/embeddings_intro.py` (they were placeholders).

## Done when
**Check** passes and `arcd_docs.jsonl` + `arcd_questions.jsonl` are on disk.
