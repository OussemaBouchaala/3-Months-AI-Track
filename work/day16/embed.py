# Turn every chunk into a vector with a multilingual embedding model served by Ollama.
# Before Run: in a terminal, `ollama pull bge-m3` (about 1.2 GB, Arabic + French + English).
# Check uses a fake HTTP client, so it works without Ollama.
import json

import httpx
import numpy as np

OLLAMA = "http://localhost:11434"
EMBED_MODEL = "bge-m3"


def embed(texts, model=EMBED_MODEL):
    """POST {OLLAMA}/api/embed with json={"model": model, "input": texts} and timeout=120.
    The reply is {"embeddings": [[...], [...]]}: one list of floats per text.
    Return a float32 numpy array of shape (len(texts), dim)."""
    # TODO
    url = OLLAMA + "/api/embed"
    payload = {"model": model, "input": texts}
    timeout = 120
    response = httpx.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    embeddings = data["embeddings"]
    return np.array(embeddings, dtype=np.float32)


def normalize(matrix):
    """Divide every row by its length (np.linalg.norm(..., axis=1, keepdims=True)) so each row has norm 1.
    After this, a dot product IS the cosine similarity."""
    # TODO
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    # Avoid division by zero by replacing zero norms with 1
    norms[norms == 0] = 1
    return matrix / norms


def embed_in_batches(texts, batch_size=16, embed_fn=embed):
    """Call embed_fn on slices of at most batch_size texts and stack the results with np.vstack.
    Real servers reject huge requests, and one failed batch shouldn't cost you everything."""
    # TODO
    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
    result_batches = [embed_fn(batch) for batch in batches]
    return np.vstack(result_batches)


def search(query_vec, matrix, k=3):
    """matrix rows and query_vec are normalized. Scores = matrix @ query_vec.
    Return the top k as a list of (row_index, score) with the best first. Scores as Python floats."""
    # TODO: np.argsort(-scores)[:k]
    scores = matrix @ query_vec
    top_indices = np.argsort(-scores)[:k]
    result = []
    for idx in top_indices:
        result.append((idx, float(scores[idx])))
    return result


if __name__ == "__main__":
    chunks = json.load(open("../day15/chunks.json", encoding="utf-8"))
    matrix = normalize(embed_in_batches([c["text"] for c in chunks]))
    np.save("embeddings.npy", matrix)
    print("embeddings:", matrix.shape, "saved to embeddings.npy")

    # Same question, three languages: do they find the same chunk?
    for q in ["How much is the deposit for renting?",
              "Quel est le montant de la caution pour une location ?",
              "كم قيمة الضمان عند الكراء؟"]:
        qv = normalize(embed([q]))[0]
        best = [(chunks[i]["heading"], round(s, 3)) for i, s in search(qv, matrix, k=3)]
        print(q, "\n   ", best)
