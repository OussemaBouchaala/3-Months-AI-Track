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

## How to read this example
An example usability report after testing the chat page with real users. Notice how it's built:

1. **Participants and tasks**, as they were run.
2. **Results**: a task table (success, time) and the mean SUS score with its grade (day 62).
3. **Issues** ranked `[high]`, `[medium]`, `[low]`, each with how many users hit it.
4. **Changes made** because of the test, and what week 10 should measure.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
