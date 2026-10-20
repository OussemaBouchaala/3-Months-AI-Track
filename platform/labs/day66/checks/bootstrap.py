import random
bc = fn("bootstrap_ci")
v = [1] * 39 + [0] * 11
check("bootstrap_ci returns (mean, lo, hi) around the mean", lambda: (lambda r: approx(r[0], 0.78) and r[1] < 0.78 < r[2] and 0.6 < r[1] and r[2] < 0.92)(bc(v)))
check("bootstrap_ci is reproducible with a seed", lambda: bc(v, seed=3) == bc(v, seed=3) and bc(v, 500, 0.05, 1) != bc(v, 500, 0.05, 2))
check("a constant list has a zero-width interval", lambda: bc([1] * 20)[1:] == (1, 1))
check("follows the percentile rule exactly", lambda: (lambda rng: bc(v, 200, 0.1, 7)[1] == sorted(sum(rng.choices(v, k=50)) / 50 for _ in range(200))[10])(random.Random(7)))
pb = fn("paired_bootstrap_diff")
a = [1] * 40 + [0] * 10
b = [1] * 30 + [0] * 20
check("paired diff: observed difference and interval", lambda: (lambda r: approx(r[0], 0.2) and 0.05 < r[1] < 0.2 < r[2] < 0.35)(pb(a, b)))
def _err():
    try:
        pb([1, 0], [1])
    except ValueError:
        return True
    return False
check("different lengths raise ValueError", _err)
sg = fn("significant")
check("significant when 0 is outside the interval", lambda: sg(0.02, 0.1) and sg(-0.2, -0.01) and not sg(-0.03, 0.08))
fc = fn("format_ci")
check("format_ci", lambda: fc(0.78, 0.6612, 0.88) == "0.78 [0.66, 0.88]" and fc(0.5, 0.4, 0.6, 1) == "0.5 [0.4, 0.6]")
qn = fn("questions_needed")
check("questions_needed: about 246 for +/-5 points at 80%", lambda: qn(0.8, 0.05) == 246 and qn(0.5, 0.1) == 97)
