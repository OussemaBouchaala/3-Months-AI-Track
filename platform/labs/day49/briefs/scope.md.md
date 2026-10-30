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

## How to read this example
An example scope page, the agreement that closes week 7. Notice how it's built:

1. **In scope / Out of scope**: what will and won't be built. Saying no is half of scoping.
2. **Success metrics**: the numbers from `targets.py`, so "done" is measurable.
3. **Timeline**: one line per week, 8 to 12.
4. **Sign-off**: who agreed and when. A scope nobody else agreed to is only a wish.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
