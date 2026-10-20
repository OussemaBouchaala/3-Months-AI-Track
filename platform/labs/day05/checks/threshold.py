import numpy as np
from sklearn.metrics import precision_recall_curve

best = fn("best_threshold")
rng = np.random.default_rng(1)
y_true = rng.integers(0, 2, 300)
scores = np.clip(y_true * 0.3 + rng.uniform(0, 0.7, 300), 0, 1)


def reference(y_true, scores, min_recall):
    p, r, t = precision_recall_curve(y_true, scores)
    p, r = p[:-1], r[:-1]
    ok = np.where(r >= min_recall)[0]
    i = ok[np.argmax(p[ok])]
    return t[i], p[i], r[i]


result = best(y_true, scores, 0.8)
check("best_threshold returns (threshold, precision, recall)", lambda: len(result) == 3)
check("the chosen recall is at least min_recall", lambda: result[2] >= 0.8)
check("it picks the highest precision that still meets the recall target",
      lambda: approx(result[1], reference(y_true, scores, 0.8)[1]),
      "Filter with recall >= min_recall, then take the argmax of precision among those.")
check("it returns the matching threshold", lambda: approx(result[0], reference(y_true, scores, 0.8)[0]))
check("it works for another target (recall >= 0.95)",
      lambda: approx(best(y_true, scores, 0.95)[1], reference(y_true, scores, 0.95)[1]))
