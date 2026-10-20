# The pipeline as a service
**Topic:** one `/ask` endpoint over the whole pipeline, with the retriever and model injected so tests need no database.

## Real example
A weather service whose data source is injected (different service, same pattern):

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

def create_app(get_temp):
    app = FastAPI()
    @app.get("/temp/{city}")
    def temp(city: str):
        return {"city": city, "celsius": get_temp(city)}
    return app

fake = lambda city: {"Sousse": 24, "Tunis": 21}.get(city)
print(TestClient(create_app(fake)).get("/temp/Sousse").json())
```

In production you pass the real API client; in tests a dict. Same app code, no network in tests.

## Your mission
Wrap Week 8 in a FastAPI service you can call from a UI next week.

## Steps
1. `build_prompt` (Day 18's, with title > section).
2. The `request_id` middleware.
3. `/ask`: scrub, retrieve, IDK shortcut, generate (503 on failure), clean markers, sources, latency.
4. **Run** with the real wiring (Postgres + Ollama) and ask 5 golden-set questions at `/docs`.

## Done when
**Check** passes and `/ask` answers a real question with a source from your documents.
