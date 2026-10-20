# Rerank the top 10
**Topic:** fast retrieval finds candidates; a slower, smarter model orders them.

## Real example
A job board shows 5 CVs out of 1,000. Step 1 (cheap) keeps 20 by keyword; step 2 (expensive) scores only those 20 with a careful reader. The "careful reader" is faked here with a rule:

```python
cvs = [{"name": "Sami", "text": "Python, pandas, 2 years data analysis"},
       {"name": "Lina", "text": "Java backend, Spring"},
       {"name": "Omar", "text": "Python, PyTorch, deployed 3 NLP models"}]

def careful_score(job, text):          # stands in for a cross-encoder or an LLM
    return sum(word in text for word in ["Python", "NLP", "deployed"]) * 3.0

job = "NLP engineer who ships models in Python"
ranked = sorted(cvs, key=lambda c: careful_score(job, c["text"]), reverse=True)
print([(c["name"], careful_score(job, c["text"])) for c in ranked[:2]])
```

## Your mission
Rerank the top 10 chunks with your model as a 0-10 judge.

## Steps
1. `score_prompt`: query, passage, "reply with a number from 0 to 10 only".
2. `parse_score`: first number, clamp to [0, 10], 0.0 if none.
3. `rerank`: score each, `sorted(..., reverse=True)` (Python's sort is stable, so ties keep their order), copy dicts with `{**c, "rerank_score": s}`.
4. **Run**: does the pets section (Animaux de compagnie) move up?

## Done when
**Check** passes and you've noted in your notes whether reranking changed the top 3.
