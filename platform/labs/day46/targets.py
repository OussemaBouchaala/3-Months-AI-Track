"""Turn "good enough" into numbers, agreed **before** building.

After the user interview, write down what success means: "the right answer 8 times out
of 10", "an answer in 10 seconds", "30 TND a month". Then every eval run tells you,
target by target, where you stand.

1. `TARGETS`: each metric with its operator and threshold.
2. `percentile`: p50 / p95 latency (nearest-rank method).
3. `cost_per_query`: dollars for one query.
4. `summarize`: eval runs into metrics.
5. `check_targets` and `report`: OK or MISS for every target.
"""
import math

TARGETS = {                                  # from the user interview
    "answer_correct": (">=", 0.80),          # share of answers judged correct
    "citation_ok": (">=", 0.90),             # share of answers citing the right document
    "p95_latency_s": ("<=", 10.0),           # "the answer in 10 seconds"
    "cost_per_query_usd": ("<=", 0.005),     # 30 TND a month for about 2,000 questions
}


def percentile(values, p):
    """The nearest-rank percentile: sort, then take the value at rank `ceil(p/100 * n)`.

    It always returns one of the real values (no interpolation), which is
    easy to explain: "95% of queries took at most this long".

    Example:
        >>> values = [5, 1, 4, 2, 3, 10, 9, 8, 7, 6]
        >>> percentile(values, 50), percentile(values, 90), percentile(values, 95)
        (5, 9, 10)
        >>> print(percentile([], 95))
        None
    """
    if not values:
        return None
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1]


def cost_per_query(in_tokens, out_tokens, price_in_per_m, price_out_per_m):
    """Dollars for one query, with prices per million tokens.

    Example (2,000 tokens in at $3/M, 200 out at $15/M):
        >>> round(cost_per_query(2000, 200, 3.0, 15.0), 6)
        0.009
    """
    return (in_tokens * price_in_per_m + out_tokens * price_out_per_m) / 1_000_000


def summarize(runs, price_in_per_m, price_out_per_m):
    """Turn the eval runs into the metrics the targets talk about.

    `sum(r["correct"] for r in runs)` counts the `True` values, so dividing by
    `n` gives a share. Cost is the **mean** over all queries.

    Example:
        >>> runs = [{"correct": True, "cited": True, "latency_s": 2.0, "in_tokens": 1000, "out_tokens": 100},
        ...         {"correct": False, "cited": True, "latency_s": 4.0, "in_tokens": 3000, "out_tokens": 300}]
        >>> summarize(runs, 1.0, 10.0)
        {'answer_correct': 0.5, 'citation_ok': 1.0, 'p50_latency_s': 2.0, 'p95_latency_s': 4.0, 'cost_per_query_usd': 0.004}
    """
    n = len(runs)
    lat = [r["latency_s"] for r in runs]
    return {
        "answer_correct": sum(r["correct"] for r in runs) / n,
        "citation_ok": sum(r["cited"] for r in runs) / n,
        "p50_latency_s": percentile(lat, 50),
        "p95_latency_s": percentile(lat, 95),
        "cost_per_query_usd": sum(cost_per_query(r["in_tokens"], r["out_tokens"], price_in_per_m, price_out_per_m)
                                  for r in runs) / n,
    }


def check_targets(metrics, targets):
    """For every target: the value, the rule and whether it's met.

    A metric that wasn't measured counts as **not met**: you can't claim a
    target you didn't check.

    Example:
        >>> result = check_targets({"acc": 0.8, "lat": 6.0}, {"acc": (">=", 0.8), "lat": ("<=", 5.0), "cost": ("<=", 0.01)})
        >>> {name: r["ok"] for name, r in result.items()}
        {'acc': True, 'lat': False, 'cost': False}
    """
    out = {}
    for name, (op, t) in targets.items():
        v = metrics.get(name)
        ok = v is not None and (v >= t if op == ">=" else v <= t)
        out[name] = {"value": v, "op": op, "target": t, "ok": ok}
    return out


def report(results):
    """One readable line per target: OK or MISS, the value and the rule.

    `{:.4g}` prints at most 4 significant digits: 0.82, 6.5, 0.003456.

    Example:
        >>> print(report(check_targets({"acc": 0.8213, "lat": 6.0}, {"acc": (">=", 0.8), "lat": ("<=", 5.0), "cost": ("<=", 0.01)})))
        OK   acc = 0.8213 (>= 0.8)
        MISS lat = 6 (<= 5.0)
        MISS cost = missing (<= 0.01)
    """
    lines = []
    for name, r in results.items():
        v = "missing" if r["value"] is None else f"{r['value']:.4g}"
        lines.append(f"{'OK  ' if r['ok'] else 'MISS'} {name} = {v} ({r['op']} {r['target']})")
    return "\n".join(lines)


if __name__ == "__main__":
    import random
    rng = random.Random(0)
    # 50 simulated eval runs.
    runs = [{"correct": rng.random() < 0.83, "cited": rng.random() < 0.9, "latency_s": rng.uniform(2, 12),
             "in_tokens": rng.randint(1500, 3000), "out_tokens": rng.randint(100, 300)} for _ in range(50)]
    m = summarize(runs, price_in_per_m=0.8, price_out_per_m=4.0)
    print(report(check_targets(m, TARGETS)))
