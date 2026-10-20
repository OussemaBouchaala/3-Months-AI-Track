# The eval harness
**Topic:** change one thing at a time, run the same questions, compare in one table.

## Real example
A coffee shop tests 4 recipes (2 beans x 2 grinds) on the same 3 tasters and keeps the best one under a price limit. The grid, the row per recipe, and the "best under a constraint" pick are exactly your harness:

```python
import itertools, statistics

scores = {("arabica", "fine"): [8, 9, 7], ("arabica", "coarse"): [6, 7, 6],
          ("robusta", "fine"): [7, 7, 8], ("robusta", "coarse"): [5, 6, 5]}
price = {"arabica": 2.5, "robusta": 1.5}

rows = [{"recipe": f"{b}-{g}", "score": statistics.mean(scores[b, g]), "price": price[b]}
        for b, g in itertools.product(["arabica", "robusta"], ["fine", "coarse"])]
for r in sorted(rows, key=lambda r: -r["score"]):
    print(f"| {r['recipe']} | {r['score']:.2f} | {r['price']:.2f} |")
ok = [r for r in rows if r["price"] <= 2.0]
print("best under 2 TND:", max(ok, key=lambda r: r["score"])["recipe"])
```

## Your mission
Run 8 configurations on your 50 questions and pick the one to keep.

## Steps
1. `config_grid`: `itertools.product`, build the name.
2. `run_config`: loop items, call `answer_fn` and `grade_fn`, aggregate (recall only on answerable items).
3. `results_table`: header, separator, one line per row, best `correct` first.
4. `pick_best`: filter by p95, then max by `(correct, -cost_1k)`.
5. **Run** (it takes a while: 8 configs x 50 questions). Commit `eval_results.md`.

## Done when
**Check** passes and `eval_results.md` holds your 8-row table.
