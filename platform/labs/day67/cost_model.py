# "Local is free" and "the API is cheap" are both wrong at some volume. Model both, find the break-even,
# and put a monthly number in front of the agency manager. Prices change: keep them in one dict.
import math

PRICES = {  # USD per million tokens; check the providers' pricing pages and update
    "small API model": {"in": 0.80, "out": 4.00, "cached_in": 0.08},
    "large API model": {"in": 3.00, "out": 15.00, "cached_in": 0.30},
}
USD_TO_TND = 3.1


def query_cost(price, in_tokens, out_tokens, cache_hit=0.0):
    """USD for one query. A share cache_hit of the input tokens is billed at price["cached_in"] (prompt caching:
    the system prompt and instructions are the same every time), the rest at price["in"]."""
    # TODO
    ...


def api_monthly(queries_per_month, per_query):
    return queries_per_month * per_query


def local_monthly(watts, hours_per_day, price_kwh, hardware_cost=0.0, months_amortized=36, days=30):
    """Electricity (watts / 1000 * hours_per_day * days * price_kwh) + hardware_cost / months_amortized."""
    # TODO
    ...


def gpus_needed(peak_queries_per_minute, seconds_per_query, concurrency_per_gpu=1):
    """Machines needed at peak: ceil(peak qpm * seconds_per_query / 60 / concurrency_per_gpu), at least 1."""
    # TODO
    ...


def break_even(local_month, per_query):
    """Queries per month above which local is cheaper than the API: ceil(local_month / per_query). per_query 0 -> None."""
    # TODO
    ...


def cost_table(scenarios):
    """scenarios: [{"name", "monthly_usd"}] -> Markdown | option | USD / month | TND / month |, cheapest first,
    2 decimals, TND = USD * USD_TO_TND."""
    # TODO
    ...


if __name__ == "__main__":
    q = 2000                                   # questions per month, from the interview
    per = {n: query_cost(p, in_tokens=2500, out_tokens=250, cache_hit=0.4) for n, p in PRICES.items()}
    local = local_monthly(watts=180, hours_per_day=10, price_kwh=0.10, hardware_cost=900)   # a PC with a 12 GB GPU
    rows = [{"name": n, "monthly_usd": api_monthly(q, c)} for n, c in per.items()] + [{"name": "local GPU PC", "monthly_usd": local}]
    print(cost_table(rows))
    for n, c in per.items():
        print(f"local beats {n} above {break_even(local, c):,} questions a month")
    print("machines at a peak of 6 questions/minute, 8 s each:", gpus_needed(6, 8))
