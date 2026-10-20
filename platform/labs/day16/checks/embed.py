import numpy as np

sent = []


class FakeResponse:
    def __init__(self, n):
        self.n = n

    def raise_for_status(self):
        return None

    def json(self):
        return {"embeddings": [[float(i), 1.0, 0.0] for i in range(self.n)]}


class FakeHttpx:
    def post(self, url, json=None, timeout=None, **kw):
        sent.append({"url": url, "body": json, "timeout": timeout})
        return FakeResponse(len(json["input"]))


embed = fn("embed")
real = embed.__globals__.get("httpx")
embed.__globals__["httpx"] = FakeHttpx()
try:
    out = embed(["a", "b", "c"])
except Exception as exc:  # shown by the checks below
    out = exc
finally:
    embed.__globals__["httpx"] = real

check("embed runs", not isinstance(out, Exception), f"embed raised {out!r}" if isinstance(out, Exception) else "")
check("embed posts to /api/embed", lambda: sent[0]["url"].endswith("/api/embed"), 'httpx.post(f"{OLLAMA}/api/embed", json=..., timeout=120)')
check("embed sends the model and the list of texts", lambda: sent[0]["body"]["input"] == ["a", "b", "c"] and sent[0]["body"]["model"])
check("embed returns a (3, dim) float32 array", lambda: isinstance(out, np.ndarray) and out.shape == (3, 3) and out.dtype == np.float32,
      'np.array(resp.json()["embeddings"], dtype=np.float32)')

norm = fn("normalize")
m = np.array([[3.0, 4.0], [0.0, 2.0]])
check("normalize gives rows of length 1", lambda: np.allclose(np.linalg.norm(norm(m), axis=1), 1.0))
check("normalize keeps the direction", lambda: np.allclose(norm(m)[0], [0.6, 0.8]))

calls = []


def fake_embed(texts):
    calls.append(len(texts))
    return np.ones((len(texts), 4), dtype=np.float32)


check("embed_in_batches respects batch_size", lambda: (calls.clear(), fn("embed_in_batches")(list("abcdefghij"), batch_size=4, embed_fn=fake_embed).shape)[1] == (10, 4) and calls == [4, 4, 2],
      "for i in range(0, len(texts), batch_size): ... then np.vstack(parts)")

def unit(rows):
    a = np.array(rows, dtype=float)
    return a / np.linalg.norm(a, axis=1, keepdims=True)


mat, q = unit([[1.0, 0, 0], [0.7, 0.7, 0], [0, 0, 1], [0.9, 0.1, 0]]), unit([[1.0, 0, 0]])[0]
res = lambda: fn("search")(q, mat, k=2)
check("search returns k results, best first", lambda: [i for i, _ in res()] == [0, 3])
check("search returns (index, score) with float scores", lambda: isinstance(res()[0][1], float) and abs(res()[0][1] - 1.0) < 1e-6,
      "[(int(i), float(scores[i])) for i in np.argsort(-scores)[:k]]")
