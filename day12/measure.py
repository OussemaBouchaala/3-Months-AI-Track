# One table: accuracy, latency and cost for the API model vs the local model.
# Start your service first (day11: uvicorn service:app --port 8002). Check only tests the helpers.
import json
import statistics
import time

import httpx

URL = "http://127.0.0.1:8002/extract"
FIELDS = ["price_tnd", "surface_m2", "rooms", "city"]
RUNS = 3


def p50_p95(latencies):
    """Return (p50, p95) using statistics.quantiles(latencies, n=100, method="inclusive"): items 49 and 94."""
    # TODO
    q = statistics.quantiles(latencies, n=100, method="inclusive")
    return q[49], q[94]

def field_accuracy(pred, label):
    """Fraction of FIELDS where pred.get(field) == label[field]."""
    # TODO
    correct = sum(1 for f in FIELDS if pred.get(f) == label.get(f))
    return correct / len(FIELDS)


def cost_per_1k(tokens_in, tokens_out, price_in_per_m, price_out_per_m):
    """Dollar cost of 1,000 requests with these AVERAGE token counts per request."""
    # TODO
    cost_in = (tokens_in * price_in_per_m)
    cost_out = (tokens_out * price_out_per_m)
    return (cost_in + cost_out) / 1000  # "per million" prices → divide by 1_000_000, then ×1000 requests = divide by 1000


def results_table(rows):
    """rows: list of dicts with keys model, accuracy, p50, p95, cost_1k (cost_1k may be a string like "local GPU").
    Return a Markdown table, header first:
    | model | field accuracy | p50 latency (s) | p95 latency (s) | cost per 1k requests |"""
    header = "| model | field accuracy | p50 latency (s) | p95 latency (s) | cost per 1k requests |\n|---|---|---|---|---|\n"
    # TODO: one line per row, e.g. f"| {r['model']} | {r['accuracy']:.2f} | {r['p50']:.2f} | {r['p95']:.2f} | {r['cost_1k']} |"
    header = "| model | field accuracy | p50 latency (s) | p95 latency (s) | cost per 1k requests |\n|---|---|---|---|---|\n"
    lines = [header]
    for r in rows:
        lines.append(f"| {r['model']} | {r['accuracy']:.2f} | {r['p50']:.2f} | {r['p95']:.2f} | {r['cost_1k']} |")
    return "\n".join(lines)


if __name__ == "__main__":
    listings = json.load(open("../day09/listings.json", encoding="utf-8"))
    rows = []
    for model in ("api", "local"):
        latencies, accuracies = [], []
        for item in listings:
            for _ in range(RUNS):
                start = time.perf_counter()
                pred = httpx.post(URL, json={"text": item["text"], "model": model}, timeout=120).json()
                latencies.append(time.perf_counter() - start)
                accuracies.append(field_accuracy(pred, item["label"]))
        p50, p95 = p50_p95(latencies)
        cost = "local hardware" if model == "local" else f"${cost_per_1k(600, 120, 1.0, 5.0):.2f}"  # TODO: your measured tokens and prices
        rows.append({"model": model, "accuracy": statistics.mean(accuracies), "p50": p50, "p95": p95, "cost_1k": cost})

    table = results_table(rows)
    print(table)
    open("results.md", "w", encoding="utf-8").write(table)
