# Answer with citations
**Topic:** the model answers only from numbered sources, cites them, and says "I don't know" otherwise.

## Real example
A hotel's FAQ bot. The model is faked, but look at the three pieces you'll build: numbered sources, a prompt with strict rules, and citations parsed back from the answer:

```python
import re

docs = [{"id": "h1", "heading": "Breakfast", "text": "Breakfast is served 7:00-10:30."},
        {"id": "h2", "heading": "Pool", "text": "The pool closes at 20:00."}]
context = "\n\n".join(f"[{i}] {d['heading']}\n{d['text']}" for i, d in enumerate(docs, 1))
prompt = ("Answer ONLY from the sources and cite them like [1]. If they don't say, reply: I don't know.\n\n"
          f"Sources:\n{context}\n\nQuestion: When does the pool close?")
fake_reply = "The pool closes at 20:00 [2]."

cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", fake_reply)})
print(prompt, "\n---\n", fake_reply, "-> cites", [docs[n - 1]["id"] for n in cited])
```

## Your mission
Turn retrieved chunks into a grounded, cited answer, and detect bad citations.

## Steps
1. `format_context`: `[n] heading`, newline, text, blank line between sources.
2. `build_prompt`: rules, sources, question. Put `IDK` in the rules word for word.
3. `parse_citations`: `re.findall`, `int`, unique, sorted.
4. `answer`: retrieve, prompt, call, map cited numbers to chunk ids, set `valid`.
5. **Run** with Ollama up (embeddings) and a model in ⚙ AI. The 4th question should get the IDK sentence.

## Done when
**Check** passes, and the car question gets "I don't know" instead of an invented answer.
