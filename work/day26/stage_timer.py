"""Where do the seconds and the cents go?

A RAG query has stages: embed the question, search, rerank, generate. Timing only the
total tells you "3.4 s, too slow" but not *where* to cut. This file times each stage
separately, prices a query, and reports p50/p95 per stage over many queries.

1. `StageTimer`: a stopwatch with one lap per stage, used with `with t.stage("name"):`.
2. `query_cost`: what one query costs in dollars.
3. `stage_report`: typical (p50) and worst-case (p95) seconds per stage over many queries.
"""
import statistics
import time
from contextlib import contextmanager


class StageTimer:
    """A stopwatch that keeps one total per stage name.

    `t.times` is a dict like `{"embed": 0.12, "generate": 1.8}` (seconds).
    If the same stage runs twice, its two durations are **added up**.

    Example:
        >>> t = StageTimer()
        >>> with t.stage("search"):
        ...     time.sleep(0.1)
        >>> round(t.times["search"], 1)
        0.1
        >>> with t.stage("search"):
        ...     time.sleep(0.1)
        >>> round(t.times["search"], 1)
        0.2
    """

    def __init__(self):
        self.times = {}

    @contextmanager
    def stage(self, name):
        """Time the block inside `with t.stage(name):` and add it to `times[name]`.

        `@contextmanager` turns this generator into something `with` can use:
        the code before `yield` runs when the block starts, the code after it when
        the block ends. `try/finally` makes sure the time is recorded **even if the
        block raises an error**, so a failing stage still shows up.

        Example (a stage that crashes is still timed):
            >>> t = StageTimer()
            >>> try:
            ...     with t.stage("rerank"):
            ...         time.sleep(0.1)
            ...         raise ValueError("model timeout")
            ... except ValueError:
            ...     pass
            >>> round(t.times["rerank"], 1)
            0.1
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            self.times[name] = self.times.get(name, 0.0) + time.perf_counter() - start

    def total(self):
        """Seconds for the whole query: the sum of every stage.

        Example:
            >>> t = StageTimer()
            >>> t.times = {"embed": 0.25, "generate": 1.5}
            >>> t.total()
            1.75
        """
        return sum(self.times.values())


def query_cost(tokens_in, tokens_out, price_in_per_m, price_out_per_m, judge_calls=0, judge_cost=0.0):
    """Dollars for one query: generation tokens plus any judge calls.

    Providers price per **million** tokens, separately for input and output
    (output is usually several times more expensive). So:
    `(tokens_in * price_in + tokens_out * price_out) / 1,000,000`.
    If an LLM judge grades the answer, add `judge_calls * judge_cost`.

    Example (1,800 tokens in, 150 out, at $0.30 / $2.50 per million):
        >>> round(query_cost(1800, 150, 0.30, 2.50), 6)
        0.000915
        >>> round(1000 * query_cost(1800, 150, 0.30, 2.50), 2)
        0.92
        >>> round(query_cost(1800, 150, 0.30, 2.50, judge_calls=2, judge_cost=0.001), 6)
        0.002915
    """
    return (tokens_in * price_in_per_m + tokens_out * price_out_per_m) / 1_000_000 + judge_calls * judge_cost


def stage_report(timers):
    """p50 and p95 seconds for each stage, plus the total, over many queries.

    - **p50** (the median): a typical query.
    - **p95**: 95% of queries are faster than this. It is what your slowest
      users feel, so latency targets are usually set on p95.

    Steps: collect every stage name (in the order first seen), then for each
    stage gather its time from every timer and take the 50th and 95th
    percentiles with `statistics.quantiles(values, n=100, method="inclusive")`.
    That returns 99 cut points: item 49 is p50 and item 94 is p95.

    Example (5 fake queries where generation dominates):
        >>> timers = []
        >>> for s in [1.0, 1.2, 1.1, 3.0, 1.3]:
        ...     t = StageTimer()
        ...     t.times = {"embed": 0.1, "generate": s}
        ...     timers.append(t)
        >>> report = stage_report(timers)
        >>> {stage: (round(p50, 2), round(p95, 2)) for stage, (p50, p95) in report.items()}
        {'embed': (0.1, 0.1), 'generate': (1.2, 2.66), 'total': (1.3, 2.76)}
    """
    names = []
    for t in timers:
        names += [n for n in t.times if n not in names]

    def pq(values):
        q = statistics.quantiles(values, n=100, method="inclusive")
        return q[49], q[94]

    out = {n: pq([t.times[n] for t in timers if n in t.times]) for n in names}
    out["total"] = pq([t.total() for t in timers])
    return out


if __name__ == "__main__":
    import random

    # A simulated pipeline: 30 queries with 4 stages each, with realistic random delays.
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
