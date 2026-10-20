# Scope on one page
**Topic:** what you'll build, what you won't, how you'll know it works, and who agreed.

## Real example
The "out of scope" list is what saves a project. From a different project (a clinic appointment bot):

```python
scope = {
    "in": ["Answer opening hours and prices", "Book, move, cancel appointments", "French and Derja"],
    "out": ["Medical advice of any kind", "Payments", "Voice messages", "Other clinics"],
}
for k, items in scope.items():
    print(k.upper(), "-", "; ".join(items))
```

When someone asks "can it also take payments?" in Week 10, the answer is already written: not in this version.

## Your mission
Close Week 7 with a scope your user (or the owner of the data) agrees to.

## Steps
1. Reuse your interview, decision matrix, targets and architecture.
2. Write In scope / Out of scope as bullets (3+ each).
3. Success metrics: copy the numbers from `targets.py`.
4. Timeline: one line per week, 8 to 12.
5. Send it to your user; write who agreed and when in Sign-off.

## Done when
**Check** passes and someone other than you has said yes to it.
