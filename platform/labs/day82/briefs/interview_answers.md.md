# Interview answers
**Topic:** five answers you'll be asked in every AI engineering interview, built from your own numbers, in spoken length.

## Real example
Checking an answer's spoken length and substance (a different candidate's answer):

```python
answer = ("At my internship, our invoice parser failed on 30% of scanned invoices. I was asked to fix it in two weeks. "
          "I first measured where it failed: 70% of errors came from rotated scans, so I added orientation detection "
          "before OCR instead of tuning the model. I tested it on 200 held-out invoices. Failures dropped from 30% to 9%, "
          "and the remaining ones are handwritten, which I documented as out of scope.")
n = len(answer.split())
print(n, "words, about", round(n / 2.3), "seconds spoken")
print("numbers:", sum(c.isdigit() for c in answer) > 0, "| 'I' count:", answer.split().count("I"))
```

Situation in one sentence, then mostly what "I" did and why, then the result in numbers. About 40 seconds.

## Your mission
Prepare the five answers, then say each out loud until it takes 30-90 seconds without reading.

## Steps
1. Write each answer from your real material: results.md, the failure taxonomy, usability.md, architecture decisions.
2. Keep each 80-250 words, first person, with a number.
3. Q4 must say what you learned; Q5 must name the alternative and the trade-off.
4. Three questions for them. Record yourself answering Q1 once and listen to it.

## Done when
**Check** passes and you can answer Q1 and Q3 out loud without notes.
