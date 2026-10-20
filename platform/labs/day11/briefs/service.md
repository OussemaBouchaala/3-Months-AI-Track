# Wrap it in FastAPI
**Topic:** honest status codes: 422 bad request, 502 bad upstream, 504 slow upstream.

## Real example
A tiny weather service with the same three error cases. `fetch` stands in for the upstream (your model). Read how each failure becomes an honest status code:

```python
import asyncio
from fastapi import HTTPException

class Timeout(Exception): ...

async def fetch(city):                 # the "upstream"
    if city == "slow": raise Timeout()
    return "sunny" if city == "Sousse" else "???"

async def weather(city):
    try:
        raw = await fetch(city)
    except Timeout:
        raise HTTPException(504, "Upstream too slow")
    if raw == "???":
        raise HTTPException(502, "Upstream gave unusable data")
    return {"city": city, "sky": raw}

for c in ["Sousse", "Mars", "slow"]:
    try:
        print(c, "->", asyncio.run(weather(c)))
    except HTTPException as e:
        print(c, "->", e.status_code, e.detail)
```

## Your mission
Build `POST /extract` with async model calls, one retry, and the right errors.

## Steps
1. `call_model`: `await client.post(...)` to Ollama, return the reply text.
2. `extract`: call, validate, retry once with the error.
3. Still invalid: `HTTPException(502)`. `httpx.TimeoutException`: `HTTPException(504)`.
4. Start it in a terminal: `uvicorn service:app --port 8002 --reload`.

## Done when
**Check** drives the endpoint with fake model answers and gets 200, 502, 504 and 422.
