# Can you trust the judge? Grade 20 answers yourself, then measure how often the judge agrees.
# Fill MY_LABELS and JUDGE_LABELS (1 = correct, 0 = wrong) for the same 20 answers, in the same order.
from collections import Counter

MY_LABELS = []      # TODO: your 20 grades, e.g. [1, 0, 1, ...]
JUDGE_LABELS = []   # TODO: the judge's 20 grades for the same answers


def agreement(a, b):
    """Share of positions where a and b are equal."""
    # TODO
    ...


def confusion(human, judge):
    """Counts of the 4 cases as a dict:
    {"both_1": ..., "both_0": ..., "judge_too_kind": (human 0, judge 1), "judge_too_harsh": (human 1, judge 0)}"""
    # TODO
    ...


def cohen_kappa(a, b):
    """Agreement corrected for chance, for 0/1 labels:
        p_o = agreement(a, b)
        p_e = P(a=1) * P(b=1) + P(a=0) * P(b=0)
        kappa = (p_o - p_e) / (1 - p_e)       if p_e == 1: return 1.0
    """
    # TODO
    ...


def verdict(kappa):
    """"trust" if kappa >= 0.8, "spot-check" if kappa >= 0.6, else "fix the judge prompt"."""
    # TODO
    ...


if __name__ == "__main__":
    print("agreement", round(agreement(MY_LABELS, JUDGE_LABELS), 2))
    print("confusion", confusion(MY_LABELS, JUDGE_LABELS))
    k = cohen_kappa(MY_LABELS, JUDGE_LABELS)
    print("kappa", round(k, 2), "->", verdict(k))
