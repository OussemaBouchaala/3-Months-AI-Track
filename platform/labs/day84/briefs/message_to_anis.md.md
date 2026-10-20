# The message to Anis
**Topic:** a short follow-up that answers exactly what he asked, shows the work, and makes a small, clear ask.

## Real example
Checking a follow-up email before sending (a different person and project):

```python
msg = """Subject: Churn model results, as promised
Hi Leila, when we met in October you asked whether churn could be predicted a month ahead.
On 2,000 held-out customers it flags 71% of churners with 40% precision, scores a customer in 30 ms,
and costs nothing to run on your existing server. It still misses customers who leave after a single bad call.
Code: https://github.com/x/churn  Demo: https://youtu.be/abc
Would you have 20 minutes next week to tell me whether this is useful for your team?"""
body = msg.split("\n", 1)[1]
print(len(body.split()), "words | ends with a question:", body.strip().endswith("?"))
```

Context in one line, his three questions answered with numbers, one honest limit, two links, one small ask.

## Your mission
Write and send the message that closes the program.

## Steps
1. Subject line, greeting, one line of context.
2. Accuracy (with the test set size), p95 latency, monthly cost: the numbers from results.md.
3. One limitation, the two links, and an ask that's easy to say yes to.
4. 120-250 words. Read it aloud once, then send it.

## Done when
**Check** passes and the message is sent.
