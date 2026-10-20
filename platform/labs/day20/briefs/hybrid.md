# Hybrid search
**Topic:** BM25 for exact words, vectors for meaning, RRF to merge two rankings without comparing their scores.

## Real example
Two judges rank 4 restaurants. Their scores are on different scales, so you can't add them, but you can add **rank points**. That's RRF:

```python
judge_a = ["Dar El Jeld", "Le Golfe", "Chez Slah", "El Ali"]   # best first
judge_b = ["Le Golfe", "El Ali", "Dar El Jeld", "Chez Slah"]

points = {}
for ranking in (judge_a, judge_b):
    for rank, name in enumerate(ranking, start=1):
        points[name] = points.get(name, 0) + 1 / (60 + rank)
for name in sorted(points, key=points.get, reverse=True):
    print(f"{points[name]:.4f}  {name}")
```

"Le Golfe" wins: second for one judge, first for the other, consistently near the top.

## Your mission
Implement BM25 and RRF, then compare keyword, vector and hybrid rankings.

## Steps
1. `tokenize`: `re.findall(r"\w+", text.lower())`.
2. `bm25_scores`: tokenize docs once; `Counter` gives tf; compute df per query term; follow the docstring formula.
3. `rank_ids`: `sorted(ids, key=..., reverse=True)` with scores zipped by position.
4. `rrf`: add `1 / (k + rank)` per ranking, sort.
5. **Run**: which query does keyword win? Which does vector win? Does hybrid get both?

## Done when
**Check** passes and your notes say which kind of query each method is good at.
