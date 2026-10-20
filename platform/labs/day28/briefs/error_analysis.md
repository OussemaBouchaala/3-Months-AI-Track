# Why it fails
**Topic:** sort every failure into one bucket; the biggest bucket tells you what to fix.

## Real example
A delivery company sorts its 200 late orders by cause instead of staring at "8% late". Order matters: the first rule that matches wins.

```python
from collections import Counter

orders = [{"late": False}, {"late": True, "traffic": True}, {"late": True, "kitchen_slow": True},
          {"late": True, "traffic": True}, {"late": True}]

def bucket(o):
    if not o["late"]:
        return "ok"
    if o.get("kitchen_slow"):
        return "kitchen"
    if o.get("traffic"):
        return "traffic"
    return "unknown"

counts = Counter(bucket(o) for o in orders)
print(counts, "-> fix first:", max((b for b in counts if b != "ok"), key=counts.get))
```

## Your mission
Bucket every answer of your best configuration and find the biggest problem.

## Steps
1. Saturday's harness saved `../day27/per_question.json` (one record per question for your best config). Open it once.
2. `bucket`: follow the docstring order exactly.
3. `bucket_counts`, `examples`, `top_problem`.
4. **Run**, then read 3 examples of the top bucket and write in your notes what you'd change.

## Done when
**Check** passes and your notes name the top failure bucket with 3 real examples.
