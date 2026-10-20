# "Good enough" must be a number agreed BEFORE building. Turn your interview into targets,
# then write the function that tells you, after every eval run, which targets you meet.
import math

TARGETS = {                                  # edit with what YOUR user said
    "answer_correct": (">=", 0.80),          # share of answers judged correct
    "citation_ok": (">=", 0.90),             # share of answers citing the right document
    "p95_latency_s": ("<=", 10.0),           # "the answer in 10 seconds"
    "cost_per_query_usd": ("<=", 0.005),     # 30 TND a month for about 2,000 questions
}


def percentile(values, p):
    """Nearest-rank percentile: sort, take the value at rank ceil(p/100 * n) (1-based). p in (0, 100].
    Empty list -> None."""
    # TODO
    ...


def cost_per_query(in_tokens, out_tokens, price_in_per_m, price_out_per_m):
    """Prices are in USD per million tokens."""
    # TODO
    ...


def summarize(runs, price_in_per_m, price_out_per_m):
    """runs: [{"correct": bool, "cited": bool, "latency_s": float, "in_tokens": int, "out_tokens": int}, ...]
    -> {"answer_correct", "citation_ok", "p50_latency_s", "p95_latency_s", "cost_per_query_usd"} (mean cost)."""
    # TODO
    ...


def check_targets(metrics, targets):
    """{name: {"value": v, "op": op, "target": t, "ok": bool}} for every target.
    A metric missing from metrics -> value None and ok False."""
    # TODO
    ...


def report(results):
    """One line per target, in the targets' order: "OK   answer_correct = 0.82 (>= 0.8)" or "MISS ...".
    Values with up to 4 significant digits ({:.4g}); a missing value prints as "missing"."""
    # TODO
    ...


if __name__ == "__main__":
    import random
    rng = random.Random(0)
    runs = [{"correct": rng.random() < 0.83, "cited": rng.random() < 0.9, "latency_s": rng.uniform(2, 12),
             "in_tokens": rng.randint(1500, 3000), "out_tokens": rng.randint(100, 300)} for _ in range(50)]
    m = summarize(runs, price_in_per_m=0.8, price_out_per_m=4.0)
    print(report(check_targets(m, TARGETS)))
