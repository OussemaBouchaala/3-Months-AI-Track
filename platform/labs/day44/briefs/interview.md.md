# Interview a real user
**Topic:** 30 minutes with a real user beats a week of guessing. Write their words, their questions, their numbers.

## Real example
What good notes look like, from a different project (a pharmacy stock assistant):

```python
notes = {
    "workflow": ["Customer asks for a drug", "Check the shelf", "If missing, call 2 suppliers", "Write the order on paper"],
    "pain": ["Calls take 10-15 min per missing drug", "About 20 missing drugs a day", "Orders get lost on paper"],
    "questions": ["Est-ce que le Doliprane 1000 est en stock ?", "عندنا Augmentin للصغار؟", "Which supplier has the cheapest Ventoline?"],
}
for k, v in notes.items():
    print(k, len(v), "->", v[0])
```

Numbers ("20 a day", "10-15 min") turn a complaint into a target. Questions in the user's own language become your test set.

## How to read this example
An example of interview notes with an agency manager. Notice how it's built:

1. **Their workflow today**, in their words, before any talk of AI.
2. **Real questions, word for word**: these become test-set items, so they're quoted exactly, in the language the client used.
3. **Numbers they gave** (how many questions a day, how long an answer takes now): they become your targets on day 46.
4. **What would make them use it daily, and what they'd refuse**: the limits of your scope.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
