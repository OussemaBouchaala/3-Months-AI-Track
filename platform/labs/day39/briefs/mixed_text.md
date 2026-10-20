# Mixed scripts and Arabizi
**Topic:** detect script and language per text (and per run) before deciding how to process it.

## Real example
A customer-support inbox routes messages to the right team by language. A tiny detector counts known words and characters, no model needed:

```python
import re

FR = {"bonjour", "merci", "commande", "le", "la", "est"}
EN = {"hello", "thanks", "order", "the", "is", "my"}

def route(msg):
    toks = re.findall(r"\w+", msg.lower())
    if sum(bool(re.search("[ء-ي]", t)) for t in toks) >= len(toks) / 2:
        return "arabic team"
    return "french team" if sum(t in FR for t in toks) >= sum(t in EN for t in toks) else "english team"

for m in ["Bonjour, ma commande est en retard", "Hello, my order is late", "طلبيتي متأخرة"]:
    print(route(m), "<-", m)
```

## Your mission
Detect scripts, Arabizi and language in Tunisian-style mixed text.

## Steps
1. `script_of` and `script_ratio` (use `collections.Counter`).
2. `is_arabizi`: has a letter and one of `2 3 5 7 9`.
3. `detect_lang`: Arabic or Arabizi majority → `"ar"`, else French vs English word counts.
4. `split_runs`: group consecutive tokens with the same script (`itertools.groupby` helps), skip digits.
5. **Run** on the 4 samples. Then try 10 real titles from Tayara and note where it's wrong.

## Done when
**Check** passes and your notes list what the detector gets wrong on real titles.
