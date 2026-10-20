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

## Your mission
Interview one real person who would use your Phase 2 project, and write the notes here.

## Steps
1. Book 30 minutes. Ask about their **current** workflow, not about AI.
2. Ask them to show you real documents and real questions from last week.
3. Fill every section; quote their questions word for word (8 or more).
4. Ask what would make them use it daily, and what they'd refuse.

## Done when
**Check** passes and you have 8 real questions for your test set.
