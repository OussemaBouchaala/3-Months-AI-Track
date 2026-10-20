import asyncio
import inspect

burst = fn("burst")


class FakeResp:
    def raise_for_status(self):
        return None


class FakeClient:
    def __init__(self):
        self.calls = 0

    async def post(self, url, json=None):
        self.calls += 1
        await asyncio.sleep(0.2)
        return FakeResp()


check("burst is async", lambda: inspect.iscoroutinefunction(burst))
client = FakeClient()
result = asyncio.run(burst(client, 5))
check("burst returns (total_seconds, durations)", lambda: len(result) == 2 and len(result[1]) == 5,
      "return time.perf_counter() - start, list(durations)")
check("burst sends 5 requests", client.calls == 5)
check("the 5 requests overlap (about 0.2 s total, not 1 s)", lambda: 0.15 < result[0] < 0.6,
      "asyncio.gather(*[one(client) for _ in range(n)])")
