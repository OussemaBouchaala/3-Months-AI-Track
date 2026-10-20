pc = fn("percentile")
vals = [5, 1, 4, 2, 3, 10, 9, 8, 7, 6]
check("percentile uses nearest rank", lambda: pc(vals, 50) == 5 and pc(vals, 95) == 10 and pc(vals, 90) == 9 and pc(vals, 10) == 1)
check("percentile of [] is None", lambda: pc([], 95) is None)
cq = fn("cost_per_query")
check("cost_per_query: price per million tokens", lambda: approx(cq(2000, 200, 3.0, 15.0), 0.009))
sm = fn("summarize")
runs = [{"correct": True, "cited": True, "latency_s": 2.0, "in_tokens": 1000, "out_tokens": 100},
        {"correct": False, "cited": True, "latency_s": 4.0, "in_tokens": 3000, "out_tokens": 300}]
m = lambda: sm(runs, 1.0, 10.0)
check("summarize: rates", lambda: approx(m()["answer_correct"], 0.5) and approx(m()["citation_ok"], 1.0))
check("summarize: latency percentiles and mean cost", lambda: m()["p50_latency_s"] == 2.0 and m()["p95_latency_s"] == 4.0 and approx(m()["cost_per_query_usd"], 0.004))
ct = fn("check_targets")
T = {"acc": (">=", 0.8), "lat": ("<=", 5.0), "cost": ("<=", 0.01)}
r = lambda: ct({"acc": 0.8, "lat": 6.0}, T)
check("check_targets: >= and <= including equality", lambda: r()["acc"]["ok"] is True and r()["lat"]["ok"] is False)
check("missing metric -> value None, not ok", lambda: r()["cost"]["value"] is None and r()["cost"]["ok"] is False)
rp = fn("report")
check("report: one line per target with OK / MISS", lambda: (lambda lines: len(lines) == 3 and lines[0].startswith("OK") and lines[1].startswith("MISS") and "missing" in lines[2])(rp(r()).strip().splitlines()))
check("your TARGETS have at least 4 entries with valid operators", lambda: len(var("TARGETS")) >= 4 and all(op in (">=", "<=") for op, _ in var("TARGETS").values()))
