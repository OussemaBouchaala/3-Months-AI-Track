# Preprocessing leakage: fit on everything (wrong) vs fit inside each fold (Pipeline).
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)

rng = np.random.default_rng(0)
X_noise = rng.normal(size=(100, 5000))   # pure noise: nothing to learn
y_noise = rng.integers(0, 2, 100)


def leaky_scaler_score(X, y):
    """WRONG on purpose: X_scaled = StandardScaler().fit_transform(X) on ALL rows,
    then return cross_val_score(KNeighborsClassifier(), X_scaled, y, cv=5).mean()."""
    # TODO
    ...


def pipeline_scaler_score(X, y):
    """RIGHT: return cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier()), X, y, cv=5).mean()."""
    # TODO
    ...


def leaky_select_score(X, y, k=20):
    """WRONG: SelectKBest(f_classif, k=k).fit_transform(X, y) on ALL rows,
    then cross-validate LogisticRegression(max_iter=1000) on the selected columns (cv=5, mean)."""
    # TODO
    ...


def pipeline_select_score(X, y, k=20):
    """RIGHT: the same selection + model inside make_pipeline, passed to cross_val_score (cv=5, mean)."""
    # TODO
    ...


if __name__ == "__main__":
    print(f"scaler  leaky={leaky_scaler_score(X, y):.3f}  pipeline={pipeline_scaler_score(X, y):.3f}")
    print(f"select  leaky={leaky_select_score(X_noise, y_noise):.3f}  pipeline={pipeline_select_score(X_noise, y_noise):.3f}")

# After running: why is the leakage gap tiny for the scaler but huge for SelectKBest on noise?
WHY_THE_GAPS_DIFFER = ""
