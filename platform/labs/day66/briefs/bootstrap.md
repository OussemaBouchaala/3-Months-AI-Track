# Confidence intervals
**Topic:** bootstrap a confidence interval for a score, and a paired interval for the difference between two configs.

## Real example
A shop measuring the share of customers who return within a month, from only 40 customers:

```python
import random
returned = [1] * 13 + [0] * 27
rng = random.Random(0)
means = sorted(sum(rng.choices(returned, k=40)) / 40 for _ in range(2000))
print(f"{sum(returned) / 40:.2f} [{means[50]:.2f}, {means[1949]:.2f}]")
```

"32%" sounds precise; "32%, somewhere between 18% and 48%" is the honest version with 40 customers.

## Your mission
Put an interval on every number in your Week 10 table, and test whether your best config really beats the baseline.

## Steps
1. `bootstrap_ci` (percentile method, seeded).
2. `paired_bootstrap_diff`: resample question indexes, not values, so both configs stay on the same questions.
3. `significant`, `format_ci`, `questions_needed`.
4. **Run**, then apply it to your real per-question results from the grid.

## Done when
**Check** passes and each config in your table has a `0.78 [0.66, 0.88]`-style score.
