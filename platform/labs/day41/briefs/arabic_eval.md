# Measure on Arabic
**Topic:** same metrics, new language: recall at document level, answer spans, and a delta column against the baseline.

## Real example
A team tests 3 spell-checkers against the simplest one. Showing the change against a baseline makes the table readable at a glance:

```python
rows = [{"variant": "no spell-check", "acc": 0.71}, {"variant": "dictionary", "acc": 0.78}, {"variant": "model", "acc": 0.69}]
base = rows[0]["acc"]
print("| variant | acc | Δ |\n|---|---|---|")
for r in rows:
    print(f"| {r['variant']} | {r['acc']:.2f} | {r['acc'] - base:+.2f} |")
```

The `+` in `:+.2f` always prints the sign, so losses stand out as clearly as gains.

## Your mission
Compare 4 retrieval variants on 100 real Arabic questions.

## Steps
1. `sample_questions` with a fixed seed (the same 100 every run).
2. `doc_ranking` and `doc_recall_at_k`: chunks → documents, then Week 4's recall.
3. `answer_found` (span containment after normalization).
4. `compare_table` with the Δ column.
5. **Run** (needs day36, day40 outputs and Ollama). Save `arabic_results.md`.

## Done when
**Check** passes and `arabic_results.md` shows whether normalization and stemming helped.
