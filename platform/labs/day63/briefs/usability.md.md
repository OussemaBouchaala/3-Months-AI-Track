# Usability report
**Topic:** what real users did with your page, in numbers and observed problems ranked by severity.

## Real example
Ranking issues from a test of a train ticket app (different product, same triage):

```python
issues = [("Date picker hides the return date", "high", 4), ("Price shown without fees", "high", 3),
          ("Button label 'Proceed' unclear", "low", 1), ("No Arabic interface", "medium", 2)]
order = {"high": 0, "medium": 1, "low": 2}
for text, sev, users in sorted(issues, key=lambda i: (order[i[1]], -i[2])):
    print(f"- [{sev}] {text} ({users}/5 users)")
```

Severity says how bad it is; the user count says how common. Fix high and common first.

## Your mission
Write up Saturday's test and what you changed because of it.

## Steps
1. Participants and tasks, as run.
2. Results: the task table and the mean SUS with its grade.
3. Issues: 3 or more, each `[high]`, `[medium]` or `[low]`, with how many users hit it.
4. Changes made this weekend, and what Week 10 should measure.

## Done when
**Check** passes and at least one high-severity issue is fixed.
