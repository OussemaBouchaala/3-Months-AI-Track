# Build the golden set
**Topic:** your project's test set: real questions, validated, deduplicated, covered by category and language, split once into dev and test.

## Real example
Splitting customer reviews by product so every product appears in the test set (a stratified split):

```python
import random
reviews = [("phone", i) for i in range(8)] + [("laptop", i) for i in range(4)] + [("tv", 0), ("tv", 1)]
dev, test = [], []
for cat in sorted({c for c, _ in reviews}):
    group = [r for r in reviews if r[0] == cat]
    random.Random(0).shuffle(group)
    k = max(1, round(len(group) * 0.3))
    test += group[:k]; dev += group[k:]
print(len(dev), "dev", len(test), "test:", sorted({c for c, _ in test}))
```

A plain random split could leave "tv" out of the test set entirely, and you'd never know the model fails on TVs.

## Your mission
Turn your interview questions into 20+ test items, check the set has no holes, and freeze a test split.

## Steps
1. Fill `GOLDEN` (20 or more): the interview's questions, variations in other languages, 2+ that the documents can't answer (`idk`), and actions.
2. `validate_item`, `norm_question`, `dedupe`, `coverage`.
3. `split_dev_test` (stratified, seeded) and `gaps`.
4. **Run**: it writes `golden_dev.jsonl` and `golden_test.jsonl`. Tune on dev only.

## Done when
**Check** passes, `gaps` prints "none" (or you know why not), and both files are committed.
