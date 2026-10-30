""""Local is free" and "the API is cheap" are both wrong at some volume.

Model both, find the **break-even** volume, and put a monthly number in front of the
agency manager. Prices change, so they live in one dict at the top.

1. `PRICES`: dollars per million tokens, per model.
2. `query_cost`: one question's price, with prompt caching.
3. `api_monthly` and `local_monthly`: a month of each option.
4. `gpus_needed`: how many machines the busiest minute needs.
5. `break_even`: the volume where local becomes cheaper.
6. `cost_table`: the table for the report, in USD and TND.
"""
import math

PRICES = {  # USD per million tokens; check the providers' pricing pages and update
    "small API model": {"in": 0.80, "out": 4.00, "cached_in": 0.08},
    "large API model": {"in": 3.00, "out": 15.00, "cached_in": 0.30},
}
USD_TO_TND = 3.1


def query_cost(price, in_tokens, out_tokens, cache_hit=0.0):
    """Dollars for one query.

    Input and output tokens have different prices (output is ~5x dearer).
    **Prompt caching**: the system prompt and instructions are identical on
    every call, so providers bill that cached share of the input at ~10%.
    `cache_hit` is that share (0.4 = 40% of input tokens cached).

    Example (2,000 tokens in, 200 out, the large model):
        >>> round(query_cost(PRICES["large API model"], 2000, 200), 6)
        0.009
        >>> round(query_cost(PRICES["large API model"], 2000, 200, cache_hit=0.5), 6)
        0.0063
    """
    cached = in_tokens * cache_hit
    return ((in_tokens - cached) * price["in"] + cached * price["cached_in"] + out_tokens * price["out"]) / 1_000_000


def api_monthly(queries_per_month, per_query):
    """An API month: you pay per query, nothing when idle.

    Example:
        >>> round(api_monthly(2000, 0.0063), 2)
        12.6
    """
    return queries_per_month * per_query


def local_monthly(watts, hours_per_day, price_kwh, hardware_cost=0.0, months_amortized=36, days=30):
    """A local month: electricity plus the machine's price spread over its life.

    `watts / 1000 x hours x days` is the energy in kWh; times the price per
    kWh. The hardware is "amortized": 900 USD over 36 months = 25 USD a month.
    It costs the same at 10 questions or 10,000.

    Example (a 200 W PC on 10 h/day at 0.10 USD/kWh, 720 USD of hardware):
        >>> round(local_monthly(200, 10, 0.1, 720, 36), 2)
        26.0
    """
    return watts / 1000 * hours_per_day * days * price_kwh + hardware_cost / months_amortized


def gpus_needed(peak_queries_per_minute, seconds_per_query, concurrency_per_gpu=1):
    """Machines needed at the busiest minute (at least 1).

    6 questions a minute x 8 seconds each = 48 busy seconds per minute: one
    GPU copes. 30 a minute = 240 seconds of work per minute: 4 GPUs, or one
    that serves 4 queries at once. The API scales by itself; local doesn't.

    Example:
        >>> gpus_needed(6, 8), gpus_needed(30, 8), gpus_needed(30, 8, concurrency_per_gpu=4)
        (1, 4, 1)
    """
    return max(1, math.ceil(peak_queries_per_minute * seconds_per_query / 60 / concurrency_per_gpu))


def break_even(local_month, per_query):
    """The queries per month above which local is cheaper than the API.

    Example:
        >>> break_even(26.0, 0.004)
        6500
        >>> print(break_even(10, 0))
        None
    """
    return math.ceil(local_month / per_query) if per_query else None


def cost_table(scenarios):
    """A Markdown table, cheapest first, in dollars and dinars.

    Example:
        >>> print(cost_table([{"name": "api", "monthly_usd": 12.5}, {"name": "local", "monthly_usd": 7.4}]))
        | option | USD / month | TND / month |
        |---|---|---|
        | local | 7.40 | 22.94 |
        | api | 12.50 | 38.75 |
    """
    lines = ["| option | USD / month | TND / month |", "|---|---|---|"]
    for s in sorted(scenarios, key=lambda s: s["monthly_usd"]):
        lines.append(f"| {s['name']} | {s['monthly_usd']:.2f} | {s['monthly_usd'] * USD_TO_TND:.2f} |")
    return "\n".join(lines)


if __name__ == "__main__":
    q = 2000                                   # questions per month, from the interview
    per = {n: query_cost(p, in_tokens=2500, out_tokens=250, cache_hit=0.4) for n, p in PRICES.items()}
    local = local_monthly(watts=180, hours_per_day=10, price_kwh=0.10, hardware_cost=900)   # a PC with a 12 GB GPU
    rows = [{"name": n, "monthly_usd": api_monthly(q, c)} for n, c in per.items()] + [{"name": "local GPU PC", "monthly_usd": local}]
    print(cost_table(rows))
    for n, c in per.items():
        print(f"local beats {n} above {break_even(local, c):,} questions a month")
    print("machines at a peak of 6 questions/minute, 8 s each:", gpus_needed(6, 8))
