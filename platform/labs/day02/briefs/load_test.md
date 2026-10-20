# Measure it
**Topic:** `asyncio.gather` runs many requests at once.

## Your mission
Fire 5 concurrent requests at each endpoint and time them.

## Steps
1. In `hit`, build `n` coroutines `client.get(path)` and `await asyncio.gather(*requests)`.
2. With `app_async` running in your terminal, predict the 4 timings, then **Run**.
3. Copy the measured table into your notes with one reason per line.

## Done when
**Check** shows the 5 requests overlap (about one request's time, not five).
