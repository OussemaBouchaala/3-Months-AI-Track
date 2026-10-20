# Write up the agent
**Topic:** a one-page report with numbers and failures is worth more than a demo that "works".

## Real example
How a short, honest results paragraph reads (a different project: a meeting-scheduler agent):

```python
report = """## Results
14/20 scenarios succeed (70%), 3.1 steps on average, 1 forbidden action (booked without confirmation).

## Failures
- "Move my 3pm to tomorrow": called cancel_meeting before create_meeting; the create failed, the meeting was lost.
- "Lunch with Sami Friday": no time given; the agent invented 12:00 instead of asking.
"""
import re
print(report)
print("has a percentage:", bool(re.search(r"\\d+\\s*%", report)))
```

Numbers first, then concrete failures with the cause. No adjectives like "robust" or "smart".

## Your mission
Write the Week 5 report from your Saturday results.

## Steps
1. Fill every section; delete the `<!-- TODO -->` comments.
2. Results: the success rate as a percentage, and the number of scenarios.
3. Failures: at least 2, each with what happened and why.
4. Commit it next to your code.

## Done when
**Check** confirms every section is filled, with numbers and at least 2 failures.
