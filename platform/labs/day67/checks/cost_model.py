qc = fn("query_cost")
P = {"in": 3.0, "out": 15.0, "cached_in": 0.3}
check("query_cost without cache", lambda: approx(qc(P, 2000, 200), 0.009))
check("query_cost with half the input cached", lambda: approx(qc(P, 2000, 200, cache_hit=0.5), (1000 * 3.0 + 1000 * 0.3 + 200 * 15.0) / 1e6))
lm = fn("local_monthly")
check("local_monthly: electricity + amortized hardware", lambda: approx(lm(200, 10, 0.1, 720, 36), 0.2 * 10 * 30 * 0.1 + 20) and approx(lm(100, 24, 0.2), 14.4))
gn = fn("gpus_needed")
check("gpus_needed at peak", lambda: gn(6, 8) == 1 and gn(30, 8) == 4 and gn(30, 8, concurrency_per_gpu=4) == 1 and gn(0, 8) == 1)
be = fn("break_even")
check("break_even: queries where local becomes cheaper", lambda: be(26.0, 0.004) == 6500 and be(10, 0) is None)
ct = fn("cost_table")
rows = [{"name": "api", "monthly_usd": 12.5}, {"name": "local", "monthly_usd": 7.4}]
check("cost_table: cheapest first, USD and TND", lambda: ct(rows).splitlines()[2:] == ["| local | 7.40 | 22.94 |", "| api | 12.50 | 38.75 |"] if var("USD_TO_TND") == 3.1 else "| local |" in ct(rows).splitlines()[2])
