import asyncio
import inspect

hit = fn("hit")


class FakeClient:
    """Answers every GET after 0.2 s, like a non-blocking server."""
    def __init__(self):
        self.calls = []

    async def get(self, path):
        self.calls.append(path)
        await asyncio.sleep(0.2)
        return path


check("hit is an async function", lambda: inspect.iscoroutinefunction(hit))
client = FakeClient()
elapsed = asyncio.run(hit(client, "/x", n=5))
check("hit sends n requests", len(client.calls) == 5, f"It sent {len(client.calls)} of 5. Make n `client.get(path)` calls.")
check("hit returns the elapsed seconds as a number", isinstance(elapsed, float))
check("the 5 requests run concurrently (about 0.2 s, not 1 s)",
      len(client.calls) == 5 and isinstance(elapsed, float) and 0.15 < elapsed < 0.6,
      "Await them together with asyncio.gather(*requests), not one by one in a loop.")
