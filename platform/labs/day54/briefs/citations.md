# Citations you can trust
**Topic:** one marker format, no invalid numbers, every sentence cited, and a cheap check that the source supports the sentence.

## Real example
A fact-checker comparing a news summary with its quotes (different domain, same word-overlap trick):

```python
import re
words = lambda t: {w for w in re.findall(r"\w+", t.lower()) if len(w) >= 4}
quote = "The minister announced a budget of 300 million for new schools in 2026."
claims = ["The budget for schools is 300 million.", "The minister resigned after the announcement."]
for c in claims:
    share = len(words(c) & words(quote)) / len(words(c))
    print(f"{share:.2f}", "supported" if share >= 0.5 else "CHECK", "-", c)
```

Word overlap is crude (it misses paraphrases and can't see negation), but it's free, instant, and catches the worst case: a citation that points to a chunk about something else.

## Your mission
Write the citation layer your API will run on every answer.

## Steps
1. `normalize_markers` and `clean_citations`.
2. `sentence_citations` (watch the "... TND. [2]" case) and `citation_coverage`.
3. `unsupported_claims` with word overlap.
4. `render_sources` for the UI.
5. **Run**: the example answer has one invalid marker and one invented sentence. Both are caught.

## Done when
**Check** passes. You'll log coverage and unsupported claims for every answer from Saturday on.
