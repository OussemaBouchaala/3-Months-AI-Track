# Target leakage: a feature that is only known because of the label.
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

rng = np.random.default_rng(0)
n = 2000
X_honest = rng.normal(size=(n, 5))
y = (X_honest[:, 0] + rng.normal(0, 2, n) > 0).astype(int)   # a weak real signal

# 1. A leaky feature computed FROM the label: y plus small noise (rng.normal(0, 0.1, n)).
leak = ...  # TODO
X_leaky = np.column_stack([X_honest, leak])


def cv_score(X, y):
    """Mean 5-fold cross-validated accuracy of LogisticRegression(max_iter=1000)."""
    # TODO
    ...


if __name__ == "__main__":
    print("honest:", round(cv_score(X_honest, y), 3))
    print("leaky: ", round(cv_score(X_leaky, y), 3))

# 3. One real example of target leakage from your own work (what leaked, and why it wasn't available at prediction time):
MY_EXAMPLE = ""
