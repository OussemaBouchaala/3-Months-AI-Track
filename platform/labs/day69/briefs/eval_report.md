# The final evaluation
**Topic:** aggregate per-question results, attach intervals, check targets, and recommend the config that meets the constraints.

## Real example
Choosing a laptop under a budget and a weight limit (different choice, same rule: constraints first, then the best score):

```python
laptops = {"A": {"score": 92, "price": 3900, "kg": 1.3}, "B": {"score": 88, "price": 2600, "kg": 1.4},
           "C": {"score": 85, "price": 2400, "kg": 2.3}}
ok = {n: l for n, l in laptops.items() if l["price"] <= 3000 and l["kg"] <= 1.6}
print("pick:", max(ok, key=lambda n: (ok[n]["score"], -ok[n]["price"])))
```

The best laptop overall (A) is out of budget. A recommendation that ignores the constraints is not a recommendation.

## Your mission
Run your 2-3 best configs once on the golden **test** set and produce the table you'll publish.

## Steps
1. `aggregate`, `missed_targets`.
2. `choose`: hard constraints (latency, cost, citations), then accuracy.
3. `results_table` with injected `ci_fn` (day66's bootstrap in `__main__`).
4. Run the finalists on `golden_test.jsonl`, save `test_runs.json`, **Run**.

## Done when
**Check** passes and `results_table.md` names a recommended config, or says none meets the targets.
