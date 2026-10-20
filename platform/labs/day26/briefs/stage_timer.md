# Latency and cost per stage
**Topic:** time every stage separately; the slowest one is where optimization pays.

## Real example
A food-delivery app times each step of an order with a context manager, then sees which step makes customers wait:

```python
import time
from contextlib import contextmanager

times = {}

@contextmanager
def stage(name):
    start = time.perf_counter()
    try:
        yield
    finally:
        times[name] = times.get(name, 0) + time.perf_counter() - start

with stage("find_restaurant"):
    time.sleep(0.02)
with stage("payment"):
    time.sleep(0.15)
with stage("find_restaurant"):     # same stage again: added up
    time.sleep(0.01)
print({k: round(v, 2) for k, v in times.items()}, "slowest:", max(times, key=times.get))
```

## Your mission
Build a reusable stage timer and a p50/p95 report per stage.

## Steps
1. `StageTimer.stage`: `try: yield finally: add elapsed`.
2. `total`: sum of the stages.
3. `query_cost`: Week 2's formula plus judge calls.
4. `stage_report`: collect each stage's values across timers, quantiles, plus `"total"`.
5. **Run** the simulation, then wrap the 4 stages of your real pipeline the same way.

## Done when
**Check** passes and you know which stage of your RAG is the slowest.
