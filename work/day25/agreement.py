"""Can you trust the judge?

An LLM judge grades your RAG answers (1 = correct, 0 = wrong). Before you believe its
numbers, compare it with your own grades on the same 20 answers.

The file builds four tools, each on top of the previous one:

1. `agreement`: how often you and the judge give the same grade.
2. `confusion`: *how* you disagree: is the judge too kind or too harsh?
3. `cohen_kappa`: agreement with the "lucky" part removed. This is the number to trust.
4. `verdict`: turns kappa into a decision.

`MY_LABELS` and `JUDGE_LABELS` are an example: 20 answers, graded by a person and by the judge.
"""

# 1 = the answer is correct, 0 = it's wrong. Same 20 answers, same order in both lists.
MY_LABELS = [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1]
JUDGE_LABELS = [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1]


def agreement(a, b):
    """Share of positions where the two lists hold the same grade.

    `zip(a, b)` walks both lists side by side. `x == y` is True (counts as 1)
    or False (counts as 0), so `sum(...)` counts the matches. Dividing by the
    length turns the count into a share between 0 and 1.

    This number is easy to read but it **flatters**: if most answers are
    correct, a lazy judge that always says 1 still agrees a lot.

    Example:
        >>> agreement([1, 0, 1, 1], [1, 1, 1, 0])
        0.5
        >>> agreement([1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [1] * 10)
        0.9
    """
    return sum(x == y for x, y in zip(a, b)) / len(a)


def confusion(human, judge):
    """Count the four possible (human, judge) pairs.

    - `both_1`: both say correct.
    - `both_0`: both say wrong.
    - `judge_too_kind`: you said wrong (0), the judge said correct (1).
      The **dangerous** one: it hides real failures.
    - `judge_too_harsh`: you said correct (1), the judge said wrong (0).

    `list(zip(human, judge))` makes a list of pairs like `(1, 0)`, and
    `.count(pair)` counts how many times each pair appears.

    Example:
        >>> confusion([1, 1, 0, 0, 1], [1, 0, 1, 0, 1])
        {'both_1': 2, 'both_0': 1, 'judge_too_kind': 1, 'judge_too_harsh': 1}
    """
    pairs = list(zip(human, judge))
    return {"both_1": pairs.count((1, 1)), "both_0": pairs.count((0, 0)),
            "judge_too_kind": pairs.count((0, 1)), "judge_too_harsh": pairs.count((1, 0))}


def cohen_kappa(a, b):
    """Agreement corrected for chance: how much better than luck the two graders agree.

    - `p_o` (observed): the plain agreement from `agreement`.
    - `p_e` (expected by chance): if both graders handed out 1s at random with
      their usual rates `pa` and `pb`, they'd agree on a 1 with probability
      `pa * pb` and on a 0 with `(1 - pa) * (1 - pb)`.
    - `kappa = (p_o - p_e) / (1 - p_e)`: the share of the *possible* improvement
      over luck that they actually achieved. 1 = perfect, 0 = no better than luck,
      below 0 = worse than luck.

    If both always give the same single label, `p_e` is 1 and the formula would
    divide by zero. Here they agree perfectly, so the function returns 1.0.

    Example (two doctors who agree 80% of the time but never on a fracture):
        >>> a = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
        >>> b = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
        >>> agreement(a, b)
        0.8
        >>> round(cohen_kappa(a, b), 2)
        -0.11
        >>> cohen_kappa([1, 0, 1, 0], [1, 0, 1, 0])
        1.0
    """
    p_o = agreement(a, b)
    pa, pb = sum(a) / len(a), sum(b) / len(b)
    p_e = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if p_e == 1 else (p_o - p_e) / (1 - p_e)


def verdict(kappa):
    """Turn kappa into a decision, with the usual rules of thumb.

    - 0.8 or more: **trust** the judge.
    - 0.6 to 0.8: use it, but **spot-check** some grades yourself.
    - below 0.6: **fix the judge prompt** (clearer rubric, a few graded examples)
      before believing its numbers.

    Example:
        >>> verdict(0.85), verdict(0.7), verdict(0.3)
        ('trust', 'spot-check', 'fix the judge prompt')
    """
    return "trust" if kappa >= 0.8 else "spot-check" if kappa >= 0.6 else "fix the judge prompt"


if __name__ == "__main__":
    print("agreement", round(agreement(MY_LABELS, JUDGE_LABELS), 2))
    print("confusion", confusion(MY_LABELS, JUDGE_LABELS))
    k = cohen_kappa(MY_LABELS, JUDGE_LABELS)
    print("kappa", round(k, 2), "->", verdict(k))
