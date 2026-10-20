ag = fn("aggregate")
rows = [{"correct": 1, "citation_ok": 1, "latency_s": float(i), "cost_usd": 0.002} for i in range(1, 20)] + [{"correct": 0, "citation_ok": 0, "latency_s": 30.0, "cost_usd": 0.004}]
check("aggregate: means, p95 nearest rank, mean cost", lambda: (lambda m: m["n"] == 20 and approx(m["correct"], 0.95) and m["p95_latency_s"] == 19.0 and approx(m["cost_usd"], 0.0021))(ag(rows)))
mt = fn("missed_targets")
T = {"correct": (">=", 0.8), "citation_ok": (">=", 0.9), "p95_latency_s": ("<=", 10.0), "cost_usd": ("<=", 0.005)}
check("missed_targets in order", lambda: mt({"correct": 0.7, "citation_ok": 0.95, "p95_latency_s": 12, "cost_usd": 0.001}, T) == ["correct", "p95_latency_s"] and mt({"correct": 0.8, "citation_ok": 0.9, "p95_latency_s": 10, "cost_usd": 0.005}, T) == [])
ch = fn("choose")
C = {"api-large": {"correct": 0.88, "citation_ok": 0.95, "p95_latency_s": 6.0, "cost_usd": 0.012},
     "api-small+rerank": {"correct": 0.84, "citation_ok": 0.93, "p95_latency_s": 7.5, "cost_usd": 0.004},
     "local+rerank": {"correct": 0.84, "citation_ok": 0.92, "p95_latency_s": 9.0, "cost_usd": 0.001},
     "local": {"correct": 0.76, "citation_ok": 0.91, "p95_latency_s": 5.0, "cost_usd": 0.001}}
check("choose: best accuracy among configs that meet cost/latency/citations", lambda: ch(C, T) == "local+rerank")
check("choose: accuracy target itself is not a hard filter", lambda: ch({"a": dict(C["local"])}, T) == "a")
check("choose: None when nothing meets the hard targets", lambda: ch({"x": C["api-large"]}, T) is None)
rt = fn("results_table")
pq = {"local+rerank": rows, "local": rows[:10]}
cf = {"local+rerank": ag(rows), "local": ag(rows[:10])}
tbl = lambda: rt(cf, pq, lambda v: f"CI{len(v)}", T).splitlines()
check("results_table: header, separator, one row per config", lambda: len(tbl()) == 4 and tbl()[0].startswith("| config | n | correct"))
check("results_table row: CI strings, p95, cost, misses", lambda: tbl()[2] == "| local+rerank | 20 | CI20 | CI20 | 19.0 | 0.0021 | p95_latency_s |" and tbl()[3].endswith("| none |"))
