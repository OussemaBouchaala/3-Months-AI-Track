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

## How to read this example
Example answers to five questions asked in every AI engineering interview. Notice how it's built:

1. Each answer is **80-250 words** (30-90 seconds spoken), first person, with at least one number.
2. They're built from real material: results, the failure taxonomy, the usability report, the architecture decisions.
3. **Q4** says what was learned; **Q5** names the alternative and the trade-off.
4. It ends with **three questions to ask them**.

Press **Check** under the editor to see the rules a good version follows. When you write your own, keep this structure and use your real numbers.
