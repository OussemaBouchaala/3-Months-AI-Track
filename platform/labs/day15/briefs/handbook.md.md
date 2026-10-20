# The documents
**Topic:** your RAG corpus for this week: 14 policies of a (fictional) Sousse agency.

## Real example
Real company documents look like this file: one topic per `## ` heading, and the language changes from one section to the next. A quick look at its shape before you chunk anything:

```python
import re

doc = """## Fees
Buyers pay 2%.

## الضمان
شهرين من الكراء.

## Visites
Gratuites, du lundi au samedi."""
for heading in re.findall(r"^## (.+)$", doc, re.M):
    print(heading)
```

## Your mission
Read the handbook once, like a new employee. You'll ask questions about it all week.

## Steps
1. Skim every section. Notice the three languages.
2. Pick 3 questions you'd ask as a client (one per language). Keep them for Thursday.
3. Don't edit the file: the checks and the test set on Sunday rely on it.

## Done when
You know roughly what each section covers.
