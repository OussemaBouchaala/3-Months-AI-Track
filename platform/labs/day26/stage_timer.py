# Where do the seconds and the cents go? Time each stage of a query and price it.
# Remember Week 1, Day 3: a context manager is the clean way to time a block.
import statistics
import time
from contextlib import contextmanager


class StageTimer:
    """Usage:
        t = StageTimer()
        with t.stage("embed"):
            ...
        with t.stage("generate"):
            ...
        t.times  -> {"embed": 0.12, "generate": 1.8}   (seconds; the same stage twice is ADDED up)
        t.total() -> 1.92"""

    def __init__(self):
        self.times = {}

    @contextmanager
    def stage(self, name):
        # TODO: start = time.perf_counter(); yield; add the elapsed time to self.times[name]
        # Use try/finally so a stage that raises is still timed.
        ...

    def total(self):
        # TODO
        ...


def query_cost(tokens_in, tokens_out, price_in_per_m, price_out_per_m, judge_calls=0, judge_cost=0.0):
    """Generation cost (per-million prices, like Week 2) plus judge_calls * judge_cost."""
    # TODO
    ...


def stage_report(timers):
    """timers: list of StageTimer, one per query. For each stage name, return (p50, p95) in seconds,
    using statistics.quantiles(values, n=100, method="inclusive"), items 49 and 94.
    Return {"embed": (p50, p95), ..., "total": (p50, p95)}."""
    # TODO
    ...


if __name__ == "__main__":
    import json
    import random

    # A simulated pipeline so you can see the report now; on Saturday you'll wrap your real stages.
    timers = []
    for _ in range(30):
        t = StageTimer()
        with t.stage("embed"):
            time.sleep(random.uniform(0.01, 0.03))
        with t.stage("search"):
            time.sleep(0.002)
        with t.stage("rerank"):
            time.sleep(random.uniform(0.05, 0.25))
        with t.stage("generate"):
            time.sleep(random.uniform(0.1, 0.6))
        timers.append(t)
    for stage, (p50, p95) in stage_report(timers).items():
        print(f"{stage:<9} p50 {p50:.3f}s  p95 {p95:.3f}s")
    print(f"cost per 1,000 queries: ${1000 * query_cost(1800, 150, 0.30, 2.50):.2f}")
