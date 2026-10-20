# Prove it doesn't block
**Topic:** day 2's lesson, on your real service.

## Real example
Five "requests" that each wait 0.5 s. Sequential takes 2.5 s; with `asyncio.gather` they overlap and take about 0.5 s:

```python
import asyncio, time

async def one():
    await asyncio.sleep(0.5)          # like waiting for a model
    return "ok"

async def main():
    t = time.perf_counter()
    for _ in range(5): await one()
    print("one by one:", round(time.perf_counter() - t, 2), "s")
    t = time.perf_counter()
    results = await asyncio.gather(*[one() for _ in range(5)])
    print("together:  ", round(time.perf_counter() - t, 2), "s", results)

asyncio.run(main())
```

## Your mission
Send 5 requests at once and show they overlap.

## Steps
1. `burst`: `await asyncio.gather(*[one(client) for _ in range(n)])`; return total time and the list.
2. With the service running, **Run**: 5 concurrent should take about as long as 1.

## Done when
**Check** shows `burst` overlaps its requests.
