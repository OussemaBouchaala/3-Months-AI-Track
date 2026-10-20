import asyncio

import httpx
from fastapi.testclient import TestClient

app, extract = var("app"), fn("extract")
check("POST /extract exists", lambda: any(getattr(r, "path", "") == "/extract" for r in app.routes))
check("extract is async def", lambda: asyncio.iscoroutinefunction(extract), "FastAPI awaits it on the event loop.")

good = '{"price_tnd": 250000, "surface_m2": 120, "rooms": 3, "city": "Sousse"}'
bad = '{"rooms": "three"}'


def post_with(replies, payload=None):
    """Call the endpoint with call_model replaced by a fake that returns `replies` in order."""
    calls = []

    async def fake_call_model(client, prompt, model):
        calls.append(prompt)
        r = replies[min(len(calls), len(replies)) - 1]
        if isinstance(r, Exception):
            raise r
        return r

    g = extract.__globals__
    real = g.get("call_model")
    g["call_model"] = fake_call_model
    try:
        resp = TestClient(app).post("/extract", json=payload or {"text": "Appart S+3 Sousse 250 mille"})
    finally:
        g["call_model"] = real
    return resp, calls


check("valid model output -> 200 with the listing",
      lambda: post_with([good])[0].status_code == 200 and post_with([good])[0].json()["city"] == "Sousse")
check("invalid then valid -> 200 after one retry", lambda: post_with([bad, good])[0].status_code == 200 and len(post_with([bad, good])[1]) == 2)
check("the retry prompt includes the validation error", lambda: "rooms" in post_with([bad, good])[1][1].split("Listing:")[-1])
check("invalid twice -> 502 Bad Gateway", lambda: post_with([bad, bad, good])[0].status_code == 502,
      "After the retry fails: raise HTTPException(status_code=502, detail=...).")
check("model timeout -> 504 Gateway Timeout", lambda: post_with([httpx.ReadTimeout("slow")])[0].status_code == 504,
      "Wrap the model calls in try/except httpx.TimeoutException -> HTTPException(504).")
check("missing text -> 422 (FastAPI validates the body)", lambda: post_with([good], {"model": "local"})[0].status_code == 422)


class FakeResp:
    def raise_for_status(self):
        return None

    def json(self):
        return {"message": {"content": good}}


class FakeAsyncClient:
    def __init__(self):
        self.body = None

    async def post(self, url, json=None, **kw):
        self.url, self.body = url, json
        return FakeResp()


def local_call():
    c = FakeAsyncClient()
    text = asyncio.run(fn("call_model")(c, "hi", "local"))
    return text, c


check("call_model('local') awaits Ollama's /api/chat and returns the reply",
      lambda: local_call()[0] == good and local_call()[1].url.endswith("/api/chat"))
check("call_model asks Ollama for JSON without streaming",
      lambda: local_call()[1].body["format"] == "json" and local_call()[1].body["stream"] is False)
