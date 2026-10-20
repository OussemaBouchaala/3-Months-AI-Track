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

## Your mission
Write Week 10's results page from Saturday's table, Thursday's taxonomy and Wednesday's cost model.

## Steps
1. Setup: test set size, languages, configs, judge, date.
2. Results: paste the table with intervals.
3. Recommendation with its trade-off; Failures with counts and examples; Cost per month.
4. Limitations: what this evaluation can't tell you.

## Done when
**Check** passes. This page goes into your README in Week 11 and your demo in Week 12.
