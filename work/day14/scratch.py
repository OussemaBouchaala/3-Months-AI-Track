import numpy as np

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

q = np.array([0.9, 0.1, 0.0])
docs = {"rent law": np.array([0.8, 0.2, 0.1]), "football": np.array([0.0, 0.1, 0.9])}
for name, v in docs.items():
    print(name, round(cosine(q, v), 3))
print(cosine([1, 2], [10, 20]))