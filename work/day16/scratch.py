import numpy as np

m = np.array([[3.0, 4.0], [1.0, 0.0], [0.0, 2.0]])
m = m / np.linalg.norm(m, axis=1, keepdims=True)    # every row now has length 1
q = np.array([1.0, 1.0]); q = q / np.linalg.norm(q)
scores = m @ q                                       # 3 cosine similarities at once
print(scores.round(3), "best:", int(np.argmax(scores)))
