# Cosine similarity and ranking by hand: the core of vector search.
import numpy as np

# Toy 3-D "embeddings" (real models output 384-1024 dimensions).
DOCS = {
    "rent law": np.array([0.8, 0.2, 0.1]),
    "apartment prices": np.array([0.7, 0.6, 0.0]),
    "football results": np.array([0.0, 0.1, 0.9]),
    "lease contract": np.array([0.9, 0.1, 0.2]),
    "weather": np.array([0.1, 0.0, 0.5]),
}
QUERY = np.array([0.9, 0.1, 0.0])   # "what does the law say about renting?"


def cosine(a, b):
    """Cosine similarity WITHOUT sklearn: dot(a, b) / (norm(a) * norm(b)).
    Use np.dot and np.linalg.norm. Return a Python float."""
    # TODO
    ...


def rank(query, docs):
    """Return the doc names sorted by cosine similarity to query, most similar first."""
    # TODO: sorted(docs, key=..., reverse=True)
    ...


if __name__ == "__main__":
    for name in rank(QUERY, DOCS):
        print(f"{cosine(QUERY, DOCS[name]):.3f}  {name}")

# The Arabic corpus you'll use for Weeks 3-6:
CORPUS_NAME = ""   # e.g. a Hugging Face dataset id
CORPUS_PATH = ""   # where it is on your disk
