# Success targets
**Topic:** accuracy, latency and cost targets agreed before you build, and a function that checks them after every run.

## Real example
A delivery app's targets (different product, same discipline):

```python
import math
times = [22, 35, 28, 41, 30, 26, 55, 33, 29, 31]          # delivery minutes
s = sorted(times)
p95 = s[math.ceil(0.95 * len(s)) - 1]
print("p95 =", p95, "->", "OK" if p95 <= 45 else "MISS", "(target <= 45 min)")
print("mean =", sum(times) / len(times))
```

The mean (33 min) looks fine; the p95 (55 min) is what angry customers feel. Latency targets use percentiles.

## Your mission
Turn your interview into 4 numeric targets, and write the checker you'll run after every evaluation.

## Steps
1. Edit `TARGETS` from your user's words ("10 seconds", "30 TND a month").
2. `percentile` (nearest rank), `cost_per_query`.
3. `summarize` a list of runs, then `check_targets` and `report`.
4. **Run** on the fake runs. In Week 10 you'll feed it real ones.

## Done when
**Check** passes and each target in `TARGETS` traces back to something your user said.
