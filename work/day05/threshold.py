# Choose a decision threshold from the precision-recall curve instead of using 0.5.
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import PrecisionRecallDisplay, precision_recall_curve
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=20000, weights=[0.995], flip_y=0, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
scores = model.predict_proba(X_test)[:, 1]


def best_threshold(y_true, scores, min_recall=0.8):
    """Return (threshold, precision, recall) with the HIGHEST precision among the
    thresholds whose recall >= min_recall.
    precision_recall_curve returns one more precision/recall value than thresholds:
    drop the last one (precision[:-1], recall[:-1]) so the arrays line up."""
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    precision, recall = precision[:-1], recall[:-1]
    # TODO: keep only indexes where recall >= min_recall, pick the one with max precision
    valid_idx = np.where(recall >= min_recall)[0]
    best_idx = valid_idx[np.argmax(precision[valid_idx])]
    
    return thresholds[best_idx], precision[best_idx], recall[best_idx]


if __name__ == "__main__":
    t, p, r = best_threshold(y_test, scores)
    print(f"threshold={t:.3f}  precision={p:.3f}  recall={r:.3f}")
    print("at the default 0.5:", "recall =", round(((scores >= 0.5) & (y_test == 1)).sum() / y_test.sum(), 3))

    PrecisionRecallDisplay.from_predictions(y_test, scores)
    # TODO: mark your chosen point on the curve: plt.scatter([r], [p], color="red", zorder=3)
    plt.scatter([r], [p], color="red", zorder=3, label=f"Selected (t={t:.3f})")
    plt.legend()
    plt.show()
