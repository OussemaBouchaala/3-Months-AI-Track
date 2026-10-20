# The results table
**Topic:** report p50 and p95 latency; the mean hides the slow tail.

## Real example
A delivery app compares two routing services. Same recipe as your table: p50/p95, accuracy, cost, one Markdown line per option:

```python
import statistics

def p50_p95(xs):
    q = statistics.quantiles(xs, n=100, method="inclusive")
    return q[49], q[94]

rows = [
    {"model": "Router A", "accuracy": 0.91, "lat": [1.0, 1.1, 0.9, 1.2, 3.8], "cost_1k": "$0.80"},
    {"model": "Router B", "accuracy": 0.86, "lat": [0.4, 0.5, 0.4, 0.6, 0.7], "cost_1k": "free (own server)"},
]
print("| model | accuracy | p50 (s) | p95 (s) | cost per 1k |\n|---|---|---|---|---|")
for r in rows:
    p50, p95 = p50_p95(r["lat"])
    print(f"| {r['model']} | {r['accuracy']:.2f} | {p50:.2f} | {p95:.2f} | {r['cost_1k']} |")
```

## Your mission
Produce one table comparing both models on accuracy, latency and cost.

## Steps
1. `p50_p95`: `statistics.quantiles(..., n=100, method="inclusive")`, items 49 and 94.
2. `field_accuracy` and `cost_per_1k`.
3. `results_table`: one Markdown line per model under the header.
4. With the service running, **Run**: `results.md` is written.

## Done when
**Check** confirms the helpers and the table format.
