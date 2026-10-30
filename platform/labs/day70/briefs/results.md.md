# Evaluation report
**Topic:** setup, results with intervals, a recommendation under the targets, failures, cost, and limits.

## Real example
A recommendation paragraph that a manager can act on (different study: choosing an OCR engine):

```python
rec = ("Recommended: tesseract-5 + preprocessing. Character accuracy 0.94 [0.92, 0.96] vs 0.95 [0.93, 0.97] "
       "for the cloud API: the difference is inside the intervals, and it is free and keeps scans on our server. "
       "Trade-off: 3x slower (2.1 s per page), acceptable for overnight indexing.")
print(rec)
```

Choice, evidence with intervals, why it beats the alternative, and the trade-off you accept. Four sentences.

## How to read this example
An example evaluation report for week 10. Notice how it's built:

1. **Setup**: test set size, languages, configs, judge, date: enough for someone to repeat it.
2. **Results** with confidence intervals (day 66), so small differences aren't over-read.
3. **Recommendation** with its trade-off, checked against the targets.
4. **Failures** with counts and examples (day 68), **cost** per month (day 67), and **limitations**: what this evaluation can't tell you.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
