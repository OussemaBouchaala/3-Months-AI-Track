# CV bullets that say something
**Topic:** a linter for CV lines: strong verb, a number, a tool, no filler, 10-30 words.

## Real example
The same work, written twice (a different job, the same rewrite):

```python
before = "Responsible for various tasks related to customer support automation."
after = "Automated 60% of tier-1 support tickets with a Python classifier, cutting first-response time from 4 hours to 9 minutes."
for b in (before, after):
    has_number = any(c.isdigit() for c in b)
    print(f"{'number' if has_number else 'NO NUMBER':9} | {b.split()[0]:12} | {b}")
```

The second one answers what you did, with what, and what changed, in one line.

## Your mission
Write the 4-6 CV bullets for this program, and make them pass your own linter.

## Steps
1. `lint` with every rule, `score`, `review`.
2. Write `BULLETS` from your real numbers (results.md, usability.md, cost model).
3. **Run** and fix until each scores 100.
4. Paste them into your CV under a "Projects" entry with the repository link.

## Done when
**Check** passes and the bullets are in your CV.
