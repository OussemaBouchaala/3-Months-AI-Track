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

## How to read this report
The file in the editor is a complete example Phase 1 report. Read it section by section:

1. **Data**: what was indexed and what it was tested on, with counts.
2. **Pipeline**: the steps, in order, in one short list.
3. **Results**: one table, where each row adds **one** change, so each gain has a cause.
4. **What worked / What didn't**: every bullet points to a number or a real example.
5. **Next**: what Phase 2 keeps and what it changes.

Press **Check** under the editor to see the rules a good report follows.
