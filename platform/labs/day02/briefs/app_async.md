# Four ways to wait
**Topic:** `async def` runs on the event loop; plain `def` runs in a thread pool.

## Your mission
Build four endpoints that each wait 2 seconds in a different way.

## Steps
1. `/blocking`: `async def` + `time.sleep(2)` (blocks the loop on purpose).
2. `/awaiting`: `async def` + `await asyncio.sleep(2)`.
3. `/threaded`: plain `def` + `time.sleep(2)`.
4. `/fixed`: `async def` + `await run_in_threadpool(time.sleep, 2)`.
5. Start it in a terminal: `uvicorn app_async:app --port 8001`.

## Done when
**Check** confirms each endpoint waits the right way (no server needed).
