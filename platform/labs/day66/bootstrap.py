"""0.78 vs 0.74 correct on 50 questions: a real difference, or luck?

The **bootstrap** answers with only the data you have: pretend your 50 questions are the
whole world, draw new sets of 50 from them (with replacement) thousands of times, and
recompute the metric each time. The spread of those results is your uncertainty.

1. `mean`: the average.
2. `bootstrap_ci`: a 95% confidence interval for one config's score.
3. `paired_bootstrap_diff`: an interval for the difference between two configs.
4. `significant` and `format_ci`: read and print the result.
5. `questions_needed`: how many test questions you need for a given precision.
"""
import random


def mean(values):
    """The average of a list.

    Example:
        >>> mean([1, 1, 0, 1])
        0.75
    """
    return sum(values) / len(values)


def bootstrap_ci(values, n_boot=2000, alpha=0.05, seed=0):
    """The mean and its percentile confidence interval: `(mean, lo, hi)`.

    1. `n_boot` times: draw `len(values)` values **with replacement**
       (`rng.choices`; some questions appear twice, some not at all) and
       take the mean.
    2. Sort the 2000 means. With `alpha=0.05`, the interval goes from the
       2.5% one to the 97.5% one: the middle 95%.

    The `seed` makes it reproducible: same data, same interval.

    Example (39 right out of 50):
        >>> m, lo, hi = bootstrap_ci([1] * 39 + [0] * 11)
        >>> m, lo, hi
        (0.78, 0.66, 0.88)
        >>> bootstrap_ci([1] * 20)
        (1.0, 1.0, 1.0)
    """
    rng = random.Random(seed)
    n = len(values)
    means = sorted(mean(rng.choices(values, k=n)) for _ in range(n_boot))
    return mean(values), means[int(alpha / 2 * n_boot)], means[int((1 - alpha / 2) * n_boot) - 1]


def paired_bootstrap_diff(a, b, n_boot=2000, alpha=0.05, seed=0):
    """The interval for `mean(a) - mean(b)`, where `a[i]` and `b[i]` are two
    configs' scores on the **same** question `i`.

    Resample question **indexes**, and use both configs' scores for those
    questions. Pairing removes the noise of "some questions are just hard",
    so it detects much smaller differences than two separate intervals.

    Example:
        >>> d, lo, hi = paired_bootstrap_diff([1] * 40 + [0] * 10, [1] * 30 + [0] * 20)
        >>> round(d, 2), round(lo, 2), round(hi, 2)
        (0.2, 0.1, 0.32)
    """
    if len(a) != len(b):
        raise ValueError("paired scores need the same questions")
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(n_boot):
        idx = rng.choices(range(n), k=n)
        diffs.append(sum(a[i] - b[i] for i in idx) / n)
    diffs.sort()
    return mean(a) - mean(b), diffs[int(alpha / 2 * n_boot)], diffs[int((1 - alpha / 2) * n_boot) - 1]


def significant(lo, hi):
    """True when the interval of a difference doesn't contain 0: the data
    says one config is really better (at this confidence level).

    Example:
        >>> significant(0.02, 0.1), significant(-0.2, -0.01), significant(-0.03, 0.08)
        (True, True, False)
    """
    return lo > 0 or hi < 0


def format_ci(m, lo, hi, digits=2):
    """How to write a result in a report: the value, then the interval.

    `f"{m:.{digits}f}"` uses a nested format: the number of decimals is itself a variable.

    Example:
        >>> format_ci(0.78, 0.6612, 0.88)
        '0.78 [0.66, 0.88]'
    """
    return f"{m:.{digits}f} [{lo:.{digits}f}, {hi:.{digits}f}]"


def questions_needed(p, half_width):
    """Roughly how many test questions give a 95% interval of +/- `half_width`
    around a proportion `p`: `1.96² x p(1-p) / half_width²`, rounded up.

    The lesson: +/-5 points needs about 250 questions. With 50 questions,
    differences under ~10 points are mostly noise.

    Example:
        >>> questions_needed(0.8, 0.05), questions_needed(0.8, 0.1)
        (246, 62)
    """
    import math
    return math.ceil(1.96 ** 2 * p * (1 - p) / half_width ** 2)


if __name__ == "__main__":
    rng = random.Random(1)
    a = [1 if rng.random() < 0.78 else 0 for _ in range(50)]
    b = [x if rng.random() < 0.85 else 1 - x for x in a]          # config B agrees with A on most questions
    print("A:", format_ci(*bootstrap_ci(a)))
    print("B:", format_ci(*bootstrap_ci(b)))
    d, lo, hi = paired_bootstrap_diff(a, b)
    print("A - B:", format_ci(d, lo, hi), "significant" if significant(lo, hi) else "not significant")
    print("questions for +/-5 points at 80%:", questions_needed(0.8, 0.05))
