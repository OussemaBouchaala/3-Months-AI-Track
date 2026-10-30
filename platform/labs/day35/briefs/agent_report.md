# Write up the agent
**Topic:** a one-page report with numbers and failures is worth more than a demo that "works".

## How this report is built
The file in the editor is a complete example report for the week's visit-booking agent. Read it section by section and notice what each one does:

1. **What the agent does**: who uses it, what it can do, and what it **refuses** to do.
2. **Tools**: one bullet per tool, marked *read* (harmless) or *write* (changes the world).
3. **Results**: numbers first: `7/10 scenarios (70%)`, average steps, forbidden actions.
4. **Failures**: concrete cases, each with what happened in the trace and **why**.
5. **Guardrails**: what stops a bad action even when the model gets it wrong.
6. **Next**: one change, and how you would measure that it helped.

No "robust", no "smart": a reader trusts numbers and named failures, not adjectives.

## Real example
The same style on a different project, a meeting-scheduler agent:

```python
report = """## Results
14/20 scenarios succeed (70%), 3.1 steps on average, 1 forbidden action (booked without confirmation).

## Failures
- "Move my 3pm to tomorrow": called cancel_meeting before create_meeting; the create failed, the meeting was lost.
- "Lunch with Sami Friday": no time given; the agent invented 12:00 instead of asking.
"""
import re
print(report)
print("has a percentage:", bool(re.search(r"\d+\s*%", report)))
```

Press **Check** under the editor to see the rules a good report follows.
