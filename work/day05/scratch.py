import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

y_true = np.array([0] * 995 + [1] * 5)
y_pred = np.zeros(1000, dtype=int)
print("accuracy", accuracy_score(y_true, y_pred))
print("recall", recall_score(y_true, y_pred))
print("f1", f1_score(y_true, y_pred, zero_division=0))
