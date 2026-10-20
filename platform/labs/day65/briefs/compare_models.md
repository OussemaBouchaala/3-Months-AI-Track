# Local vs API model
**Topic:** per-category scores, pairwise judging with swapped positions, and a paired comparison on the same questions.

## Real example
Two translators compared by a reviewer who tends to prefer whatever they read first (different task, same bias):

```python
verdicts = {  # (A=Lina, B=Omar) then swapped (A=Omar, B=Lina)
    "doc1": ("A", "B"),   # Lina wins both orders -> Lina
    "doc2": ("A", "A"),   # "first one" both times -> position bias, call it a tie
    "doc3": ("B", "A"),   # Omar wins both orders -> Omar
}
def outcome(ab, ba):
    return "Lina" if (ab, ba) == ("A", "B") else "Omar" if (ab, ba) == ("B", "A") else "tie"
print({d: outcome(*v) for d, v in verdicts.items()})
```

LLM judges have the same first-position bias. Judging both orders and only counting consistent wins removes it.

## Your mission
Compare your two candidate models on the golden dev set.

## Steps
1. `per_category` (where does each model win?).
2. `parse_preference`, `debias`, `win_rate`.
3. `paired`: which questions only one model gets right?
4. Generate `answers_local.jsonl` and `answers_api.jsonl` with your pipeline (one line per question: id, question, sources, answer, category, correct), then **Run**.

## Done when
**Check** passes and you can say where the local model loses, by category.
