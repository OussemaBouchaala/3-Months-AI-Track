# 0.5% positives: which metrics expose a model that never predicts the positive class?
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=20000, weights=[0.995], flip_y=0, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)


def evaluate(model):
    """Fit model on the train split and return a dict with these keys, computed on the test split:
       accuracy, precision, recall, f1     -> from y_pred = model.predict(X_test)
       roc_auc, pr_auc                     -> from scores = model.predict_proba(X_test)[:, 1]
                                              (pr_auc = average_precision_score)
    Pass zero_division=0 to precision_score and f1_score."""
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    scores = model.predict_proba(X_test)[:, 1]
    # TODO: return the dict
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, scores),
        "pr_auc": average_precision_score(y_test, scores)
    }


if __name__ == "__main__":
    for name, model in [("dummy", DummyClassifier(strategy="most_frequent")),
                        ("logreg", LogisticRegression(max_iter=1000))]:
        metrics = evaluate(model)
        print(f"{name:<7}", "  ".join(f"{k}={v:.3f}" for k, v in metrics.items()))

# After running: list the metric names (dict keys) that reveal the dummy model is useless.
EXPOSES_DUMMY = ["precision","f1" , "pr_auc", "recall"]
