# Phase 1 report
**Topic:** close Phase 1 with one page: data, pipeline, a results table, and honest failures.

## Real example
A results table that says something (a different project: French legal search):

```python
table = """| config | recall@5 | answer found |
|---|---|---|
| baseline (raw text) | 0.58 | 41% |
| + normalization | 0.66 | 47% |
| + hybrid BM25 | 0.74 | 52% |
| + rerank | 0.81 | 60% |"""
print(table)
best = max(table.splitlines()[2:], key=lambda r: float(r.split("|")[2]))
print("best:", best.split("|")[1].strip())
```

Each row adds one change, so each delta has a cause. A reader sees in five seconds what mattered.

## Your mission
Write the Phase 1 report from your Week 6 numbers (the table from Saturday's `arabic_eval.py`).

## Steps
1. Fill every section and delete the `<!-- TODO -->` comments.
2. Results: a Markdown table with a header and at least 2 configurations, real numbers.
3. What worked / What didn't: tie each bullet to a number or an example.
4. Next: what Phase 2 keeps and what it changes. Commit it.
