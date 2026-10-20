# Search by meaning
**Topic:** cosine similarity compares direction, not length.

## Real example
A music app recommends songs with "mood vectors" (energy, sadness, danceability). Same maths you'll write: cosine, then sort:

```python
import numpy as np

songs = {"Summer party": np.array([0.9, 0.1, 0.9]),
         "Rainy night": np.array([0.2, 0.9, 0.1]),
         "Gym mix": np.array([1.0, 0.0, 0.7])}
liked = np.array([0.8, 0.1, 1.0])   # what the user likes

cos = lambda a, b: float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
for name in sorted(songs, key=lambda n: cos(liked, songs[n]), reverse=True):
    print(f"{cos(liked, songs[name]):.3f}  {name}")
```

## Your mission
Implement cosine similarity yourself and rank documents against a query.

## Steps
1. `cosine`: `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))`.
2. `rank`: `sorted(docs, key=..., reverse=True)`.
3. **Run** and check the ranking makes sense.
4. Fill `CORPUS_NAME` and `CORPUS_PATH` for Weeks 3-6.

## Done when
**Check** confirms the maths, the ranking, and your corpus choice.
