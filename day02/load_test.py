# Start app_async.py in your terminal first (uvicorn app_async:app --port 8001),
# then press Run here. Check works without the server (it uses a fake client).
import asyncio
import time

import httpx

BASE = "http://127.0.0.1:8001"
ENDPOINTS = ["/blocking", "/awaiting", "/threaded", "/fixed"]


async def hit(client, path, n=5):
    """Send n GET requests to path AT THE SAME TIME and return the elapsed seconds (float)."""
    start = time.perf_counter()
    # TODO: build a list of n `client.get(path)` coroutines,
    #       then run them together with `await asyncio.gather(*requests)`
    requests = [client.get(path) for _ in range(n)]
    await asyncio.gather(*requests)
    return time.perf_counter() - start


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=30) as client:
        for path in ENDPOINTS:
            seconds = await hit(client, path)
            print(f"{path:<10} {seconds:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
