# Failure taxonomy
**Topic:** one cause per failure, counted, sorted into a Pareto list, and sliced by language and document type.

## Real example
A call center sorting complaints by cause (different failures, same method):

```python
from collections import Counter
complaints = ["late delivery"] * 9 + ["wrong item"] * 4 + ["rude agent"] * 2 + ["billing"] * 1
counts = Counter(complaints).most_common()
total, run = len(complaints), 0
for cause, n in counts:
    run += n
    print(f"{cause:14} {n:2}  cumulative {run / total:.0%}")
```

Fixing deliveries alone removes 56% of complaints. The Pareto list tells you where one week of work pays most.

## Your mission
Explain your failures on the golden dev set and pick the one fix for Week 10.

## Steps
1. `classify` with the priority order (one label per case).
2. `taxonomy`, `pareto`.
3. `failure_rate_by` (language, document type) and `examples`.
4. Write `../day64/per_question.jsonl` from your best grid run (one line per question with these fields), then **Run**. Read 3 examples of the top category.

## Done when
**Check** passes and you know the top failure category, with 3 real examples read.
