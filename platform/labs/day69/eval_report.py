# The final run: the best configs on the golden TEST set (opened once), metrics with intervals,
# and a recommendation that respects the targets from Week 7, not just the highest accuracy.
import math

TARGETS = {"correct": (">=", 0.80), "citation_ok": (">=", 0.90), "p95_latency_s": ("<=", 10.0), "cost_usd": ("<=", 0.005)}


def aggregate(rows):
    """rows: per-question dicts {"correct": 0/1, "citation_ok": 0/1, "latency_s", "cost_usd"}.
    -> {"n", "correct" (mean), "citation_ok" (mean), "p95_latency_s" (nearest rank), "cost_usd" (mean)}."""
    # TODO
    ...


def missed_targets(metrics, targets):
    """Names of the targets this config misses, in the targets' order."""
    # TODO
    ...


def choose(configs, targets, primary="correct"):
    """configs: {name: metrics}. Keep configs that meet every target EXCEPT primary (the hard constraints: latency, cost,
    citations). Among them, the highest primary; tie -> lower cost_usd; tie -> name. None if nothing qualifies."""
    # TODO
    ...


def results_table(configs, per_question, ci_fn, targets):
    """Markdown, configs in the given order:
    | config | n | correct | citations | p95 s | USD / query | misses |
    correct and citations as ci_fn(list of 0/1 values) -> "0.78 [0.66, 0.88]"; p95 with 1 decimal; cost with 4 decimals;
    misses = ", ".join(missed_targets) or "none"."""
    # TODO
    ...


if __name__ == "__main__":
    import json
    import sys
    sys.path += ["../day66"]
    from bootstrap import bootstrap_ci, format_ci

    ci = lambda values: format_ci(*bootstrap_ci(values))
    per_question = json.load(open("test_runs.json", encoding="utf-8"))      # {config name: [per-question rows]}
    configs = {name: aggregate(rows) for name, rows in per_question.items()}
    table = results_table(configs, per_question, ci, TARGETS)
    pick = choose(configs, TARGETS)
    open("results_table.md", "w", encoding="utf-8").write(table + f"\n\nRecommended: {pick}\n")
    print(table)
    print("recommended:", pick)
