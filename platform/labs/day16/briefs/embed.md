# Multilingual embeddings
**Topic:** one vector per chunk; normalized vectors turn cosine into a plain dot product.

## Real example
A support team searches old tickets by meaning. A fake 4-dimensional "model" stands in for the real one so you can run it now. Same steps as your exercise: embed, normalize, dot product, top k:

```python
import numpy as np

fake_vectors = {"printer jams": [0.9, 0.1, 0, 0], "imprimante bloquée": [0.85, 0.2, 0.05, 0],
                "password reset": [0, 0.1, 0.9, 0.2], "VPN down": [0.1, 0, 0.3, 0.9]}
tickets = list(fake_vectors)
m = np.array([fake_vectors[t] for t in tickets], dtype=np.float32)
m = m / np.linalg.norm(m, axis=1, keepdims=True)

q = np.array([0.8, 0.3, 0, 0.1], dtype=np.float32)      # "paper stuck in the printer"
q = q / np.linalg.norm(q)
scores = m @ q
for i in np.argsort(-scores)[:2]:
    print(round(float(scores[i]), 3), tickets[i])
```

Notice the French ticket ranks second: a multilingual model puts the same meaning in the same place.

## Your mission
Embed the 14 handbook chunks with `bge-m3` and search them in three languages.

## Steps
1. `embed`: one `httpx.post` to `/api/embed`, return `np.array(..., dtype=np.float32)`.
2. `normalize`: divide each row by its norm.
3. `embed_in_batches`: loop over slices, `np.vstack` at the end.
4. `search`: scores with `@`, `np.argsort(-scores)[:k]`.
5. In a terminal: `ollama pull bge-m3`, then **Run**.

## Done when
**Check** passes, and your three questions (EN, FR, AR) find the deposit section (الضمان) in their top 3.
