from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression

evaluate = fn("evaluate")
keys = {"accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"}
dummy = evaluate(DummyClassifier(strategy="most_frequent"))
check("evaluate returns a dict with all six metrics", lambda: set(dummy) == keys,
      "Keys: accuracy, precision, recall, f1, roc_auc, pr_auc.")
check("dummy: accuracy looks great (> 0.99)", lambda: dummy["accuracy"] > 0.99)
check("dummy: recall and F1 are 0", lambda: dummy["recall"] == 0 and dummy["f1"] == 0)
check("dummy: ROC-AUC is 0.5 (no ranking at all)", lambda: abs(dummy["roc_auc"] - 0.5) < 1e-9)
check("dummy: PR-AUC equals the positive rate (tiny)", lambda: dummy["pr_auc"] < 0.02,
      "Use average_precision_score(y_test, scores).")
logreg = evaluate(LogisticRegression(max_iter=1000))
check("logistic regression catches some positives", lambda: logreg["recall"] > 0 and logreg["pr_auc"] > dummy["pr_auc"])
answer = {str(k).lower() for k in var("EXPOSES_DUMMY")}
check("EXPOSES_DUMMY names recall, f1 and pr_auc", lambda: {"recall", "f1", "pr_auc"} <= answer,
      "Which metrics were 0 or near the positive rate for the dummy?")
check("EXPOSES_DUMMY does not include accuracy", lambda: filled(answer) and "accuracy" not in answer)
