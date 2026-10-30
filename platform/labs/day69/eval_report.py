"""The final run: the best configs on the golden **test** set (opened once, at the end).

Metrics with confidence intervals, and a recommendation that respects the Week 7 targets,
not just the highest accuracy. A config that is 2 points more accurate but costs 3x the
budget is not the recommendation.

1. `TARGETS`: the success targets from day 46.
2. `aggregate`: per-question rows -> one config's metrics.
3. `missed_targets`: which targets a config misses.
4. `choose`: the recommendation, under hard constraints.
5. `results_table`: the Markdown table for `results.md` (day 70).
"""
import math

TARGETS = {"correct": (">=", 0.80), "citation_ok": (">=", 0.90), "p95_latency_s": ("<=", 10.0), "cost_usd": ("<=", 0.005)}


def aggregate(rows):
    """One config's metrics from its per-question rows.

    Means for `correct`, `citation_ok` and `cost_usd`; the p95 latency by
    nearest rank (day 46): sort, take the value at rank `ceil(0.95 x n)`.

    Example (19 fast correct answers and one slow wrong one):
        >>> rows = [{"correct": 1, "citation_ok": 1, "latency_s": float(i), "cost_usd": 0.002} for i in range(1, 20)]
        >>> rows.append({"correct": 0, "citation_ok": 0, "latency_s": 30.0, "cost_usd": 0.004})
        >>> m = aggregate(rows)
        >>> m["n"], m["correct"], m["p95_latency_s"], round(m["cost_usd"], 4)
        (20, 0.95, 19.0, 0.0021)
    """
    n = len(rows)
    lat = sorted(r["latency_s"] for r in rows)
    return {"n": n, "correct": sum(r["correct"] for r in rows) / n, "citation_ok": sum(r["citation_ok"] for r in rows) / n,
            "p95_latency_s": lat[max(1, math.ceil(0.95 * n)) - 1], "cost_usd": sum(r["cost_usd"] for r in rows) / n}


def missed_targets(metrics, targets):
    """The names of the targets a config misses, in the targets' order.

    Example:
        >>> missed_targets({"correct": 0.7, "citation_ok": 0.95, "p95_latency_s": 12, "cost_usd": 0.001}, TARGETS)
        ['correct', 'p95_latency_s']
    """
    return [k for k, (op, t) in targets.items() if not (metrics[k] >= t if op == ">=" else metrics[k] <= t)]


def choose(configs, targets, primary="correct"):
    """The recommended config.

    1. **Hard constraints** = every target except the primary one (latency,
       cost, citations): a config that misses one is out. The agency can't
       pay more or wait longer, whatever the accuracy.
    2. Among the rest: the highest accuracy; on a tie, the cheaper; then by
       name, so the choice is always the same.
    3. Nothing qualifies: `None` (say so in the report, don't force a pick).

    `min` with the key `(-accuracy, cost, name)` does all three at once.

    Example:
        >>> C = {"api-large": {"correct": 0.88, "citation_ok": 0.95, "p95_latency_s": 6.0, "cost_usd": 0.012},
        ...      "local+rerank": {"correct": 0.84, "citation_ok": 0.92, "p95_latency_s": 9.0, "cost_usd": 0.001},
        ...      "local": {"correct": 0.76, "citation_ok": 0.91, "p95_latency_s": 5.0, "cost_usd": 0.001}}
        >>> choose(C, TARGETS)
        'local+rerank'
        >>> print(choose({"x": C["api-large"]}, TARGETS))
        None
    """
    hard = {k: v for k, v in targets.items() if k != primary}
    ok = [(name, m) for name, m in configs.items() if not missed_targets(m, hard)]
    if not ok:
        return None
    return min(ok, key=lambda nm: (-nm[1][primary], nm[1]["cost_usd"], nm[0]))[0]


def results_table(configs, per_question, ci_fn, targets):
    """The results table, one row per config.

    `correct` and `citations` come with their bootstrap interval, computed
    by `ci_fn` from the 0/1 values (day 66), so a reader sees which
    differences are real. The last column lists the missed targets.

    Example (a fake ci_fn that just shows how many values it got):
        >>> rows = [{"correct": 1, "citation_ok": 1, "latency_s": 4.0, "cost_usd": 0.001}] * 4
        >>> print(results_table({"local": aggregate(rows)}, {"local": rows}, lambda v: f"CI({len(v)})", TARGETS))
        | config | n | correct | citations | p95 s | USD / query | misses |
        |---|---|---|---|---|---|---|
        | local | 4 | CI(4) | CI(4) | 4.0 | 0.0010 | none |
    """
    lines = ["| config | n | correct | citations | p95 s | USD / query | misses |", "|---|---|---|---|---|---|---|"]
    for name, m in configs.items():
        rows = per_question[name]
        lines.append(f"| {name} | {m['n']} | {ci_fn([r['correct'] for r in rows])} | {ci_fn([r['citation_ok'] for r in rows])} | "
                     f"{m['p95_latency_s']:.1f} | {m['cost_usd']:.4f} | {', '.join(missed_targets(m, targets)) or 'none'} |")
    return "\n".join(lines)


def make_ci():
    """The `ci_fn` for the table: day 66's bootstrap, formatted
    "0.78 [0.66, 0.88]". If day 66 isn't available, a plain mean.

    Example:
        >>> make_ci()([1] * 39 + [0] * 11)
        '0.78 [0.66, 0.88]'
    """
    import sys
    sys.path.append("../day66")
    try:
        from bootstrap import bootstrap_ci, format_ci
        ci = lambda values: format_ci(*bootstrap_ci(values))
        ci([1, 0])
        return ci
    except Exception:
        return lambda values: f"{sum(values) / len(values):.2f}"


if __name__ == "__main__":
    import json
    import random
    from pathlib import Path
    if Path("test_runs.json").exists():
        per_question = json.load(open("test_runs.json", encoding="utf-8"))      # {config name: [per-question rows]}
    else:
        # Demo: 60 test questions, four configs with different accuracy, speed and price.
        rng = random.Random(11)
        specs = {"local": (0.76, 5, 0.0005), "local+rerank": (0.85, 8, 0.0006),
                 "api-small+rerank": (0.86, 6, 0.004), "api-large": (0.90, 5, 0.012)}
        per_question = {name: [{"correct": int(rng.random() < acc), "citation_ok": int(rng.random() < 0.94),
                                "latency_s": rng.uniform(0.4, 1.2) * lat, "cost_usd": cost * rng.uniform(0.8, 1.2)}
                               for _ in range(60)] for name, (acc, lat, cost) in specs.items()}
    configs = {name: aggregate(rows) for name, rows in per_question.items()}
    table = results_table(configs, per_question, make_ci(), TARGETS)
    pick = choose(configs, TARGETS)
    print(table)
    print("\nrecommended:", pick)
    if Path("test_runs.json").exists():
        Path("results_table.md").write_text(table + f"\n\nRecommended: {pick}\n", encoding="utf-8")
