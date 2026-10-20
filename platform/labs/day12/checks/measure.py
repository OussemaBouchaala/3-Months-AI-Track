import statistics

lat = [0.8, 0.9, 1.1, 0.7, 4.2, 0.9, 1.0, 0.8, 0.9, 5.1]
q = statistics.quantiles(lat, n=100, method="inclusive")
check("p50_p95 returns the 50th and 95th percentiles", lambda: approx(fn("p50_p95")(lat)[0], q[49]) and approx(fn("p50_p95")(lat)[1], q[94]))
check("p95 shows the slow tail (> 4 s here)", lambda: fn("p50_p95")(lat)[1] > 4)

label = {"price_tnd": 1, "surface_m2": 2, "rooms": 3, "city": "Sousse"}
check("field_accuracy", lambda: fn("field_accuracy")({"price_tnd": 1, "rooms": 3}, label) == 0.5)
check("cost_per_1k: 500 in / 200 out at $3/$15 -> $4.50", lambda: approx(fn("cost_per_1k")(500, 200, 3, 15), 4.5))

rows = [{"model": "api", "accuracy": 0.9, "p50": 0.8, "p95": 2.1, "cost_1k": "$1.20"},
        {"model": "local", "accuracy": 0.75, "p50": 1.9, "p95": 4.4, "cost_1k": "local hardware"}]


def table_lines():
    return [l for l in fn("results_table")(rows).strip().splitlines() if l.strip()]


check("results_table returns header + separator + one line per model", lambda: len(table_lines()) == 4)
check("each row shows model, accuracy, p50, p95 and cost",
      lambda: all(s in table_lines()[2] for s in ("api", "0.90", "0.80", "2.10", "$1.20")))
