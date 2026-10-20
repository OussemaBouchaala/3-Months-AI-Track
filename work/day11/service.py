# Run in your TERMINAL: uvicorn service:app --port 8002 --reload
# Check tests the endpoint with a fake model, so it works without Ollama.
import json
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = "qwen2.5:3b"

app = FastAPI()


class ExtractIn(BaseModel):
    text: str
    model: str = "local"   # "local" or "api"


class Listing(BaseModel):
    price_tnd: float | None = None
    surface_m2: float | None = None
    rooms: int | None = None
    city: str | None = None


def build_prompt(text, error=None):
    prompt = f"Return JSON only with keys {list(Listing.model_fields)}.\n\nListing:\n{text}"
    return prompt + (f"\n\nYour previous answer was invalid: {error}. Return corrected JSON." if error else "")


async def call_model(client: httpx.AsyncClient, prompt: str, model: str) -> str:
    """Return the raw reply text. For "local": await client.post(f"{OLLAMA_URL}/api/chat", json={...,
    "format": "json", "stream": False}) and read ["message"]["content"] (same body as day10)."""
    # TODO
    payload = {
        "model": MODEL if model == "local" else model,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False
    }
    try:
        resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except httpx.TimeoutException:
        raise
    except Exception as e:
        # If the model service is down or returns an error, let it bubble up or return empty
        # But for the "Check" to work with a fake model, we assume the client is mocked or Ollama is up.
        # If Ollama is down, we want a 502 or 504, not a crash.
        raise HTTPException(502, "Model service error")


@app.post("/extract")
async def extract(body: ExtractIn) -> Listing:
    """1. async with httpx.AsyncClient(timeout=30) as client: raw = await call_model(client, build_prompt(body.text), body.model)
    2. Validate with Listing.model_validate_json(raw). On ValidationError, retry ONCE with the error in the prompt.
    3. Still invalid -> raise HTTPException(502, ...). httpx.TimeoutException at any point -> HTTPException(504, ...)."""
    # TODO
    prompt = build_prompt(body.text)
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # First attempt
            raw = await call_model(client, prompt, body.model)
            
            # Try to validate
            try:
                return Listing.model_validate_json(raw)
            except ValidationError as ve:
                # Retry once with error feedback
                new_prompt = build_prompt(body.text, error=str(ve))
                raw_retry = await call_model(client, new_prompt, body.model)
                
                try:
                    return Listing.model_validate_json(raw_retry)
                except ValidationError:
                    # Still invalid after retry
                    raise HTTPException(502, "Upstream gave unusable data")
        
        except httpx.TimeoutException:
            raise HTTPException(504, "Upstream too slow")
        except HTTPException:
            raise
        except Exception:
            # Any other unexpected error from the model call
            raise HTTPException(502, "Upstream bad request")
