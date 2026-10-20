# Grade the grader
**Topic:** raw agreement flatters; Cohen's kappa removes the agreement you'd get by luck.

## Real example
Two doctors read 10 X-rays (1 = fracture). They agree 8 times out of 10, which sounds great, until you see that both say "no fracture" almost always:

```python
a = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
b = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
p_o = sum(x == y for x, y in zip(a, b)) / len(a)
pa1, pb1 = sum(a) / len(a), sum(b) / len(b)
p_e = pa1 * pb1 + (1 - pa1) * (1 - pb1)
kappa = (p_o - p_e) / (1 - p_e)
print(f"agreement {p_o:.2f}, chance {p_e:.2f}, kappa {kappa:.2f}")
```

80% agreement, kappa below 0: they never agree on a fracture. That's the trap kappa catches.

## Your mission
Measure whether your judge grades like you do.

## Steps
1. Run your RAG on 20 test questions; grade each answer yourself (1/0) **before** looking at the judge.
2. Run the judge on the same 20; fill both lists.
3. `agreement`, `confusion`, `cohen_kappa`, `verdict`.
4. **Run**. If the verdict isn't "trust", read the disagreements and improve `judge_prompt` (e.g. add 2 graded examples).

## Done when
**Check** passes with your 20 + 20 labels, and you know if the judge is too kind or too harsh.
