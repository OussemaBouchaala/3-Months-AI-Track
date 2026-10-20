# Measure retrieval
**Topic:** recall@k asks "is the right chunk in what the model will see?"; MRR asks "how high?".

## Real example
An online shop measures its product search with 3 test queries and the product a human said is right. Same three metrics you'll write:

```python
tests = [("red running shoes", ["p7"], ["p2", "p7", "p9"]),
         ("chaussures de course rouges", ["p7"], ["p7", "p1", "p2"]),
         ("waterproof jacket", ["p4"], ["p1", "p2", "p3"])]
for k in (1, 3):
    hits = [len(set(rel) & set(got[:k])) / len(rel) for _, rel, got in tests]
    print(f"recall@{k} = {sum(hits) / len(hits):.2f}")
rr = [next((1 / pos for pos, i in enumerate(got, 1) if i in rel), 0.0) for _, rel, got in tests]
print(f"MRR = {sum(rr) / len(rr):.2f}")
```

## Your mission
Score keyword, vector and hybrid retrieval on your 50 questions.

## Steps
1. `recall_at_k`: set intersection over `len(relevant)`.
2. `hit_at_k` and `reciprocal_rank` (first relevant position, from 1).
3. `evaluate_retrieval`: skip unanswerable items, average each metric with `statistics.mean`.
4. **Run**: it prints one Markdown table row per retriever. Paste it in your notes.

## Done when
**Check** passes and you have recall@1/3/5 and MRR for all three retrievers.
