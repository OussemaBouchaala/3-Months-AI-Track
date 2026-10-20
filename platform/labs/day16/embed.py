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
    ...


def normalize(matrix):
    """Divide every row by its length (np.linalg.norm(..., axis=1, keepdims=True)) so each row has norm 1.
    After this, a dot product IS the cosine similarity."""
    # TODO
    ...


def embed_in_batches(texts, batch_size=16, embed_fn=embed):
    """Call embed_fn on slices of at most batch_size texts and stack the results with np.vstack.
    Real servers reject huge requests, and one failed batch shouldn't cost you everything."""
    # TODO
    ...


def search(query_vec, matrix, k=3):
    """matrix rows and query_vec are normalized. Scores = matrix @ query_vec.
    Return the top k as a list of (row_index, score) with the best first. Scores as Python floats."""
    # TODO: np.argsort(-scores)[:k]
    ...


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
