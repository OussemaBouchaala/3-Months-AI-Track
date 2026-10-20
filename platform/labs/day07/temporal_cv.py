# Why shuffled K-fold lies on time series: compare it with forward-chaining splits.
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, KFold, TimeSeriesSplit, cross_val_score

N = 1500


def make_series(n=N, seed=0):
    """Autocorrelated series: a random walk plus daily seasonality.
    y[t] = cumsum(noise)[t] + 2 * sin(2 * pi * t / 24), with noise ~ Normal(0, 1)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    # TODO
    ...


def lag_features(y, lags=3):
    """Supervised table from a series. For every t >= lags:
    X row = [y[t-1], y[t-2], ..., y[t-lags]], target = y[t].
    Return (X, target) as numpy arrays with len(y) - lags rows."""
    # TODO
    ...


def score(cv, X, target):
    """Mean R^2 of RandomForestRegressor(n_estimators=100, random_state=0) under cross-validator cv."""
    # TODO
    ...


def groups_stay_apart(X, groups, n_splits=4):
    """Bonus: return True if, for every GroupKFold(n_splits) split of X,
    no group id appears in both the train and the test indexes."""
    # TODO (bonus)
    ...


if __name__ == "__main__":
    y = make_series()
    X, target = lag_features(y)
    print("shuffled KFold  R2:", round(score(KFold(5, shuffle=True, random_state=0), X, target), 3))
    print("TimeSeriesSplit R2:", round(score(TimeSeriesSplit(5), X, target), 3))

# After running: explain the gap between the two scores, and link it to your MmCows result.
GAP_EXPLANATION = ""
