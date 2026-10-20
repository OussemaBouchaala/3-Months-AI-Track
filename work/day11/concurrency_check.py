# Fire 5 concurrent /extract requests at your running service (port 8002).
# If async is done right they overlap, so the total is close to ONE request's time.
import asyncio
import time

import httpx

URL = "http://127.0.0.1:8002/extract"
SAMPLE = {"text": "Appartement S+2, 95 m2, Sousse Khezama, 280 000 DT", "model": "local"}


async def one(client):
    """Send one request and return its duration in seconds."""
    start = time.perf_counter()
    resp = await client.post(URL, json=SAMPLE)
    resp.raise_for_status()
    return time.perf_counter() - start


async def burst(client, n=5):
    """Run n calls of one(client) concurrently. Return (total_seconds, list_of_each_duration)."""
    start = time.perf_counter()
    # TODO: durations = await asyncio.gather(...)
    results = await asyncio.gather(*[one(client) for _ in range(n)])
    return round(time.perf_counter() - start, 2), results


if __name__ == "__main__":
    async def main():
        async with httpx.AsyncClient(timeout=120) as client:
            single = await one(client)
            total, each = await burst(client)
            print(f"one request: {single:.2f}s | 5 concurrent: {total:.2f}s total, slowest {max(each):.2f}s")
            print("concurrent" if total < 2 * single else "they ran one after another: check for blocking calls")

    asyncio.run(main())
