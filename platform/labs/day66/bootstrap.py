# 0.78 vs 0.74 correct on 50 questions: a real difference or luck? The bootstrap answers with the data you have:
# resample the questions many times, recompute the metric, and look at the spread.
import random


def mean(values):
    return sum(values) / len(values)


def bootstrap_ci(values, n_boot=2000, alpha=0.05, seed=0):
    """Percentile CI of the mean. rng = random.Random(seed); n_boot times: resample len(values) values WITH replacement
    (rng.choices), take the mean. Sort the means; lo = means[int(alpha/2 * n_boot)], hi = means[int((1 - alpha/2) * n_boot) - 1].
    Return (mean(values), lo, hi)."""
    # TODO
    ...


def paired_bootstrap_diff(a, b, n_boot=2000, alpha=0.05, seed=0):
    """a[i] and b[i] are two configs' scores on the SAME question i. Resample question INDEXES with replacement
    (rng.choices(range(n), k=n)), compute mean(a) - mean(b) on those indexes. Same percentile rule.
    Return (observed diff, lo, hi). ValueError if lengths differ."""
    # TODO
    ...


def significant(lo, hi):
    """True when the interval does not contain 0."""
    # TODO
    ...


def format_ci(m, lo, hi, digits=2):
    """"0.78 [0.66, 0.88]" with the given number of decimals."""
    # TODO
    ...


def questions_needed(p, half_width):
    """Rough sample size so a proportion p has a 95% CI of +/- half_width: ceil(1.96**2 * p * (1 - p) / half_width**2)."""
    # TODO
    ...


if __name__ == "__main__":
    rng = random.Random(1)
    a = [1 if rng.random() < 0.78 else 0 for _ in range(50)]
    b = [x if rng.random() < 0.85 else 1 - x for x in a]          # config B agrees with A on most questions
    print("A:", format_ci(*bootstrap_ci(a)))
    print("B:", format_ci(*bootstrap_ci(b)))
    d, lo, hi = paired_bootstrap_diff(a, b)
    print("A - B:", format_ci(d, lo, hi), "significant" if significant(lo, hi) else "not significant")
    print("questions for +/-5 points at 80%:", questions_needed(0.8, 0.05))
