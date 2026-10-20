# Run an open model yourself
**Topic:** Ollama serves local models over HTTP; the first call is a slow cold start.

## Real example
Timing any slow call and measuring accuracy work the same way, whatever the model. Here a fake "model" sleeps like a cold start on the first call:

```python
import time, statistics

calls = {"n": 0}
def fake_chat(prompt):
    start = time.perf_counter()
    calls["n"] += 1
    time.sleep(0.6 if calls["n"] == 1 else 0.05)   # first call = cold start
    return '{"city": "Sousse", "rooms": 3}', time.perf_counter() - start

fake_chat("warm-up")                       # never measure the first one
times = [fake_chat("extract")[1] for _ in range(5)]
print("median latency", round(statistics.median(times), 3), "s")

pred, label = {"city": "Sousse", "rooms": 2}, {"city": "Sousse", "rooms": 3}
print("field accuracy", sum(pred.get(k) == v for k, v in label.items()) / len(label))
```

## Your mission
Run your 10 extractions through a local model and measure accuracy and latency.

## Steps
1. `chat`: `httpx.post` to `/api/chat` with `format="json"`, `stream=False`; return text and seconds.
2. `field_accuracy`: share of the 4 fields that match your label.
3. Install Ollama, `ollama pull qwen2.5:3b`, then **Run**.
4. Note accuracy and median latency next to yesterday's API results.

## Done when
**Check** confirms the request body and the accuracy maths (no Ollama needed).
