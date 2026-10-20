# The same 10 extractions, run on an open model served locally by Ollama.
# Before Run: install Ollama, then in a terminal `ollama pull qwen2.5:3b` (Ollama keeps serving on port 11434).
# Check uses a fake HTTP client, so it works without Ollama.
import json
import statistics
import time

import httpx

OLLAMA = "http://localhost:11434"
MODEL = "qwen2.5:3b"   # change to what your machine can run
FIELDS = ["price_tnd", "surface_m2", "rooms", "city"]


def chat(prompt, model=MODEL):
    """POST {OLLAMA}/api/chat with json={"model": model, "messages": [{"role": "user", "content": prompt}],
    "format": "json", "stream": False} and timeout=120.
    Return (reply_text, seconds) where reply_text = resp.json()["message"]["content"]."""
    start = time.perf_counter()
    # TODO
    ...


def field_accuracy(pred, label):
    """Fraction of FIELDS where pred.get(field) == label[field] (a missing field counts as wrong)."""
    # TODO
    ...


if __name__ == "__main__":
    listings = json.load(open("../day09/listings.json", encoding="utf-8"))
    chat("Reply with {}")  # warm-up: the first call loads the model (cold start)

    latencies, accuracies = [], []
    for item in listings:
        prompt = f"Extract {FIELDS} from this listing. Reply with JSON only.\n\n{item['text']}"
        reply, seconds = chat(prompt)
        pred = json.loads(reply)
        latencies.append(seconds)
        accuracies.append(field_accuracy(pred, item["label"]))
        print(f"{seconds:5.2f}s  acc={accuracies[-1]:.2f}  {pred}")

    print(f"mean field accuracy {statistics.mean(accuracies):.2f}, median latency {statistics.median(latencies):.2f}s")
    # TODO: write these two numbers next to yesterday's API results in your notes
